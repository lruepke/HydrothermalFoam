#!/usr/bin/env python3
"""Isolated property-handling checks; never run or clean a preserved baseline.

Run after building HTFoam-review and probe into RUN/bin and sourcing OF10 in bash.
Use --mpi separately for communication and rank-local fatal-error checks.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
INPUTS = ROOT / 'benchmarks/HTFoam/HydrothermalFoam/1d/h1'
FIXTURE = HERE / 'fixtures/h1-old'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--mpi', action='store_true')
    parser.add_argument('--baseline', type=Path,
                        help='optional full old baseline with case/ and SHA256SUMS; adds byte comparisons')
    parser.add_argument('--preserve', type=Path, action='append', default=[],
                        help='optional existing file/directory to hash before/after the run (repeatable)')
    args = parser.parse_args()
    run = args.run.resolve()
    baseline = args.baseline.resolve() if args.baseline else None
    protected = [p.resolve() for p in args.preserve]
    if baseline:
        if not (baseline/'SHA256SUMS').is_file() or not (baseline/'case').is_dir():
            parser.error('--baseline must contain case/ and SHA256SUMS')
        protected.append(baseline)
    for path in protected:
        if not path.exists(): parser.error(f'preservation target does not exist: {path}')
    for path in [INPUTS, FIXTURE, *protected]:
        if run == path or path in run.parents:
            parser.error(f'run directory must be outside protected inputs/artifacts: {path}')
    cases = run / ('mpi-cases' if args.mpi else 'cases')
    cases.mkdir(exist_ok=False)
    manifest = run / ('mpi-preserved-sha256.json' if args.mpi else 'preserved-sha256.json')
    paths = [p for target in protected
             for p in (target.rglob('*') if target.is_dir() else [target]) if p.is_file()]
    manifest.write_text(json.dumps({str(p.resolve()): hashlib.sha256(p.read_bytes()).hexdigest()
                                    for p in paths}, indent=2) + '\n')

    def verify_checksums(folder):
        for line in (folder/'SHA256SUMS').read_text().splitlines():
            digest,name=line.split('  ',1)
            assert hashlib.sha256((folder/name).read_bytes()).hexdigest()==digest,name

    def verify_preserved():
        for name,digest in json.loads(manifest.read_text()).items():
            assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==digest,name
        verify_checksums(FIXTURE)
        if baseline: verify_checksums(baseline)

    verify_preserved()
    results = []
    summary = run / ('mpi-results.json' if args.mpi else 'results.json')
    solver = run / 'bin/HTFoam-review'
    probe = run / 'bin/propertyProbe'
    env = os.environ.copy()
    # Test failures use OpenFOAM's normal MPI abort, not an OS core-dump override.
    env.pop('FOAM_ABORT', None)

    def command(argv, case, log, failure=None, timeout=90):
        path = case / log
        with path.open('w') as output:
            process = subprocess.Popen([str(x) for x in argv], cwd=case, env=env,
                                       stdout=output, stderr=subprocess.STDOUT,
                                       start_new_session=True)
            try:
                code = process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
                raise AssertionError(f'timeout: {argv}; see {path}')
        text = path.read_text(errors='replace')
        if failure:
            assert code != 0, f'expected failure: {path}'
            assert failure in text, f'expected {failure!r}: {path}\n{text[-3000:]}'
        else:
            assert code == 0, f'exit {code}: {path}\n{text[-3000:]}'
        return text

    def record(name, **details):
        results.append(dict(test=name, passed=True, **details))
        summary.write_text(json.dumps(results, indent=2) + '\n')
        print('PASS', name, flush=True)

    def case(name, T=573.15, p=3e7, X=0.1, backend='IAPS84', fluid='H2O-NaCl'):
        path = cases / name
        path.mkdir()
        for sub in ('0', 'constant', 'system'):
            shutil.copytree(INPUTS / sub, path / sub)
        for field, value in (('p', p), ('T', T)):
            f = path / '0' / field
            text = re.sub(r'(uniform\s+)[^;]+;', lambda m: m[1] + str(value) + ';', f.read_text())
            f.write_text(text)
        (path / 'constant/xThermoProperties').write_text(
            f'FoamFile {{ version 2.0; format ascii; class dictionary; object xThermoProperties; }}\n'
            f'fluid {fluid};\nbackend {backend};\n{fluid} {{ constX {X}; }}\n')
        f = path / 'system/blockMeshDict'
        f.write_text(f.read_text().replace('(200 1 1)', '(40 1 1)'))
        f = path / 'system/controlDict'
        text = f.read_text()
        for key, value in (('deltaT', '1'), ('endTime', '2'), ('writeInterval', '1'), ('writePrecision', '14')):
            text = re.sub(rf'\b{key}\s+[^;]+;', f'{key} {value};', text)
        f.write_text(text)
        command(['blockMesh'], path, 'log.blockMesh')
        return path

    def values(path):
        text = path.read_text()
        match = re.search(r'internalField\s+uniform\s+([^;]+);', text)
        if match:
            return [float(x) for x in match[1].replace('(', ' ').replace(')', ' ').split()]
        match = re.search(r'internalField\s+nonuniform\s+List<(?:scalar|vector)>\s+\d+\s*\((.*?)\)\s*;', text, re.S)
        assert match, path
        return [float(x) for x in match[1].replace('(', ' ').replace(')', ' ').split()]

    if args.mpi:
        for bad in (False, True):
            path = case('rank-local-failure' if bad else 'nonuniform-valid')
            f = path / '0/T'
            temperatures = [573.15 + i for i in range(40)]
            if bad:
                temperatures[30] = 1500  # only the right subdomain has an invalid internal state
            text = re.sub(r'internalField\s+uniform\s+[^;]+;',
                          'internalField nonuniform List<scalar>\n40\n(\n' +
                          '\n'.join(map(str, temperatures)) + '\n);', f.read_text())
            f.write_text(text)
            (path / 'system/decomposeParDict').write_text('''FoamFile { version 2.0; format ascii; class dictionary; object decomposeParDict; }
numberOfSubdomains 2;
method simple;
simpleCoeffs { n (2 1 1); delta 0.001; }
''')
            if not bad:
                pressure = path / '0/p'
                text = pressure.read_text()
                text = re.sub(r'internalField\s+uniform\s+[^;]+;', 'internalField uniform 3.05e7;', text)
                text = re.sub(r'(left\s*\{.*?value\s+uniform\s+)[^;]+;', r'\g<1>3.1e7;', text, count=1, flags=re.S)
                pressure.write_text(text)
            command(['decomposePar'], path, 'log.decomposePar')
            if bad:
                text = command(['mpirun', '-np', '2', solver, '-parallel'], path, 'log.parallel',
                               failure='outside advertised model bounds', timeout=30)
                assert 'rank=1' in text and 'local cell=' in text and 'centre=' in text
                record('rank-local failure aborts MPI without hanging')
            else:
                command([solver], path, 'log.serial')
                expected = {field: values(path / '2' / field) for field in ('p','T','rho','mu','U','phi')}
                # Remove only this disposable serial result so reconstructPar writes fresh fields.
                shutil.rmtree(path / '2')
                command(['mpirun', '-np', '2', solver, '-parallel'], path, 'log.parallel')
                command(['reconstructPar', '-time', '2'], path, 'log.reconstructPar')
                errors = {}
                for field, original in expected.items():
                    actual = values(path / '2' / field)
                    if len(original) in (1,3) and len(actual) > len(original): original *= len(actual)//len(original)
                    if len(actual) in (1,3) and len(original) > len(actual): actual *= len(original)//len(actual)
                    assert len(actual) == len(original)
                    scale = max(max(map(abs, actual)), max(map(abs, original)), 1e-30)
                    errors[field] = max(abs(a-b) for a,b in zip(actual,original)) / scale
                    assert errors[field] < (1e-6 if field in ('U','phi') else 1e-9), (field, errors[field])
                record('nonuniform two-rank vs serial', max_relative_errors=errors)
        verify_preserved()
        return

    valid = case('hot-brine-IAPS84')
    for backend in ('IAPS84', 'IAPWS95'):
        path = valid if backend == 'IAPS84' else case('hot-brine-IAPWS95', backend=backend)
        command([solver], path, 'log.solver')
        text = command([probe, '-backend', backend], path, 'log.reference')
        density = float(re.search(r'PROBE phase=\S+ rho=(\S+)', text)[1])
        for rho in values(path / '2/rho'):
            assert abs(rho-density) / density < 1e-12
        if backend == 'IAPS84': assert abs(density-849.034) < 0.001
        record('valid nonzero-salinity startup '+backend, rho=density)

    for name, options, expected in (
        ('negative-pressure', dict(p=-1), 'invalid input'),
        ('invalid-composition', dict(X=1.1), 'configuration failure'),
        ('out-of-range', dict(T=1500), 'outside advertised model bounds'),
        ('unavailable-viscosity', dict(T=473.15,p=4e8,X=0,fluid='H2O'), 'unusable property mu='),
        ('multiphase', dict(T=673.15,p=1e7,X=0.1), 'unsupported phase'),
        ('bad-backend', dict(backend='invalidBackend'), 'model construction exception'),
        ('cold-brine-domain', dict(T=278.15,backend='IAPWS95'), 'xThermo status='),
        ('negative-compressibility-domain', dict(T=323.15,p=1e5,X=0.26), 'unusable property betaT='),
    ):
        path = case(name, **options)
        text = command([solver], path, 'log.expected-failure', failure=expected)
        if 'configuration' not in text:
            assert all(x in text for x in ('T=', 'p=', 'X=', 'time=', 'rank=', 'centre='))
        record(name+' fails with context')

    path = case('invalid-boundary')
    f = path / '0/T'
    f.write_text(re.sub(r'(left\s*\{.*?value\s+uniform\s+)[^;]+;', r'\g<1>1500;', f.read_text(), count=1, flags=re.S))
    text = command([solver], path, 'log.expected-failure', failure='physical boundary property update')
    assert 'patch=left' in text and 'local face=0' in text
    record('physical-boundary failure reports face')

    for mode, failure in (
        ('nanInput','invalid input'), ('status','xThermo status=OutOfRange'), ('exception','exception during EOS evaluation'),
        ('nanMu','unusable property mu='), ('zeroCp','unusable property Cp='),
        ('negativeBeta','unusable property betaT='), ('nanAlpha','unusable property alphaP='),
        ('critical','unsupported phase'), ('solid','unsupported phase'), ('unknown','unsupported phase'),
        ('negativeAlpha',None), ('zeroAlpha',None), ('superV',None), ('superL',None),
    ):
        command([probe,'-mode',mode,'-salinity','0'], valid, 'log.probe-'+mode, failure=failure)
        record('validator '+mode)
    for name, T, p in (('real-vapour',573.15,1e5),('real-supercritical',773.15,3e7),('real-negative-alpha',274.15,1e6)):
        text = command([probe,'-mode','water','-temperature',T,'-pressure',p,'-salinity','0'], valid, 'log.'+name)
        if name == 'real-negative-alpha': assert float(re.search(r'alpha=(\S+)',text)[1]) < 0
        record(name)

    # A periodic constraint patch exercises the non-processor coupled path.
    path = case('cyclic-brine')
    for sub in ('0','constant/polyMesh'):
        if sub == 'constant/polyMesh':
            f = path / sub / 'boundary'
            text=f.read_text()
            for patch,other in (('left','right'),('right','left')):
                text=re.sub(rf'({patch}\s*\{{\s*)type\s+patch\s*;',rf'\g<1>type cyclic; neighbourPatch {other};',text)
            f.write_text(text)
        else:
            for name in ('p','T','permeability'):
                f=path/sub/name; text=f.read_text()
                for patch in ('left','right'):
                    text=re.sub(rf'{patch}\s*\{{[^{{}}]*\}}',patch+' { type cyclic; }',text)
                f.write_text(text)
    # Skip the singular steady all-Neumann initializer; transient p has storage.
    (path/'0').rename(path/'1')
    f=path/'system/controlDict'; text=f.read_text().replace('startTime 0;','startTime 1;').replace('endTime 2;','endTime 3;'); f.write_text(text)
    command([solver],path,'log.solver')
    record('cyclic property communication')

    # Preserve original h1 settings, precision, and full 250-year duration.
    path=cases/'h1-regression'; path.mkdir()
    for sub in ('0','constant','system'): shutil.copytree(INPUTS/sub,path/sub)
    command(['blockMesh'],path,'log.blockMesh')
    text=command([solver],path,'log.solver',timeout=120)
    assert text.rstrip().endswith('End')
    assert text.count('\nTime = ')==9125
    rel=Path('postProcessing/linesample/7884000000/data.xy')
    def table(file):
        rows = [[float(x) for x in line.split()] for line in file.read_text().splitlines()
                if line.strip() and not line.lstrip().startswith('#')]
        assert rows and all(math.isfinite(x) for row in rows for x in row),file
        return rows

    def compare(actual, expected, tolerance, label):
        assert len(actual)==len(expected),label
        assert all(math.isfinite(x) for x in actual),label
        scale=max(max(map(abs,expected)),1e-30)
        error=max(abs(a-b) for a,b in zip(actual,expected))/scale
        assert error <= tolerance,(label,error,tolerance)
        return error

    reference=table(FIXTURE/'cell-properties.txt')
    errors={}
    for field,columns in (('p',(0,)),('T',(1,)),('U',(2,3,4)),('rho',(5,)),('mu',(6,))):
        expected=[row[column] for row in reference for column in columns]
        actual=values(path/'7884000000'/field)
        if len(actual)==len(columns): actual *= len(reference)
        errors[field]=compare(actual,expected,5e-6,field)
    errors['phi']=compare(values(path/'7884000000/phi'),
                          [row[0] for row in table(FIXTURE/'face-flux.txt')],5e-6,'phi')
    actual_profile=table(path/rel)
    reference_profile=table(FIXTURE/'profile.xy')
    for column,name in enumerate(('profile_x','profile_T','profile_p')):
        errors[name]=compare([row[column] for row in actual_profile],
                             [row[column] for row in reference_profile],
                             1e-12 if column==0 else 5e-6,name)
    record('h1 full regression vs tracked numerical fixture',steps=9125,
           max_scaled_errors=errors)
    if baseline:
        assert (path/rel).read_bytes()==(baseline/'case'/rel).read_bytes()
        for field in ('p','T','U','rho','mu','phi'):
            assert (path/'7884000000'/field).read_bytes()==(baseline/'case/7884000000'/field).read_bytes()
        record('optional h1 full-baseline byte comparison')

    verify_preserved()
    record('tracked fixture and requested preservation targets verified')


if __name__ == '__main__':
    main()
