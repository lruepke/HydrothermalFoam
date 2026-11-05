#!/usr/bin/env bash
# Run only in a fresh copy outside the source checkout. Never clean existing runs.
set -euo pipefail
cd "$(dirname "$0")"
mode=run
triangle_mesh=false
for arg in "$@"; do
    case "$arg" in
        --prepare-only) mode=prepare ;;
        --smoke) mode=smoke ;;
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
blockMesh > log.blockMesh 2>&1
checkMesh > log.checkMesh 2>&1
grep -q 'Mesh OK' log.checkMesh
: > case.foam
if [[ $mode == prepare ]]; then
    echo "Prepared. Run $solver > log.HTFoam-review; open case.foam in ParaView."
    exit 0
fi
if [[ $mode == smoke ]]; then
    # Three one-hour steps, always in the fresh run copy; physical inputs unchanged.
    foamDictionary system/controlDict -entry startFrom -set startTime >> log.configure
    foamDictionary system/controlDict -entry deltaT -set 3600 >> log.configure
    foamDictionary system/controlDict -entry adjustTimeStep -set no >> log.configure
    foamDictionary system/controlDict -entry endTime -set 10800 >> log.configure
    foamDictionary system/controlDict -entry writeControl -set timeStep >> log.configure
    foamDictionary system/controlDict -entry writeInterval -set 1 >> log.configure
fi
"$solver" > log.HTFoam-review 2>&1
echo "Finished. Open case.foam in ParaView (T in K, p in Pa, U in m/s)."
