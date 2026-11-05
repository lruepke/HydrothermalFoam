#!/usr/bin/env python3
"""Complete shared-library clone regression; no HTFoam baseline required."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

HERE=Path(__file__).resolve().parent
CLASSES=(('noFlux','noFluxFvPatchScalarField.H'),
         ('HydrothermalMassFluxPressure','HydrothermalMassFluxPressureFvPatchScalarField.H'),
         ('submarinePressureFvPatchScalarField','submarinePressureFvPatchScalarField.H'))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',type=Path,required=True)
    run=parser.parse_args().run.resolve()
    cases=run/'pressure-cases';cases.mkdir(exist_ok=False)
    library=next((p for p in (run/'lib/libHydrothermalBoundaryConditions.so',run/'lib/libHydrothermalBoundaryConditions.dylib') if p.exists()),None)
    assert library is not None
    env=os.environ.copy();env.pop('FOAM_ABORT',None)
    for key in ('DYLD_LIBRARY_PATH','LD_LIBRARY_PATH'):env[key]=str(library.parent)+os.pathsep+env.get(key,'')
    env.update(FOAM_USER_APPBIN=str(run/'bin'),FOAM_USER_LIBBIN=str(run/'lib'),
               CLONE_HEADER_DIR=str(run/'source/BoundaryConditions/HydrothermalHeatFlux'),
               CLONE_LINK_FLAGS='-Wl,-undefined,error' if library.suffix=='.dylib' else '-Wl,--no-allow-shlib-undefined')
    results=[]

    def command(argv,cwd,log,failure=False):
        p=subprocess.run(argv,cwd=cwd,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=120)
        log.write_text(p.stdout)
        assert (p.returncode!=0) if failure else (p.returncode==0),(argv,p.returncode,p.stdout[-2500:])
        return p.stdout

    def record(name):
        results.append(dict(test=name,passed=True))
        (run/'pressure-results.json').write_text(json.dumps(results,indent=2)+'\n')
        print('PASS',name,flush=True)

    # Existing heat-flux contract checks now run against the COMPLETE library.
    command([sys.executable,str(HERE.parent/'heatFluxClone/run_tests.py'),'--run',str(run)],run,run/'log.heat-flux-tests')
    symbols=command(['nm','-u',str(library)],run,run/'full-library-undefined-symbols.txt')
    decoded=subprocess.run(['c++filt'],input=symbols,capture_output=True,text=True,check=True).stdout
    (run/'full-library-undefined-symbols-decoded.txt').write_text(decoded)
    for cls in ('HydrothermalHeatFlux',*(c for c,h in CLASSES)):
        assert f'{cls}::{cls}(Foam::{cls} const&)' not in decoded,cls
    if library.suffix=='.so':
        relocations=command(['ldd','-r',str(library)],run,run/'log.ldd-relocations')
        assert 'undefined symbol' not in relocations and 'not found' not in relocations
    record('complete shared library has no unresolved plain-copy constructors')

    for cls,header in CLASSES:
        for scenario in ('copy','clone'):
            project=run/f'negative-{cls}-{scenario}';(project/'Make').mkdir(parents=True)
            expression=f'Foam::{cls} copied(source);' if scenario=='copy' else 'auto copied=source.clone();'
            (project/'unsupported.C').write_text(f'#include "{header}"\nvoid unsupported(const Foam::{cls}& source) {{ {expression} }}\nint main() {{ return 0; }}\n')
            (project/'Make/files').write_text('unsupported.C\n\nEXE = $(FOAM_USER_APPBIN)/unsupported-pressure-copy\n')
            shutil.copy2(HERE/'probe/Make/options',project/'Make/options')
            diagnostic=command(['wmake'],project,run/f'log.negative-{cls}-{scenario}',failure=True)
            if scenario=='copy':assert 'deleted' in diagnostic and cls in diagnostic
            else:assert 'clone' in diagnostic and ('no matching' in diagnostic or 'too few arguments' in diagnostic)
            record(cls+' unsupported '+scenario+' rejected at compile time')

        case=cases/cls;shutil.copytree(run/'cases/legacy',case)
        mesh=case/'system/blockMeshDict';s=mesh.read_text()
        old='vertices ((0 0 0)(1 0 0)(1 1 0)(0 1 0)(0 0 1)(1 0 1)(1 1 1)(0 1 1));'
        new='vertices ((0 -2 0)(1 -2 0)(1 -1 0)(0 -1 0)(0 -2 1)(1 -2 1)(1 -1 1)(0 -1 1));'
        assert old in s;mesh.write_text(s.replace(old,new))
        (case/'constant/g').write_text('FoamFile {version 2.0; format ascii; class uniformDimensionedVectorField; object g;}\ndimensions [0 1 -2 0 0 0 0]; value (0 -9.81 0);\n')
        selectors='rhorAUf mobilityCloneTest; phig gravityCloneTest;'
        if cls=='noFlux': config='type noFlux; '+selectors
        elif cls=='HydrothermalMassFluxPressure':config='type hydrothermalMassFluxPressure; '+selectors+' q nonuniform List<scalar> 4 (0.1 0.2 0.3 0.4);'
        else:config='type submarinePressure; rhoValue 1123;'
        (case/'0/p').write_text(f'''FoamFile {{version 2.0; format ascii; class volScalarField; object p;}}
dimensions [1 -1 -2 0 0 0 0]; internalField uniform 300000;
boundaryField {{ bottom {{ {config} value uniform 300000; }}
 top {{type zeroGradient;}} sides {{type zeroGradient;}} }}
''')
        command(['blockMesh'],case,case/'log.blockMesh')
        text=command([str(run/'bin/pressureCloneProbe')],case,case/'log.pressure-clone')
        assert 'PASS' in text and 'configuration and owner' in text
        record(cls+' constructor/clone(iF)/field-copy preserve references and state')


if __name__=='__main__':main()
