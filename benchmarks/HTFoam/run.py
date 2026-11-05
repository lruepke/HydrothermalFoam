#!/usr/bin/env python3
"""Run a fresh copy of one canonical HTFoam benchmark; never clean source cases."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent
YEAR = 31557600
CASES = ('h1', 'h2', 'h3', 'v1', 'v2', 'v3', '2d', '2d-layered')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def setting(text, key, value):
    text, count = re.subn(r'\b'+key+r'\s+[^;]+;', f'{key} {value};', text, count=1)
    if count != 1:
        raise ValueError(f'Missing controlDict entry: {key}')
    return text


def refine_layered(case, reference):
    """Halve uniform spacing; retain physical material, heater and initial bands."""
    p = case/'system/blockMeshDict'
    text, count = re.subn(r'\(90\s+30\s+1\)', '(180 60 1)', p.read_text())
    if count != 1:
        raise ValueError('Expected the canonical 90 x 30 mesh')
    p.write_text(text)
    def internal(name, values):
        p = case/'0'/name
        text, count = re.subn(r'internalField\s+nonuniform\s+List<scalar>\s+2700\s*\(.*?\)\s*;',
                             'internalField nonuniform List<scalar> 10800 (\\n'+' '.join(values)+'\\n);',
                             p.read_text(), count=1, flags=re.S)
        if count != 1:
            raise ValueError('Expected canonical internal field: '+name)
        p.write_text(text)
    internal('permeability', ['1e-15']*(180*38)+['1e-14']*(180*22))
    internal('T', ['283.15']*(180*58)+['278.15']*(180*2))
    q = ['0' if x<100 or x>8900 else '5' if 4000<x<5000 else '.05'
         for x in range(25,9000,50)]
    p = case/'0/T'
    p.write_text(re.sub(r'q nonuniform List<scalar> 90\s*\([^)]*\)',
                        'q nonuniform List<scalar> 180 ('+' '.join(q)+')', p.read_text()))
    reference = reference.replace('90     1     30', '180     1     60')
    reference = re.sub(r'\nTOP\n.*?(?=# UNCONFINED)',
                       '\nTOP\n180*-1001\n'+'180*1\n'*21+'180*2\n'*38, reference, flags=re.S)
    reference = re.sub(r'XSPACING \(m\)\nFREE_FORMAT\n.*?(?=YSPACING)',
                       'XSPACING (m)\nCONSTANT\n50.0\n', reference, flags=re.S)
    reference = reference.replace('ZSPACING (m)\nCONSTANT\n100.0', 'ZSPACING (m)\nCONSTANT\n50.0')
    reference = reference.replace('304.974620148809', '302.4873100744045')
    reference = re.sub(r'(CONDUCTIVE Heat Input along Base \(W/m\^2\)\nFREE_FORMAT\n).*?(?=# End of Keyword)',
                       lambda m:m[1]+' '.join(q)+'\n', reference, flags=re.S)
    # Same 100 m initially cold band on both grids; only the top row has IBC=10.
    reference = reference.replace('TEMPERATURE (C)\nCONSTANT\n10.0',
        'TEMPERATURE (C)\nFREE_FORMAT\nBOTTOM\n'+' '.join(['10']*(180*58)+['5']*(180*2)))
    for name, value in [('PRESSURE', '302.4873100744045'), ('TEMPERATURE', '5.0')]:
        reference = re.sub(r'(?m)(^'+name+r' \([^\n]+\)\nNODE\n).*?^\s*0\s+0\s+0\s+0\s*$',
            lambda m:m[1]+''.join(f'     {i}     1     60     {value}\n' for i in range(1,181))+'     0     0     0     0',
            reference, flags=re.S)
    return reference


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', choices=CASES, required=True)
    parser.add_argument('--output', type=Path, required=True, help='new run directory, normally work/CASE')
    parser.add_argument('--solver', default=os.environ.get('HTFOAM_SOLVER', 'HTFoam-review'))
    parser.add_argument('--library', type=Path, default=os.environ.get('HTFOAM_LIBRARY'))
    parser.add_argument('--prepare-only', action='store_true', help='copy inputs without mesh generation or simulation')
    parser.add_argument('--resume', action='store_true', help='continue only a run created by this driver')
    parser.add_argument('--until-year', type=int, choices=(5000, 15000, 50000), help='2D: stop at an accepted checkpoint')
    parser.add_argument('--refine', action='store_true', help='2d-layered only: 180 x 60 instead of 90 x 30')
    args = parser.parse_args()
    if args.until_year is not None and args.case not in ('2d', '2d-layered'):
        parser.error('--until-year is only supported for the staged 2D benchmark')
    if args.refine and args.case != '2d-layered':
        parser.error('--refine applies only to 2d-layered')
    source = ROOT/'HydrothermalFoam'/(args.case if args.case in ('2d', '2d-layered') else '1d/'+args.case)
    out = args.output.expanduser().resolve()
    if out == ROOT or (ROOT in out.parents and ROOT/'work' not in out.parents):
        parser.error('Place runs under benchmarks/HTFoam/work/ or outside the benchmark source tree')
    template = (source/'system/controlDict').read_text()
    end = int(float(re.search(r'\bendTime\s+([^;]+);', template)[1]))
    if args.case == 'v2':
        end = 350*YEAR
        phases = [end//864000*864000, end]  # unchanged 10-day steps plus final 7.5 days
    elif args.case == '2d-layered':
        if args.until_year not in (None, 5000):
            parser.error('2d-layered stops at the verified 5 kyr checkpoint')
        end = 5000*YEAR
        phases = [end]
    elif args.case == '2d':
        end = 50000*YEAR
        phases = [5000*YEAR, 15000*YEAR, end]
    else:
        phases = [end]
    requested = args.until_year*YEAR if args.until_year else end
    phases = [t for t in phases if t <= requested]
    inputs = {str(p.relative_to(source)): digest(p) for sub in ('0', 'constant', 'system')
              for p in (source/sub).iterdir() if p.is_file()}
    reference = ROOT/'USGS_HYDROTHERMAL/2d/layered/layered.input'
    reference_text = reference.read_text() if args.case == '2d-layered' else None
    # Validate runtime dependencies before creating or changing any run output.
    # Preparation alone still works without a built solver or boundary library.
    solver = shutil.which(args.solver) if args.solver else None
    if solver is None and args.solver and Path(args.solver).is_file():
        solver = str(Path(args.solver).resolve())
    library = args.library.expanduser().resolve() if args.library else None
    if not args.prepare_only and (not solver or not library or not library.is_file()):
        parser.error('Provide a built --solver and matching --library, or HTFOAM_SOLVER/HTFOAM_LIBRARY')
    if args.resume:
        meta = json.loads((out/'run.json').read_text())
        if meta.get('format') != 'HTFoam-benchmark-1' or meta['case'] != args.case or meta['inputs'] != inputs:
            parser.error('Resume requires the same driver, case and canonical input hashes')
        if args.case == '2d-layered' and (
            meta.get('refine') != args.refine
            or meta.get('reference_source_sha256') != digest(reference)
            or digest(out/'reference.input') != meta.get('reference_sha256')
        ):
            parser.error('Resume cannot switch grid or HYDROTHERM inputs')
    else:
        out.mkdir(parents=True, exist_ok=False)
        (out/'case').mkdir()
        for sub in ('0', 'constant', 'system'):
            shutil.copytree(source/sub, out/'case'/sub)
        meta = dict(format='HTFoam-benchmark-1', case=args.case, inputs=inputs,
                    full_end_seconds=end, completed_phases=[])
        if args.case == '2d-layered':
            if args.refine:
                reference_text = refine_layered(out/'case', reference_text)
            (out/'reference.input').write_text(reference_text)
            meta.update(refine=args.refine, reference_source_sha256=digest(reference),
                        reference_sha256=digest(out/'reference.input'))
    for filename, path in [('solver', Path(solver) if solver else None), ('library', library)]:
        if path and path.is_file():
            checksum = digest(path)
            if filename in meta and meta[filename]['sha256'] != checksum:
                parser.error(f'Resume cannot switch the {filename}')
            target = out/('bin/HTFoam-review' if filename == 'solver' else 'lib/'+path.name)
            target.parent.mkdir(exist_ok=True)
            if not target.exists():
                shutil.copy2(path, target)
            if digest(target) != checksum:
                parser.error(f'Copied {filename} does not match')
            meta[filename] = dict(path=str(target), sha256=checksum)
    private = meta.get('library', {}).get('path')
    if private:
        template = re.sub(r'"[^"\n]*libHydrothermalBoundaryConditions\.(so|dylib)"',
                          lambda _: '"'+private+'"', template)
    case = out/'case'
    def control(target, restart):
        text = setting(template, 'endTime', target)
        text = setting(text, 'startFrom', 'latestTime' if restart else 'startTime')
        if args.case == 'v2':
            text = setting(text, 'deltaT', 648000 if restart else 864000)
            text = setting(text, 'writeInterval', 1 if restart else target)
            if restart:
                text = setting(text, 'writeControl', 'timeStep')
        return text
    def save():
        (out/'run.json').write_text(json.dumps(meta, indent=2)+'\n')
    pending = [t for t in phases if t not in meta['completed_phases']]
    if pending:
        (case/'system/controlDict').write_text(control(pending[0], bool(meta['completed_phases'])))
    save()
    if args.prepare_only:
        print(f'Prepared {args.case}: {case}; full duration {end} s. No solver run.')
        return
    env = os.environ.copy()
    for key in ('DYLD_LIBRARY_PATH', 'LD_LIBRARY_PATH'):
        env[key] = str(out/'lib')+os.pathsep+env.get(key, '')
    def command(argv, name):
        log = out/name
        if log.exists():
            parser.error(f'Refusing to overwrite {log}; inspect the previous attempt')
        with log.open('w') as stream:
            subprocess.run(list(map(str, argv)), cwd=case, env=env, stdout=stream,
                           stderr=subprocess.STDOUT, check=True)
    if not (case/'constant/polyMesh/points').exists():
        command(['blockMesh'], 'log.mesh')
    for target in pending:
        (case/'system/controlDict').write_text(control(target, bool(meta['completed_phases'])))
        command([out/'bin/HTFoam-review'], f'log.{target}')
        if not (case/str(target)/'T').is_file() or not (case/str(target)/'p').is_file():
            raise RuntimeError(f'Missing expected p/T fields at {target} s')
        meta['completed_phases'].append(target)
        save()
        print(f'{args.case}: completed {target} s; results in {case}', flush=True)
    for name, checksum in inputs.items():
        if digest(source/name) != checksum:
            raise RuntimeError('Canonical source inputs changed during the run')


if __name__ == '__main__':
    main()
