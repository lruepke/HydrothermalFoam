#!/usr/bin/env python3
"""Regression for the OpenFOAM 10 heat-flux copying contract; no solver baseline needed."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess

HERE=Path(__file__).resolve().parent


def header(kind,name):
    return f'FoamFile {{ version 2.0; format ascii; class {kind}; object {name}; }}\n'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',type=Path,required=True)
    parser.add_argument('--legacy-only',action='store_true',help='also test the fix alone on pre-conductivity source')
    args=parser.parse_args()
    run=args.run.resolve()
    cases=run/'cases';cases.mkdir(exist_ok=False)
    library=next((p for p in (run/'lib/libHydrothermalBoundaryConditions.so',run/'lib/libHydrothermalBoundaryConditions.dylib') if p.exists()),None)
    assert library is not None
    env=os.environ.copy();env.pop('FOAM_ABORT',None)
    for key in ('DYLD_LIBRARY_PATH','LD_LIBRARY_PATH'):env[key]=str(library.parent)+os.pathsep+env.get(key,'')
    env.update(FOAM_USER_APPBIN=str(run/'bin'),FOAM_USER_LIBBIN=str(run/'lib'),
               CLONE_HEADER_DIR=str(run/'source/BoundaryConditions/HydrothermalHeatFlux'),
               CLONE_LINK_FLAGS='-Wl,-undefined,error' if library.suffix=='.dylib' else '-Wl,--no-allow-shlib-undefined')
    results=[]

    def command(argv,cwd,log,failure=None):
        p=subprocess.run(argv,cwd=cwd,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=120)
        log.write_text(p.stdout)
        if failure:
            assert p.returncode!=0 and all(word in p.stdout for word in failure),(argv,p.returncode,p.stdout[-2000:])
        else:assert p.returncode==0,(argv,p.returncode,p.stdout[-2000:])
        return p.stdout

    def record(name):
        results.append(dict(test=name,passed=True))
        (run/'results.json').write_text(json.dumps(results,indent=2)+'\n')
        print('PASS',name,flush=True)

    symbols=command(['nm','-u',str(library)],run,run/'undefined-symbols.txt')
    decoded=subprocess.run(['c++filt'],input=symbols,capture_output=True,text=True,check=True).stdout
    (run/'undefined-symbols-decoded.txt').write_text(decoded)
    assert 'HydrothermalHeatFlux::HydrothermalHeatFlux(Foam::HydrothermalHeatFlux const&)' not in decoded
    assert 'HydrothermalHeatFluxC1ERKS0_' not in symbols and 'HydrothermalHeatFluxC2ERKS0_' not in symbols
    record('plain-copy constructor has no unresolved library symbol')

    # Each must fail during compilation rather than remain a runtime trap.
    for name,expected in [('plainCopy',('deleted','HydrothermalHeatFlux')),('noArgumentClone',('clone',))]:
        project=run/('negative-'+name);(project/'Make').mkdir(parents=True)
        shutil.copy2(HERE/'negative'/f'{name}.C',project/f'{name}.C')
        (project/'Make/files').write_text(f'{name}.C\n\nEXE = $(FOAM_USER_APPBIN)/unsupported-{name}\n')
        shutil.copy2(HERE/'probe/Make/options',project/'Make/options')
        diagnostic=command(['wmake'],project,run/f'log.negative-{name}',failure=expected)
        if name=='noArgumentClone':
            assert 'no matching' in diagnostic or 'too few arguments' in diagnostic
        record(name+' rejected at compile time')

    for mode in (('legacy',) if args.legacy_only else ('legacy','field')):
        case=cases/mode
        for sub in ('0','constant','system'):(case/sub).mkdir(parents=True,exist_ok=True)
        (case/'system/controlDict').write_text(header('dictionary','controlDict')+f'''
application heatFluxCloneProbe; startFrom startTime; startTime 0; stopAt endTime;
endTime 1; deltaT 1; writeControl timeStep; writeInterval 1;
writeFormat ascii; writePrecision 16; runTimeModifiable false;
libs ("{library}");
''')
        (case/'system/blockMeshDict').write_text(header('dictionary','blockMeshDict')+'''
convertToMeters 1;
vertices ((0 0 0)(1 0 0)(1 1 0)(0 1 0)(0 0 1)(1 0 1)(1 1 1)(0 1 1));
blocks (hex (0 1 2 3 4 5 6 7) (4 1 1) simpleGrading (1 1 1)); edges ();
boundary (
 bottom {type patch; faces ((0 1 5 4));}
 top {type patch; faces ((3 7 6 2));}
 sides {type wall; faces ((0 3 2 1)(4 5 6 7)(0 4 7 3)(1 2 6 5));}
); mergePatchPairs ();
''')
        (case/'system/fvSchemes').write_text(header('dictionary','fvSchemes')+'''
ddtSchemes {default Euler;} gradSchemes {default Gauss linear;}
divSchemes {default none;} laplacianSchemes {default Gauss linear corrected;}
interpolationSchemes {default linear;} snGradSchemes {default corrected;}
''')
        (case/'system/fvSolution').write_text(header('dictionary','fvSolution')+'solvers {}\n')
        (case/'constant/thermophysicalProperties').write_text(header('dictionary','thermophysicalProperties')+
              'mixture { porousMedia { conductivity conductivity [1 1 -3 -1 0 0 0] 1.5; } }\n')
        (case/'0/kr_eff').write_text(header('volScalarField','kr_eff')+'''
dimensions [1 1 -3 -1 0 0 0]; internalField uniform 2;
boundaryField {
 bottom {type fixedValue; value nonuniform List<scalar> 4 (2 3 4 5);}
 top {type zeroGradient;} sides {type zeroGradient;}
}
''')
        selector='conductivityField kr_eff;' if mode=='field' else ''
        (case/'0/T').write_text(header('volScalarField','T')+f'''
dimensions [0 0 0 1 0 0 0]; internalField uniform 300;
boundaryField {{
 bottom {{type hydrothermalHeatFlux; kr conductivity; {selector}
 q nonuniform List<scalar> 4 (2 4 6 8); value uniform 300;
 shape gaussian3d; x0 0.2; z0_ 0.7; c 0.3; qmin 1; qmax 8;}}
 top {{type zeroGradient;}} sides {{type zeroGradient;}}
}}
''')
        command(['blockMesh'],case,case/'log.blockMesh')
        out=command([str(run/'bin/heatFluxCloneProbe')],case,case/'log.clone')
        assert 'PASS field copy' in out
        record(mode+' constructor/clone(iF)/field-copy and independent owner')


if __name__=='__main__':main()
