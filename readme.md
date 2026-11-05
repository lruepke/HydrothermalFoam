# HydrothermalFoam / HTFoam

HTFoam simulates single-phase thermal convection and Darcy flow in porous media,
principally submarine hydrothermal systems. It solves pressure and temperature
with fluid properties from xThermo. Water and fixed-composition H2O–NaCl are
supported; salinity transport, multiple fluid phases and salt precipitation are
outside this solver's scope.

The [modernization overview](solvers/HTFoam/Modernization.md) explains the numerical
changes and scientific verification limits.

## Requirements and build

Use **OpenFOAM Foundation 10**, Bash, a C++ compiler and an installed
[xThermo C++ library](https://lruepke.github.io/xThermo/installation/). CMake is
needed to build xThermo; bundled GSL provides the layout used by Make/options.
Gmsh and ParaView are needed for meshing and visualization; Triangle is optional.

For example, after obtaining xThermo sources in `$HOME/xThermo`:

```bash
cmake -S "$HOME/xThermo" -B "$HOME/xThermo/build" \
  -DCMAKE_INSTALL_PREFIX="$HOME/xThermo/install" \
  -DXTHERMO_BUNDLED_GSL=ON -DXTHERMO_PYTHON=OFF
cmake --build "$HOME/xThermo/build" --parallel
cmake --install "$HOME/xThermo/build"
```

From this repository root, in Bash:

```bash
source /path/to/OpenFOAM-10/etc/bashrc
export xThermo_DIR="$HOME/xThermo/install"
(cd libraries/BoundaryConditions && wmake libso)
(cd solvers/HTFoam && wmake)
```

The executable is currently **HTFoam-review**. Rebuild when switching xThermo
installations. See [case configuration](solvers/HTFoam/CaseConfiguration.md) for
supported dictionaries, numerical controls and boundary conditions. Older online
manual chapters describe earlier releases and may use obsolete build instructions.

## Five maintained tutorials

| Example | Purpose |
|---|---|
| [Regular2DBox](tutorials/cookbooks/2d/Regular2DBox/README.md) | Uniform-permeability convection |
| [Regular2DBox_layered](tutorials/cookbooks/2d/Regular2DBox_layered/README.md) | Permeability zoning and harmonic mobility |
| [Regular2DBox_exp_perm](tutorials/cookbooks/2d/Regular2DBox_exp_perm/README.md) | Compiled exponential permeability; 1000 C basal boundary |
| [gmsh2DBox](tutorials/cookbooks/2d/gmsh2DBox/README.md) | Independent Gmsh and Triangle mesh alternatives |
| [3Dbox](tutorials/cookbooks/3Dbox/README.md) | 3D convection with serial and two-rank instructions |

The 3D example explicitly uses **X=0 instead of the original X=0.2**: its
600 C / 30 MPa saline hot state is vapor + halite and cannot be simulated by
single-phase HTFoam. Geometry and heating are preserved; this is not the original
saline model. These tutorials have brief smoke qualification, not full-duration
accuracy certification. Other tutorials are historical/unqualified; their inputs
are preserved under `tutorials/old/` in the development tree and in Git history,
and are excluded from the public snapshot.

Always run a fresh copy outside the checkout:

```bash
export HTFOAM_SOLVER="$FOAM_USER_APPBIN/HTFoam-review"
export HTFOAM_LIBRARY="$FOAM_USER_LIBBIN/libHydrothermalBoundaryConditions.so"
# On macOS use the matching .dylib library.
mkdir -p "$HOME/HydrothermalFoam_runs"
cp -R tutorials/cookbooks/2d/Regular2DBox "$HOME/HydrothermalFoam_runs/box-smoke"
bash "$HOME/HydrothermalFoam_runs/box-smoke/run.sh" --smoke
```

Open the resulting `case.foam` in ParaView. Each tutorial README explains mesh
preparation, full runs and its limits; scripts never clean existing runs.

## Benchmarks and mesh conversion

[benchmarks/HTFoam](benchmarks/HTFoam/README.md) contains quantitative HYDROTHERM
comparisons, reference inputs/data and reproducible run/plot instructions.
Teaching tutorials and quantitative benchmarks are separate collections.

[utilities/triToFoam](utilities/triToFoam/readme.md) converts Triangle meshes to
OpenFOAM prism meshes. Build it with `(cd utilities/triToFoam && wmake)`.
The [Gmsh/Triangle tutorial](tutorials/cookbooks/2d/gmsh2DBox/README.md) shares one
solver configuration between both mesh routes; Triangle is a separate dependency.

## Python environment

Python comparison scripts require Python 3.13, NumPy and Matplotlib. The project
uses Conda environment `py313_htf` and Poetry:

```bash
conda env create --file environment.yaml  # first setup only
conda activate py313_htf
POETRY_VIRTUALENVS_CREATE=false poetry install --no-root
poetry run python --version
```

The root environment.yaml, pyproject.toml and poetry.lock declare that workflow
and are included in the public snapshot. Solver runs and ParaView visualization
do not require this Python environment.

## Citation and license

Please cite [Guo, Rüpke and Tao (2020), HydrothermalFoam v1.0](https://doi.org/10.5194/gmd-13-6547-2020).
HydrothermalFoam is distributed under [GNU GPL v3](LICENSE).
