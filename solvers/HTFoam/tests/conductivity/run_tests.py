#!/usr/bin/env python3
"""Isolated conductivity/BC verification. Source OF10 in bash; build into RUN/bin and RUN/lib.

No original case, executable or baseline is run, cleaned or overwritten.
Use --mpi for the separate two-rank checks (requires local MPI sockets).
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

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
H1 = ROOT / 'benchmarks/HTFoam/HydrothermalFoam/1d/h1'
FIXTURE = HERE.parent / 'propertyHandling/fixtures/h1-old'
DIM = '[1 1 -3 -1 0 0 0]'


def header(kind, name):
    return f'FoamFile {{ version 2.0; format ascii; class {kind}; object {name}; }}\n'


def field(name, dimensions, values, bottom, top='type fixedValue; value uniform 300;', sides='empty'):
    internal = (f'uniform {values}' if isinstance(values, (float, int)) else
                f'nonuniform List<scalar>\n{len(values)}\n(\n' + '\n'.join(f'{x:.17g}' for x in values) + '\n)')
    return (header('volScalarField', name) + f'dimensions {dimensions};\ninternalField {internal};\n'
            + f'boundaryField {{ bottom {{ {bottom} }} top {{ {top} }} sides {{ type {sides}; }} }}\n')


def mesh_text(nx=1, nz=1):
    # Different centre-to-interface distances: 20 cells below, 40 above.
    return header('dictionary', 'blockMeshDict') + f'''
convertToMeters 1;
vertices ((0 0 0)(1 0 0)(1 0.5 0)(0 0.5 0)(0 0 1)(1 0 1)(1 0.5 1)(0 0.5 1)
          (1 1 0)(0 1 0)(1 1 1)(0 1 1));
blocks (hex (0 1 2 3 4 5 6 7) ({nx} 20 {nz}) simpleGrading (1 1 1)
        hex (3 2 8 9 7 6 10 11) ({nx} 40 {nz}) simpleGrading (1 1 1));
edges ();
boundary
(
 bottom {{type patch; faces ((0 1 5 4));}}
 top {{type patch; faces ((9 11 10 8));}}
 sides {{type {'empty' if nx == nz == 1 else 'wall'};
 faces ((0 3 2 1)(4 5 6 7)(0 4 7 3)(1 2 6 5)
        (3 9 8 2)(7 6 10 11)(3 7 11 9)(2 8 10 6));}}
);
mergePatchPairs ();
'''


def values(path):
    text = path.read_text()
    m = re.search(r'internalField\s+uniform\s+([^;]+);', text)
    if not m:
        m = re.search(r'internalField\s+nonuniform\s+List<(?:scalar|vector)>\s+\d+\s*\((.*?)\)\s*;', text, re.S)
    assert m, path
    return [float(x) for x in m[1].replace('(', ' ').replace(')', ' ').split()]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--mpi', action='store_true')
    parser.add_argument('--cyclic', action='store_true', help='standalone periodic-patch check')
    parser.add_argument('--baseline', type=Path, help='optional full h1 old snapshot for byte comparisons')
    args = parser.parse_args()
    run = args.run.resolve()
    assert HERE in run.parents, 'Use a fresh run-* directory inside tests/conductivity'
    assert not (args.mpi and args.cyclic)
    cases = run / ('cyclic-cases' if args.cyclic else 'mpi-cases' if args.mpi else 'cases')
    cases.mkdir(exist_ok=False)
    env = os.environ.copy()
    env.pop('FOAM_ABORT', None)
    library = run/'lib/libHydrothermalBoundaryConditions.dylib'
    if not library.exists(): library = run/'lib/libHydrothermalBoundaryConditions.so'
    assert library.is_file(), library
    env['FOAM_USER_LIBBIN'] = str(library.parent)
    # macOS can redirect even an absolute dlopen through DYLD_LIBRARY_PATH.
    for key in ('DYLD_LIBRARY_PATH', 'LD_LIBRARY_PATH'):
        env[key] = str(library.parent) + os.pathsep + env.get(key, '')
    solver, probe = run/'bin/HTFoam-review', run/'bin/conductivityProbe'
    results = []

    def record(name, **details):
        results.append(dict(test=name, passed=True, **details))
        (run/('cyclic-results.json' if args.cyclic else 'mpi-results.json' if args.mpi else 'results.json')).write_text(json.dumps(results, indent=2)+'\n')
        print('PASS', name, flush=True)

    def command(argv, case, log, failure=None, timeout=90):
        logfile = case/log
        with logfile.open('w') as out:
            process = subprocess.Popen(list(map(str, argv)), cwd=case, env=env,
                                       stdout=out, stderr=subprocess.STDOUT, start_new_session=True)
            try: code = process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
                raise AssertionError(f'Timeout: {logfile}')
        text = logfile.read_text(errors='replace')
        if failure:
            assert code != 0 and failure in text, (code, failure, logfile, text[-2000:])
        else: assert code == 0, (code, logfile, text[-3000:])
        return text

    def case(name, source='field', layers=(2, 4), shape='', q=20, nx=1, nz=1, exact=False):
        path = cases/name
        path.mkdir()
        for sub in ('0', 'constant', 'system'): shutil.copytree(H1/sub, path/sub)
        # The copied h field is unused and belongs to a differently named mesh.
        (path/'0/h').rename(path/'legacy-h-not-used')
        (path/'system/blockMeshDict').write_text(mesh_text(nx,nz))
        control = header('dictionary','controlDict') + f'''
application HTFoam-review;
startFrom startTime; startTime 0; stopAt endTime; endTime 4; deltaT 1;
writeControl timeStep; writeInterval 1; purgeWrite 0; writeFormat ascii; writePrecision 14;
writeCompression off; timeFormat general; timePrecision 14; runTimeModifiable false;
adjustTimeStep no; libs ("{library}");
'''
        (path/'system/controlDict').write_text(control)
        schemes = (path/'system/fvSchemes').read_text().replace('laplacian(kr,T) Gauss linear corrected;',
                                                                   'default none;\n    laplacian(kr,T) Gauss harmonic corrected;')
        assert 'laplacian(kr_eff,T)' not in schemes
        (path/'system/fvSchemes').write_text(schemes)
        solution = header('dictionary','fvSolution') + '''
solvers { p { solver PCG; preconditioner DIC; tolerance 1e-12; relTol 0; }
          T { solver smoothSolver; smoother symGaussSeidel; tolerance 1e-13; relTol 0; maxIter 20000; }
          pFinal { $p; } TFinal { $T; } }
PIMPLE { nOuterCorrectors 1; nCorrectors 1; nNonOrthogonalCorrectors 0; }
PTCOUPLING { tightCouplingIters 0; }
relaxationFactors { equations { p 1; T 1; } }
'''
        (path/'system/fvSolution').write_text(solution)
        (path/'constant/g').write_text(header('uniformDimensionedVectorField','g')+'dimensions [0 1 -2 0 0 0 0]; value (0 0 0);\n')
        (path/'constant/xThermoProperties').write_text(header('dictionary','xThermoProperties')+'fluid H2O; backend IAPS84;\n')
        (path/'constant/transportProperties').write_text(header('dictionary','transportProperties')+f'''
krSource {source}; kr kr {DIM} 2;
rho_rock rho_rock [1 -3 0 0 0 0 0] 2700;
cp_rock cp_rock [0 2 -2 -1 0 0 0] 880;
porosity porosity [0 0 0 0 0 0 0] 0.1;
''')
        (path/'0/p').write_text(field('p','[1 -1 -2 0 0 0 0]',3e7,'type fixedValue; value uniform 3e7;',
                                     'type fixedValue; value uniform 3e7;', 'empty' if nx==nz==1 else 'zeroGradient'))
        (path/'0/permeability').write_text(field('permeability','[0 2 0 0 0 0 0]',1e-15,
                    'type zeroGradient;', 'type zeroGradient;', 'empty' if nx==nz==1 else 'zeroGradient'))
        bottom = f'type hydrothermalHeatFlux; conductivityField kr_eff; q uniform {q}; value uniform 0; {shape}'
        temperatures = 300
        if exact:
            assert nx==nz==1
            coordinates=[(i+0.5)*0.5/20 for i in range(20)]+[0.5+(i+0.5)*0.5/40 for i in range(40)]
            temperatures=[300+q*((1-y)/layers[1] if y>=0.5 else 0.5/layers[1]+(0.5-y)/layers[0]) for y in coordinates]
        (path/'0/T').write_text(field('T','[0 0 0 1 0 0 0]',temperatures,bottom,
                                     sides='empty' if nx==nz==1 else 'zeroGradient'))
        if source=='field':
            (path/'0/kr').write_text(field('kr',DIM,[layers[0]]*(nx*20*nz)+[layers[1]]*(nx*40*nz),
                                    'type zeroGradient;','type zeroGradient;', 'empty' if nx==nz==1 else 'zeroGradient'))
        command(['blockMesh'],path,'log.blockMesh')
        return path

    def patches(path, name='initial'):
        return [dict(patch=s[0], face=int(s[1]), xyz=tuple(map(float,s[2:5])),
                     k=float(s[5]), grad=float(s[6]), T=float(s[7]), area=float(s[8]))
                for s in (line.split() for line in (path/f'patch-{name}.txt').read_text().splitlines())]

    def analytical(path, layers, q=20):
        rows=[[float(x) for x in line.split()] for line in (path/'cells.txt').read_text().splitlines()]
        error=max(abs(T-(300+q*((1-y)/layers[1] if y>=0.5 else 0.5/layers[1]+(0.5-y)/layers[0]))) for y,T,k in rows)
        data=patches(path,'solved')
        power={patch:sum(r['k']*r['grad']*r['area'] for r in data if r['patch']==patch) for patch in ('bottom','top')}
        flux=[abs(float(line.split()[1])) for line in (path/'face-flux.txt').read_text().splitlines()]
        assert error < 1e-7,(error,layers)
        assert abs(power['bottom']-q)<1e-7 and abs(power['top']+q)<1e-7,power
        assert max(abs(x-abs(q)) for x in flux)<1e-7,flux
        return dict(max_temperature_error_K=error, inward_power_W=power, max_internal_flux_error_W=max(abs(x-abs(q)) for x in flux))

    if args.cyclic:
        path=case('cyclic')
        f=path/'constant/polyMesh/boundary'; text=f.read_text()
        for patch,other in (('bottom','top'),('top','bottom')):
            text=re.sub(rf'({patch}\s*\{{\s*)type\s+patch\s*;',rf'\g<1>type cyclic; neighbourPatch {other};',text)
        f.write_text(text)
        (path/'0/kr').write_text(field('kr',DIM,[2]*20+[4]*40,'type cyclic;','type cyclic;'))
        (path/'0/T').write_text(field('T','[0 0 0 1 0 0 0]',300,'type cyclic;','type cyclic;'))
        command([probe],path,'log.probe')
        data=patches(path)
        assert all(abs(r['k']-10/3)<1e-12 and abs(r['grad'])<1e-12 for r in data),data
        record('cyclic conductivity uses standard coupled interpolation')
        return

    if args.mpi:
        path=case('layered',exact=True)
        (path/'system/decomposeParDict').write_text(header('dictionary','decomposeParDict')+'''
numberOfSubdomains 2; method manual; manualCoeffs { dataFile "cellDecomposition"; }
''')
        # Put the 2/4 W/(m K) discontinuity exactly on the processor interface.
        (path/'constant/cellDecomposition').write_text(header('labelList','cellDecomposition')+
                    '60\n(\n'+'\n'.join(['0']*20+['1']*40)+'\n)\n')
        command([solver],path,'log.serial')
        expected={f:values(path/'4'/f) for f in ('p','T','U','rho','mu','phi','kr','kr_eff')}
        command(['decomposePar','-time','0'],path,'log.decompose')
        command(['mpirun','-np','2',solver,'-parallel'],path,'log.parallel')
        # reconstruct only fresh parallel results; preserve the serial reference.
        (path/'4').rename(path/'4-serial')
        command(['reconstructPar','-time','4'],path,'log.reconstruct')
        errors={}
        for f,old in expected.items():
            actual=values(path/'4'/f)
            if len(old) in (1,3) and len(actual)>len(old): old*=len(actual)//len(old)
            if len(actual) in (1,3) and len(old)>len(actual): actual*=len(old)//len(actual)
            assert len(actual)==len(old),(f,len(actual),len(old))
            errors[f]=max(abs(a-b) for a,b in zip(actual,old))
            # U/phi are roundoff-sized at hydrostatic equilibrium; use absolute errors.
            assert errors[f] < (1e-5 if f=='p' else 1e-8),(f,errors[f])
        record('HTFoam layered serial/two-rank agreement',max_absolute_errors=errors)
        path=case('rank-local-bad',exact=True)
        (path/'system/decomposeParDict').write_text(header('dictionary','decomposeParDict')+'numberOfSubdomains 2; method simple; simpleCoeffs { n (1 2 1); delta 0.001; }')
        f=path/'0/kr'; f.write_text(field('kr',DIM,[2]*20+[4]*35+[-1]*5,'type zeroGradient;','type zeroGradient;'))
        command(['decomposePar','-time','0'],path,'log.decompose')
        text=command(['mpirun','-np','2',solver,'-parallel'],path,'log.expected-failure',failure='Invalid conductivity',timeout=30)
        assert 'rank=1' in text,text[-2000:]
        record('rank-local invalid conductivity aborts without hanging')
        path=case('nonuniform-flux-mapping',nx=4,nz=3)
        bottom='type hydrothermalHeatFlux; conductivityField kr_eff; q nonuniform List<scalar> 12 ('+' '.join(str(20+i) for i in range(12))+'); value uniform 0;'
        (path/'0/T').write_text(field('T','[0 0 0 1 0 0 0]',300,bottom,sides='zeroGradient'))
        command([probe],path,'log.serial')
        original={r['xyz']:r['k']*r['grad'] for r in patches(path) if r['patch']=='bottom'}
        (path/'system/decomposeParDict').write_text(header('dictionary','decomposeParDict')+'numberOfSubdomains 2; method simple; simpleCoeffs { n (2 1 1); delta 0.001; }')
        command(['decomposePar','-time','0'],path,'log.decompose')
        command(['mpirun','-np','2',probe,'-parallel'],path,'log.parallel')
        actual={r['xyz']:r['k']*r['grad'] for rank in (0,1) for r in patches(path/f'processor{rank}') if r['patch']=='bottom'}
        assert actual.keys()==original.keys()
        assert max(abs(actual[k]-original[k]) for k in actual)<1e-10
        record('nonuniform prescribed heat flux survives decomposition')
        path=case('legacy-invalid-boundary',exact=True)
        f=path/'0/T'; f.write_text(f.read_text().replace('conductivityField kr_eff;', ''))
        (path/'constant/thermophysicalProperties').write_text(header('dictionary','thermophysicalProperties')+
                    f'mixture {{ porousMedia {{ kr kr {DIM} 0; }} }}')
        (path/'system/decomposeParDict').write_text(header('dictionary','decomposeParDict')+
                    'numberOfSubdomains 2; method simple; simpleCoeffs { n (1 2 1); delta 0.001; }')
        command(['decomposePar','-time','0'],path,'log.decompose')
        text=command(['mpirun','-np','2',probe,'-parallel','-legacy'],path,'log.expected-failure',
                     failure='Invalid boundary conductivity',timeout=30)
        assert 'rank=0' in text and 'centre=' in text
        record('rank-local legacy boundary failure reports geometry without hanging')
        return

    for source in ('uniform','field'):
        path=case('uniform-'+source,source=source,layers=(2,2))
        if source=='uniform':
            (path/'0/kr').write_text(field('kr',DIM,-100,'type zeroGradient;','type zeroGradient;'))
        command([probe,'-solve','-cycle'],path,'log.probe')
        metrics=analytical(path,(2,2))
        a=patches(path,'solved'); b=patches(path,'doubled')
        for old,new in zip(a,b):
            assert new['k']==2*old['k']
            if old['patch']=='bottom': assert abs(new['grad']-old['grad']/2)<1e-12
        record('uniform '+source+'; same-timestep refresh',**metrics)
    for layers in ((2,4),(4,2)):
        path=case('layers-'+str(layers[0]),layers=layers)
        command([probe,'-solve'],path,'log.probe')
        record('layered harmonic '+str(layers),**analytical(path,layers))
    # Arithmetic interpolation is deliberately tested as a negative control.
    path=case('arithmetic-control')
    f=path/'system/fvSchemes'; f.write_text(f.read_text().replace('Gauss harmonic corrected','Gauss linear corrected'))
    command([probe,'-solve'],path,'log.probe')
    rows=[[float(x) for x in line.split()] for line in (path/'cells.txt').read_text().splitlines()]
    error=max(abs(T-(300+20*((1-y)/4 if y>=.5 else .125+(.5-y)/2))) for y,T,k in rows)
    assert error>1e-3,error
    record('arithmetic negative control detects interface resistance error',max_temperature_error_K=error)

    for shape in ('fixed','gaussian2d','gaussian3d','linear2d'):
        settings={'fixed':'','gaussian2d':'shape gaussian2d; x0 0.3; c 0.2; qmin 2; qmax 20;',
                  'gaussian3d':'shape gaussian3d; x0 0.3; z0 0.7; c 0.2; qmin 2; qmax 20;',
                  'linear2d':'shape linear2d; x1 0.1; x2 0.9; q1 3; q2 15;'}[shape]
        path=case('patch-'+shape,nx=4,nz=3,shape=settings)
        # Explicit physical conductivities differ from internal values face by face.
        f=path/'0/kr'; f.write_text(f.read_text().replace('bottom { type zeroGradient; }',
                  'bottom { type fixedValue; value nonuniform List<scalar> 12 ('+' '.join(str(3+i) for i in range(12))+'); }'))
        command([probe],path,'log.first')
        first=patches(path)
        for r in first:
            if r['patch']!='bottom': continue
            x,y,z=r['xyz']
            expected=20 if shape=='fixed' else (3+(x-.1)*12/.8 if shape=='linear2d' else
                      2+18*math.exp(-((x-.3)**2+((z-.7)**2 if shape=='gaussian3d' else 0))/(2*.2**2)))
            assert r['k']==3+r['face'],r
            assert abs(r['k']*r['grad']-expected)<1e-10,(shape,r,expected)
        command([probe],path,'log.reload')
        assert max(abs(a['grad']-b['grad']) for a,b in zip(first,patches(path)))<1e-10
        record(shape+' facewise physical conductivity and serialization')

    path=case('legacy')
    f=path/'0/T'; f.write_text(f.read_text().replace('conductivityField kr_eff;',''))
    (path/'constant/thermophysicalProperties').write_text(header('dictionary','thermophysicalProperties')+f'mixture {{ porousMedia {{ kr kr {DIM} 1.5; }} }}')
    command([probe,'-legacy'],path,'log.probe')
    assert abs(next(r for r in patches(path) if r['patch']=='bottom')['grad']-20/1.5)<1e-12
    record('legacy dictionary mode retained despite registered fields')

    for name,edit,message in (
        ('missing-reference',lambda p:(p/'0/kr').rename(p/'reference-not-input'),'cannot find file'),
        ('missing-selected-field',lambda p:(p/'0/T').write_text((p/'0/T').read_text().replace('conductivityField kr_eff','conductivityField absent')),'absent'),
        ('negative-cell',lambda p:(p/'0/kr').write_text(field('kr',DIM,[-1]*60,'type zeroGradient;','type zeroGradient;')),'Invalid conductivity'),
        ('zero-boundary',lambda p:(p/'0/kr').write_text(field('kr',DIM,[2]*60,'type fixedValue; value uniform 0;','type zeroGradient;')),'Invalid conductivity'),
        ('wrong-dimensions',lambda p:(p/'0/kr').write_text((p/'0/kr').read_text().replace(DIM,'[0 0 0 0 0 0 0]')),'has dimensions'),
        ('unknown-source',lambda p:(p/'constant/transportProperties').write_text((p/'constant/transportProperties').read_text().replace('krSource field','krSource typo')),'Unknown krSource'),
    ):
        path=case(name); edit(path)
        command([solver],path,'log.expected-failure',failure=message)
        record(name+' fails fast')

    path=case('invalid-startup-face',q=2e6)
    text=command([solver],path,'log.expected-failure',failure='physical boundary property update')
    assert 'patch=bottom' in text and 'time=0' in text
    assert 'Initialize hydrostatic pressure' not in text
    record('startup computes heat-flux face temperature before EOS validation')

    path=case('nonfinite-reference')
    command([probe,'-nan'],path,'log.expected-failure',failure='Invalid conductivity')
    record('nonfinite reference fails fast')

    # Actual HTFoam startup and restart, not just the isolated diffusion probe.
    path=case('htfoam-layered',exact=True)
    command([solver],path,'log.solver')
    initial=values(path/'0/T'); final=values(path/'4/T')
    assert max(abs(a-b) for a,b in zip(initial,final))<1e-8
    record('HTFoam stationary layered conduction',max_temperature_change_K=max(abs(a-b) for a,b in zip(initial,final)))
    restart=cases/'restart'; shutil.copytree(path,restart)
    f=restart/'system/controlDict'; f.write_text(f.read_text().replace('startTime 0','startTime 2'))
    for t in ('3','4'): (restart/t).rename(restart/(t+'-uninterrupted'))
    (restart/'2/kr_eff').write_text(field('kr_eff',DIM,-100,'type calculated; value uniform -100;', 'type calculated; value uniform -100;'))
    f=restart/'2/T'
    f.write_text(f.read_text().replace('gradient        uniform 10;', 'gradient        uniform 1e9;').replace('value           uniform 307.5;', 'value           uniform 0;'))
    assert 'gradient        uniform 1e9;' in f.read_text() and 'value           uniform 0;' in f.read_text()
    command([solver],restart,'log.restart')
    errors={}
    for f in ('T','p','rho','mu','U','phi','kr','kr_eff'):
        a,b=values(path/'4'/f),values(restart/'4'/f)
        assert len(a)==len(b),(f,len(a),len(b))
        errors[f]=max(abs(x-y) for x,y in zip(a,b))
        assert errors[f]<(1e-5 if f=='p' else 1e-8),(f,errors[f])
    record('nonzero restart rebuilds stale kr_eff',max_absolute_errors=errors)
    missing=cases/'restart-missing-reference'; shutil.copytree(restart,missing)
    (missing/'2/kr').rename(missing/'2/reference-not-input')
    command([solver],missing,'log.expected-failure',failure='cannot find file')
    record('missing restart reference fails rather than using scalar')

    # Existing h1 settings and reference data are unchanged; select isolated library.
    path=cases/'h1'; path.mkdir()
    for sub in ('0','constant','system'): shutil.copytree(H1/sub,path/sub)
    f=path/'system/controlDict'; f.write_text(f.read_text().replace('"libHydrothermalBoundaryConditions.so"',f'"{library}"'))
    command(['blockMesh'],path,'log.blockMesh')
    text=command([solver],path,'log.solver',timeout=120)
    assert text.count('\nTime = ')==9125 and text.rstrip().endswith('End')
    ref=[[float(x) for x in line.split()] for line in (FIXTURE/'cell-properties.txt').read_text().splitlines() if line and not line.startswith('#')]
    errors={}
    for f,columns in (('p',(0,)),('T',(1,)),('U',(2,3,4)),('rho',(5,)),('mu',(6,))):
        expected=[row[c] for row in ref for c in columns]; actual=values(path/'7884000000'/f)
        if len(actual)==len(columns): actual*=len(ref)
        assert len(actual)==len(expected)
        errors[f]=max(abs(a-b) for a,b in zip(actual,expected))/max(max(map(abs,expected)),1e-30)
        assert errors[f]<=5e-6,(f,errors[f])
    expected=[float(line) for line in (FIXTURE/'face-flux.txt').read_text().splitlines() if line and not line.startswith('#')]
    actual=values(path/'7884000000/phi')
    assert len(actual)==len(expected)
    errors['phi']=max(abs(a-b) for a,b in zip(actual,expected))/max(map(abs,expected))
    assert errors['phi']<=5e-6
    sample=Path('postProcessing/linesample/7884000000/data.xy')
    actual_profile=[[float(x) for x in line.split()] for line in (path/sample).read_text().splitlines()
                    if line.strip() and not line.lstrip().startswith('#')]
    reference_profile=[[float(x) for x in line.split()] for line in (FIXTURE/'profile.xy').read_text().splitlines()
                       if line.strip() and not line.lstrip().startswith('#')]
    assert len(actual_profile)==len(reference_profile)
    assert all(len(row)==3 and all(math.isfinite(x) for x in row) for row in actual_profile)
    for column,name in enumerate(('profile_x','profile_T','profile_p')):
        scale=max(max(abs(row[column]) for row in reference_profile),1e-30)
        errors[name]=max(abs(a[column]-b[column]) for a,b in zip(actual_profile,reference_profile))/scale
        assert errors[name]<=(1e-12 if column==0 else 5e-6),(name,errors[name])
    for line in (FIXTURE/'SHA256SUMS').read_text().splitlines():
        digest,name=line.split('  ',1); assert hashlib.sha256((FIXTURE/name).read_bytes()).hexdigest()==digest
    if args.baseline:
        baseline=args.baseline.resolve()
        for f in ('p','T','U','rho','mu','phi'):
            assert (path/'7884000000'/f).read_bytes()==(baseline/'case/7884000000'/f).read_bytes(),f
        assert (path/sample).read_bytes()==(baseline/'case'/sample).read_bytes()
    record('full h1 regression; unchanged profile and optional byte comparison',steps=9125,max_scaled_errors=errors,
           full_baseline_compared=bool(args.baseline))


if __name__=='__main__': main()
