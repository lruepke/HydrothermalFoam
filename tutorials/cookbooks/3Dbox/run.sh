#!/usr/bin/env bash
# Run only in a fresh copy outside the source checkout. Never clean existing runs.
set -euo pipefail
cd "$(dirname "$0")"
mode=run
parallel=false
for arg in "$@"; do
    case "$arg" in
        --prepare-only) mode=prepare ;;
        --smoke) mode=smoke ;;
        --parallel) parallel=true ;;
        *) echo "Unknown option: $arg" >&2; exit 2 ;;
    esac
done
: "${WM_PROJECT_DIR:?Activate OpenFOAM Foundation 10 in bash first}"
[[ ${WM_PROJECT_VERSION:-} == 10 ]] || { echo "Require Foundation 10" >&2; exit 2; }
if git ls-files --error-unmatch system/controlDict >/dev/null 2>&1; then
    echo "Copy this case outside the checkout before running." >&2; exit 2
fi
[[ ! -e constant/polyMesh ]] || { echo "Existing mesh: use a fresh case copy." >&2; exit 2; }
solver=${HTFOAM_SOLVER:-HTFoam-review}
command -v "$solver" >/dev/null || { echo "Missing solver: $solver" >&2; exit 2; }
library=${HTFOAM_LIBRARY:-${FOAM_USER_LIBBIN}/libHydrothermalBoundaryConditions.so}
if [[ ! -f $library && -f ${library%.so}.dylib ]]; then library=${library%.so}.dylib; fi
[[ -f $library ]] || { echo "Set HTFOAM_LIBRARY to the matching built library." >&2; exit 2; }
foamDictionary system/controlDict -entry libs -set "(\"$library\")" > log.configure 2>&1
gmsh gmsh/box.geo -3 -format msh22 -o gmsh/box.msh > log.gmsh 2>&1
gmshToFoam gmsh/box.msh > log.gmshToFoam 2>&1
checkMesh > log.checkMesh 2>&1
grep -q 'Mesh OK' log.checkMesh
: > case.foam
if [[ $mode == prepare ]]; then
    echo "Prepared. Run $solver > log.HTFoam-review; open case.foam in ParaView."
    exit 0
fi
if [[ $mode == smoke ]]; then
    # One one-hour step, always in the fresh run copy; physical inputs unchanged.
    foamDictionary system/controlDict -entry startFrom -set startTime >> log.configure
    foamDictionary system/controlDict -entry deltaT -set 3600 >> log.configure
    foamDictionary system/controlDict -entry adjustTimeStep -set no >> log.configure
    foamDictionary system/controlDict -entry endTime -set 3600 >> log.configure
    foamDictionary system/controlDict -entry writeControl -set timeStep >> log.configure
    foamDictionary system/controlDict -entry writeInterval -set 1 >> log.configure
fi
if [[ $parallel == true ]]; then
    decomposePar > log.decomposePar 2>&1
    mpi_env=()
    if [[ ${WM_ARCH:-} == darwin* ]]; then
        # Restore/forward the MPI library path across macOS launcher boundaries.
        export DYLD_LIBRARY_PATH="$FOAM_LIBBIN/$FOAM_MPI:$FOAM_LIBBIN:${DYLD_LIBRARY_PATH:-}"
        mpi_env=(-x DYLD_LIBRARY_PATH)
    fi
    mpirun "${mpi_env[@]}" -np 2 "$solver" -parallel > log.HTFoam-review 2>&1
    reconstructPar > log.reconstructPar 2>&1
else
    "$solver" > log.HTFoam-review 2>&1
fi
echo "Finished. Open case.foam in ParaView (T in K, p in Pa, U in m/s)."
