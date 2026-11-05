#!/usr/bin/env python3
"""Check layered inputs and Darcy interface accuracy; optional actual-solver smoke test.

Source OpenFOAM 10, activate py313_htf, then use:
poetry run python tests/check_layered.py --output /absolute/new/check-directory
Builds the small probe there. Add --solver PATH --library PATH to verify the
configured harmonic lookup in an unchanged HTFoam executable (one 0.01-year step).
This does not qualify pressure elevation or bidirectional thermal equivalence.
"""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'postprocess'))
from _fields import centres, mesh_points, numeric_field


def plain(text):
    return [line.strip() for line in text.splitlines() if line.strip() and not line.lstrip().startswith('#')]


def expand(lines):
    values = []
    for token in ' '.join(lines).split():
        if '*' in token:
            count, value = token.split('*')
            values.extend([float(value)]*int(count))
        else:
            values.append(float(token))
    return np.array(values)


def hydro_geometry(path):
    """Structural checks for this derivative of the verified Version 3.2 input."""
    text = path.read_text()
    dims = plain(text.split('# DIMENSIONS', 1)[1].split('# TIME STEP', 1)[0])[0].split()
    assert list(map(int, dims)) == [90, 1, 30, 0, 2]
    rock = plain(text.split('# SLICE number', 1)[1].split('# UNCONFINED', 1)[0])
    assert rock.pop(0) == 'TOP'
    rock = np.array([expand([line]) for line in rock][::-1], int)
    assert rock.shape == (30, 90)
    assert (rock[:19] == 2).all() and (rock[19:29] == 1).all() and (rock[29] == -1001).all()
    z = plain(text.split('ZSPACING (m)', 1)[1].split('XPERMEABILITY', 1)[0])
    assert z == ['CONSTANT', '100.0']
    dz = np.full(30, float(z[1]))
    height = np.cumsum(dz)-dz/2  # gdata.f90:1224-1227, bottom face datum zero
    assert np.isclose(height[-1], 2950, rtol=0, atol=1e-10)
    assert np.isclose(dz[:19].sum(), 1900)
    assert np.isclose(dz.sum(), 3000) and np.isclose(dz[-1], 100)
    for quantity, value in [('PRESSURE', (30e6+1014.19371025668*9.81*50)/1e5), ('TEMPERATURE', 5.0)]:
        node = re.search(r'(?m)^'+quantity+r' \([^\n]+\)\nNODE\n(.*?)^\s*0\s+0\s+0\s+0\s*$', text, re.S)
        assert node, quantity
        rows = np.array([list(map(float, line.split())) for line in plain(node[1])])
        assert rows.shape == (90, 4)
        assert np.array_equal(rows[:, 0], np.arange(1, 91))
        assert (rows[:, 1:3] == [1, 30]).all() and np.allclose(rows[:, 3], value, rtol=0, atol=1e-10)
    expected = {'XPERMEABILITY':(1e-14, 1e-15), 'ZPERMEABILITY':(1e-14, 1e-15),
                'POROSITY':(.1, .1), 'COMPRESSIBILITY':(0., 0.),
                'RDENSITY':(2700., 2700.), 'SPECIFIC_HEAT':(880., 880.),
                'THERMAL_COND':(2., 2.)}
    for quantity, values in expected.items():
        block = re.search(r'(?m)^'+quantity+r' \([^\n]+\)\nRTFTEMP\n(.*?)(?=^[A-Z])', text, re.S)
        rows = plain(block[1]);assert len(rows) == 4, quantity
        for i, value in enumerate(values):
            assert rows[2*i].split() == [str(i+1), '1', '1']
            assert float(rows[2*i+1]) == value, quantity
    assert 'YPERMEABILITY (m^2)\nCALCULATE\n' in text
    heat = expand(plain(text.split('CONDUCTIVE Heat Input along Base (W/m^2)', 1)[1].split('# End of Keyword', 1)[0])[1:])
    assert len(heat) == 90
    return height, dz, heat


def header(name, cls='dictionary'):
    return f'FoamFile {{ version 2.0; format ascii; class {cls}; object {name}; }}\n'


def darcy_case(case, nlow, nhigh, scheme, lookup):
    for part in ('0', 'constant', 'system'):(case/part).mkdir(parents=True)
    (case/'system/controlDict').write_text(header('controlDict')+'application layeredDarcyProbe; startFrom startTime; startTime 0; stopAt endTime; endTime 1; deltaT 1; writeControl timeStep; writeInterval 1;\n')
    mesh = '''convertToMeters 1;
vertices ((0 0 0)(1900 0 0)(1900 1 0)(0 1 0)(0 0 1)(1900 0 1)(1900 1 1)(0 1 1)(3000 0 0)(3000 1 0)(3000 0 1)(3000 1 1));
blocks (hex (0 1 2 3 4 5 6 7) (NLOW 1 1) simpleGrading (1 1 1)
hex (1 8 9 2 5 10 11 6) (NHIGH 1 1) simpleGrading (1 1 1)); edges ();
boundary (left { type patch; faces ((0 4 7 3)); } right { type patch; faces ((8 9 11 10)); }
sides { type empty; faces ((0 1 5 4)(1 8 10 5)(3 7 6 2)(2 6 11 9)(0 3 2 1)(1 2 9 8)(4 5 6 7)(5 10 11 6)); }); mergePatchPairs ();
'''.replace('NLOW',str(nlow)).replace('NHIGH',str(nhigh))
    (case/'system/blockMeshDict').write_text(header('blockMeshDict')+mesh)
    interpolation='default linear;' if scheme=='linear' else f'default linear; {lookup} harmonic;'
    (case/'system/fvSchemes').write_text(header('fvSchemes')+'ddtSchemes {default Euler;} gradSchemes {default Gauss linear;} divSchemes {default none;} laplacianSchemes {default Gauss linear corrected;} interpolationSchemes {'+interpolation+'} snGradSchemes {default corrected;} fluxRequired {default no; p;}\n')
    (case/'system/fvSolution').write_text(header('fvSolution')+'solvers {p {solver PCG; preconditioner DIC; tolerance 1e-13; relTol 0; maxIter 10000;}}\n')
    (case/'0/p').write_text(header('p','volScalarField')+'dimensions [1 -1 -2 0 0 0 0]; internalField uniform 30500000; boundaryField {left {type fixedValue; value uniform 31000000;} right {type fixedValue; value uniform 30000000;} sides {type empty;}}\n')
    values=' '.join(['1e-15']*nlow+['1e-14']*nhigh)
    (case/'0/permeability').write_text(header('permeability','volScalarField')+f'dimensions [0 2 0 0 0 0 0]; internalField nonuniform List<scalar> {nlow+nhigh} ({values}); boundaryField {{left {{type zeroGradient;}} right {{type zeroGradient;}} sides {{type empty;}}}}\n')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--solver', type=Path, help='optional matching HTFoam-review executable')
    parser.add_argument('--library', type=Path, help='matching boundary library, required with --solver')
    args=parser.parse_args();out=args.output.resolve()
    if bool(args.solver) != bool(args.library):parser.error('Supply both --solver and --library')
    for path in (args.solver,args.library):
        if path and not path.is_file():parser.error(f'Missing runtime dependency: {path}')
    if os.environ.get('WM_PROJECT_VERSION')!='10':parser.error('Source OpenFOAM Foundation 10 in bash first')
    if ROOT in out.parents and ROOT/'work' not in out.parents:
        parser.error('Put generated checks under work/ or outside the benchmark source tree')
    for name in ('pEqn.H', 'initpEqn.H'):
        code=(ROOT.parents[1]/'solvers/HTFoam'/name).read_text()
        assert 'volScalarField rAU(permeability/mu);' in code
        assert 'fvc::interpolate(rho*rAU)' in code
    out.mkdir(parents=True,exist_ok=False)
    env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1'
    env.setdefault('MPLCONFIGDIR', str(out/'mpl'))
    env.setdefault('XDG_CACHE_HOME', str(out/'cache'))
    def command(argv, cwd, log):
        with (out/log).open('w') as stream:subprocess.run(list(map(str,argv)),cwd=cwd,env=env,stdout=stream,stderr=subprocess.STDOUT,check=True)
    # Only the standalone verification utility is compiled, in a private build.
    build=out/'build';shutil.copytree(ROOT/'tests/layeredDarcy',build);(out/'bin').mkdir();env['FOAM_USER_APPBIN']=str(out/'bin')
    command(['wmake'],build,'build.log')
    lookup=None;records=[]
    for nlow,nhigh in [(19,11),(38,22),(76,44),(1,1)]:
        for scheme in ('linear','harmonic'):
            case=out/f'darcy-{nlow+nhigh}-{scheme}';darcy_case(case,nlow,nhigh,scheme,lookup)
            command(['blockMesh'],case,case.name+'-mesh.log');command([out/'bin/layeredDarcyProbe'],case,case.name+'.log')
            text=(out/(case.name+'.log')).read_text();key=re.search(r'^MOBILITY_LOOKUP (.+)$',text,re.M)[1];lookup=key if lookup is None else lookup;assert key==lookup
            row=np.fromstring(re.search(r'^RESULT (.+)$',text,re.M)[1],sep=' ')
            fields=('cells','q_exact_m_s','q_m_s','k_face_m2','drop_Pa','exact_drop_Pa','max_pressure_error_Pa','max_relative_flux_error','relative_flux_spread','net_boundary_mass_kg_s','max_relative_velocity_error');record=dict(zip(fields,map(float,row)));record['scheme']=scheme
            dl,dr=1900/nlow/2,1100/nhigh/2;klo,khi=1e-15,1e-14
            kf=(dr*klo+dl*khi)/(dl+dr) if scheme=='linear' else (dl+dr)/(dl/klo+dr/khi)
            resistance=1900/klo+1100/khi-(dl/klo+dr/khi)+(dl+dr)/kf
            qmodel=1e6/(1e-3*resistance)
            assert np.isclose(record['k_face_m2'],kf,rtol=1e-12,atol=0)
            assert np.isclose(record['q_m_s'],qmodel,rtol=1e-9,atol=0),record
            assert record['relative_flux_spread']<1e-8,record
            if scheme=='harmonic':assert record['max_relative_flux_error']<1e-8 and record['max_pressure_error_Pa']<1e-3,record
            if scheme=='harmonic':assert record['max_relative_velocity_error']<1e-8,record
            record['flux_error_percent']=100*(record['q_m_s']/record['q_exact_m_s']-1)
            record['interface_drop_error_percent']=100*(record['drop_Pa']/record['exact_drop_Pa']-1);records.append(record)
    # Prepare the actual new inputs, mesh them, and parse all OpenFOAM dictionaries.
    run=out/'layered';command([sys.executable,ROOT/'run.py','--case','2d-layered','--output',run,'--prepare-only','--solver','__not_required__'],ROOT,'prepare.log');case=run/'case';command(['blockMesh'],case,'layered-mesh.log')
    for part in ('0','constant','system'):
        for path in (case/part).iterdir():
            if path.is_file():command(['foamDictionary',path,'-keywords'],case,'parse-'+part+'-'+path.name+'.log')
    xyz=centres(case);pts=mesh_points(case);assert len(xyz)==2700
    assert np.array_equal(pts.min(axis=0),[0,-3000,0]) and np.array_equal(pts.max(axis=0),[9000,0,1])
    permeability=numeric_field(case/'0/permeability');expected=np.where(xyz[:,1]>-1100,1e-14,1e-15);assert np.array_equal(permeability,expected)
    assert int((permeability==1e-14).sum())==990 and int((permeability==1e-15).sum())==1710
    top_p=re.search(r'\btop\s*\{([^{}]*)\}',(case/'0/p').read_text(),re.S)[1]
    assert re.search(r'\btype\s+fixedValue\s*;',top_p) and re.search(r'\bvalue\s+uniform\s+3e7\s*;',top_p)
    initial_T=numeric_field(case/'0/T')
    assert np.array_equal(initial_T,np.where(xyz[:,1]>-100,278.15,283.15))
    top=re.search(r'\btop\s*\{([^{}]*)\}',(case/'0/T').read_text(),re.S)[1]
    assert re.search(r'\btype\s+inletOutlet\s*;',top)
    assert re.search(r'\binletValue\s+uniform\s+278\.15\s*;',top)
    assert 'kr kr [1 1 -3 -1 0 0 0] 2;' in (case/'constant/transportProperties').read_text()
    height,dz,heat=hydro_geometry(run/'reference.input');qtext=(case/'0/T').read_text();q=np.fromstring(re.search(r'q nonuniform List<scalar> 90\s*\(([^)]+)\)',qtext)[1],sep=' ');assert np.array_equal(heat,q);power=float((q*100).sum());assert np.isclose(power,5390)
    smoke=None
    if args.solver:
        # Preserve the executable and library; never replace installed artifacts.
        (out/'lib').mkdir()
        private=out/'lib'/args.library.name
        shutil.copy2(args.library.resolve(),private)
        executable=out/'bin/HTFoam-review'
        shutil.copy2(args.solver.resolve(),executable)
        env['DYLD_LIBRARY_PATH']=str(out/'lib')+os.pathsep+env.get('DYLD_LIBRARY_PATH','')
        env['LD_LIBRARY_PATH']=str(out/'lib')+os.pathsep+env.get('LD_LIBRARY_PATH','')
        path=case/'system/controlDict';text=path.read_text()
        for key,value in [('endTime',315576),('deltaT',315576),('adjustTimeStep','no'),('writeInterval',315576)]:
            text,count=re.subn(r'\b'+key+r'\s+[^;]+;',f'{key} {value};',text,count=1);assert count==1
        text=re.sub(r'"[^"\n]*libHydrothermalBoundaryConditions\.(so|dylib)"',lambda _: '"'+str(private)+'"',text)
        path.write_text(text+'\nDebugSwitches { surfaceInterpolation 1; }\n')
        command([executable],case,'actual-solver.log')
        text=(out/'actual-solver.log').read_text()
        before,after=text.split('Time = 315576',1)
        counts=[]
        for section in (before,after):
            selected=re.findall(r'using interpolate\(\(rho\*\(permeability\|mu\)\)\)(.*?)(?=interpolating GeometricField|$)',section,re.S)
            assert selected and all('Discretisation scheme = harmonic' in item for item in selected)
            counts.append(len(selected))
        assert counts[1]==8 and 'End' in after
        smoke=dict(initialization_harmonic_selections=counts[0],transient_harmonic_selections=counts[1],years=.01)
    report=dict(mobility_lookup_key=lookup,interface_tests=records,
                boundary=dict(HTFoam_top_faces=90,HYDROTHERM_IBC10_top_nodes=90,
                              HT_pressure_y_m=0,HY_pressure_y_m=float(height[-1]-3000),
                              pressure_Pa=3e7,uniform_cell_height_m=float(dz[-1]),
                              thermal_equivalence_qualified=False,
                              HT_pressure_datum_y_m=0,HY_pressure_Pa=30e6+1014.19371025668*9.81*50,
                              basal_power_W_per_m_thickness=power),
                actual_solver_smoke=smoke)
    (out/'foundation-results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))


if __name__=='__main__':main()
