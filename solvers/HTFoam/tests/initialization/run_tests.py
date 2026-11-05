#!/usr/bin/env python3
"""Isolated initialization checks. Requires OF10 environment and isolated solver/library."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('conductivity', HERE.parent/'conductivity/run_tests.py')
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)
a = argparse.ArgumentParser(description=__doc__)
a.add_argument('--build', type=Path, required=True)
a.add_argument('--run', type=Path, required=True)
a.add_argument('--old-solver', type=Path)
a = a.parse_args()
build, run = a.build.resolve(), a.run.resolve()
assert run.parent == HERE and run.name.startswith('run-')
run.mkdir(exist_ok=False)
solver = build/'bin/HTFoam-review'
lib = build/'lib/libHydrothermalBoundaryConditions.dylib'
if not lib.exists(): lib = lib.with_suffix('.so')
env = os.environ.copy()
# Foundation 10 has no -debug-switch option: use its process-local debug dictionary.
env['FOAM_CONTROLDICT'] = (Path(env['WM_PROJECT_DIR'])/'etc/controlDict').read_text() + '\nDebugSwitches { solution 1; }\n'
for key in ('DYLD_LIBRARY_PATH', 'LD_LIBRARY_PATH'):
    env[key] = str(lib.parent)+os.pathsep+env.get(key, '')
results = []
def command(argv, path, log):
    with (path/log).open('w') as out:
        r = subprocess.run(list(map(str, argv)), cwd=path, env=env, stdout=out, stderr=subprocess.STDOUT, timeout=180)
    text = (path/log).read_text()
    assert r.returncode == 0, text[-4000:]
    return text

def case(name, init='', outer=4, threshold=1e-3, gravity=0):
    path = run/name
    path.mkdir()
    for sub in ('0', 'constant', 'system'): shutil.copytree(c.H1/sub, path/sub)
    (path/'0/h').rename(path/'unused-h')
    (path/'system/blockMeshDict').write_text(c.mesh_text())
    (path/'system/controlDict').write_text(c.header('dictionary','controlDict')+f'''
application HTFoam-review; startFrom startTime; startTime 0; stopAt endTime; endTime 2; deltaT 1;
writeControl timeStep; writeInterval 1; purgeWrite 0; writeFormat ascii; writePrecision 14;
writeCompression off; timeFormat general; timePrecision 14; runTimeModifiable false;
adjustTimeStep no; libs ("{lib}");
''')
    (path/'system/fvSolution').write_text(c.header('dictionary','fvSolution')+f'''
solvers {{ p {{ solver PCG; preconditioner DIC; tolerance 1e-12; relTol 0; }}
T {{ solver smoothSolver; smoother symGaussSeidel; tolerance 1e-12; relTol 0; }}
pFinal {{ $p; relTol 0.5; }} TFinal {{ $T; relTol 0.5; }} }}
PIMPLE {{ nOuterCorrectors {outer}; nCorrectors 1; nNonOrthogonalCorrectors 1; }}
PTCOUPLING {{ maxDeltaP {threshold}; tightCouplingIters 0; }}
{init}
''')
    (path/'constant/g').write_text(c.header('uniformDimensionedVectorField','g')+f'dimensions [0 1 -2 0 0 0 0]; value (0 {gravity} 0);\n')
    (path/'constant/xThermoProperties').write_text(c.header('dictionary','xThermoProperties')+'fluid H2O; backend IAPS84;\n')
    (path/'0/p').write_text(c.field('p','[1 -1 -2 0 0 0 0]',3e7,'type noFlux; value uniform 3e7;' if gravity else 'type fixedValue; value uniform 3e7;', 'type fixedValue; value uniform 3e7;'))
    (path/'0/T').write_text(c.field('T','[0 0 0 1 0 0 0]',300,'type fixedValue; value uniform 300;'))
    (path/'0/permeability').write_text(c.field('permeability','[0 2 0 0 0 0 0]',1e-15,'type zeroGradient;', 'type zeroGradient;'))
    command(['blockMesh'],path,'log.mesh')
    return path

def solve(path, executable=solver, log='log.solver'):
    text = command([executable],path,log)
    choices = re.findall(r'Lookup solver for (\w+)',text)
    transient = text.split('\nTime = ',1)[1]
    selected = re.findall(r'Lookup solver for (\w+)',transient)
    assert any(x in selected for x in ('p', 'pFinal')) and any(x in selected for x in ('T', 'TFinal'))
    if executable == solver:
        assert 'p' in selected and 'T' in selected
        assert not any(x.endswith('Final') for x in choices), choices
    return text, selected

def record(name, **kw):
    results.append(dict(test=name, **kw))
    (run/'results.json').write_text(json.dumps(results,indent=2)+'\n')
    print('PASS', name, flush=True)

p=case('early',outer=1)
t, choices=solve(p)
assert 'target met after 1 iterations' in t
record('early exit selects ordinary solvers', selected=sorted(set(choices)))
if a.old_solver:
    old_path = run/(p.name+'-old')
    shutil.copytree(p, old_path)
    t, choices=solve(old_path,a.old_solver.resolve(),'log.old')
    assert 'pFinal' in choices and 'TFinal' in choices
    record('old solver reproduces leaked final selection',selected=sorted(set(choices)))

p=case('exhaustion',init='INIT { maxIterations 3; maxDeltaP 0; }',outer=1)
t,_=solve(p)
assert t.count('initpEqn: iteration=')==3 and 'budget exhausted after 3 iterations' in t
record('explicit limit overrides legacy; exhaustion continues')

p=case('legacy-exhaustion',outer=2,threshold=0)
t,_=solve(p)
assert t.count('initpEqn: iteration=')==2 and 'budget exhausted after 2 iterations' in t
record('legacy outer limit remains functional')
if a.old_solver:
    old_path=run/'legacy-exhaustion-old'; shutil.copytree(p,old_path)
    t,choices=solve(old_path,a.old_solver.resolve(),'log.old')
    assert set(choices)=={'p','T'},choices
    record('old normal exhaustion clears final selection')

p=case('zero',outer=0)
t,_=solve(p)
assert 'skipped by initialization controls' in t
record('legacy zero disables initialization without final selection')
if a.old_solver:
    t,choices=solve(p,a.old_solver.resolve(),'log.old')
    assert 'pFinal' in choices
    record('old zero-outer case reproduces final selection')

p=case('disabled',init='INIT { enabled false; maxIterations 3; }')
t,_=solve(p)
assert 'initpEqn: iteration=' not in t
record('explicit disabled initialization')

p=case('hydrostatic',init='INIT { maxIterations 40; maxDeltaP 1e-6; }',gravity=-9.81)
t,_=solve(p)
assert 'target met after' in t
pressure=c.values(p/'2/p'); density=c.values(p/'2/rho'); velocity=c.values(p/'2/U')
y=[(i+.5)*.5/20 for i in range(20)]+[.5+(i+.5)*.5/40 for i in range(40)]
# Orthogonal two-point discrete hydrostatics: dp/dy = -g*rho_face.
err=max(abs((pressure[i+1]-pressure[i])/(y[i+1]-y[i])+9.81*(density[i]+density[i+1])/2) for i in range(59))
assert err < .1,err
assert max(map(abs,velocity)) < 1e-10, max(map(abs,velocity))
record('hydrostatic equilibrium', max_gradient_error_Pa_per_m=err,max_U_m_per_s=max(map(abs,velocity)), initial_iterations=t.count('initpEqn: iteration='))
# Continue unchanged equilibrium from saved time 2. Preserve all first-run output.
f=p/'system/controlDict'; s=f.read_text().replace('startTime 0;', 'startTime 2;').replace('endTime 2;', 'endTime 3;'); f.write_text(s)
t,_=solve(p,log='log.restart')
assert 'Initialize hydrostatic pressure' not in t
restart_delta=max(abs(x-y) for x,y in zip(c.values(p/'2/p'),c.values(p/'3/p')))
assert restart_delta < 1e-4, restart_delta
record('nonzero restart skips initialization',max_p_change_Pa=restart_delta)

p=case('hydrostatic-two-correctors',init='INIT { maxIterations 40; nCorrectors 2; maxDeltaP 1e-6; }',gravity=-9.81)
t,_=solve(p)
assert 'target met after' in t
pressure=c.values(p/'2/p')
reference=c.values(run/'hydrostatic/2/p')
error=max(abs(x-y) for x,y in zip(pressure,reference))
assert error < 1e-4,error
# On this orthogonal column, additional frozen-coefficient pressure solves must
# not incorporate the first pressure-dependent EOS density change (about 0.02 Pa).
first_delta = lambda text: float(re.search(r'initpEqn: iteration=1,.*?max\|delta p\|=([^,]+)',text)[1])
one_corrector_log=(run/'hydrostatic/log.solver').read_text()
first_delta_difference=abs(first_delta(t)-first_delta(one_corrector_log))
assert first_delta_difference < 1e-4, first_delta_difference
record('multiple pressure correctors converge to same hydrostatics',max_pressure_difference_Pa=error, initial_iterations=t.count('initpEqn: iteration='), first_outer_pressure_change_difference_Pa=first_delta_difference)
