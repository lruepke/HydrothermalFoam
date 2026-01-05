[![Docker badge](https://img.shields.io/badge/Docker-Image-<COLOR>.svg)](https://hub.docker.com/repositories/lruepke)
[![GPLv3 License](https://img.shields.io/badge/License-GPL%20v3-yellow.svg)](LICENSE)



# About HydrothermalFOAM
**HydrothermalFoam** —combination of **hydrothermal** and **OpenFOAM** — 
a three dimensional hydro-thermo-transport model designed to resolvefluid flow within submarine hydrothermal circulation systems. 
HydrothermalFoam has been developed on the OpenFOAM platform, 
which is a Finite Volume based C++ toolbox for fluid-dynamic simulations 
and for developing customized numerical solvers that provides access to 
state-of-the-art parallelized solvers and to a wide range of pre- and post-processing tools. 
We have implemented a porous media Darcy-flow model with associated boundary conditions designed to facilitate numerical 
simulations of submarine hydrothermal systems. 
The current implementation is valid for single-phase fluid states and uses a pure water equation-of-state (IAPWS-97). 
We here present the model formulation, OpenFOAM implementation details, and a sequence of 1-D, 2-D and 3-D benchmark tests. 
The source code repository further includes a number of tutorials that canbe used as starting points 
for building specialized hydrothermal flow models. 

# [Download and installation instructions](https://www.hydrothermalfoam.info/manual/en/Installation/index.html)
# Documentation: [English version](https://www.hydrothermalfoam.info/manual/en/index.html),  [Chinese version](https://www.hydrothermalfoam.info/manual/zh/index.html)
# [Quick start video tutorial](https://youtu.be/6czcxC90gp0)
# [Source code documentation](https://gmdpapers.gitlab.io/hydrothermalfoam/doxygen/)
# [Reporting bugs in HydrothermalFOAM](https://gitlab.com/gmdpapers/hydrothermalfoam/-/issues)

# [HydrothermalFOAM environment docker image](https://hub.docker.com/repositories/lruepke)

# How to cite

* [Endnote](https://gmd.copernicus.org/preprints/gmd-2020-140/gmd-2020-140.ris)

* [BibTex entry](https://gmd.copernicus.org/preprints/gmd-2020-140/gmd-2020-140.bib)

```
@article{guo2020hydrothermalfoam,
author = {Guo, Zhikui and R{\"{u}}pke, Lars and Tao, Chunhui},
doi = {10.5194/gmd-2020-140},
journal = {Geoscientific Model Development},
number = {July},
title = {{HydrothermalFoam v1 . 0 : a 3-D hydro-thermo-transport model for natural submarine hydrothermal systems}},
year = {2020}
}
```

# Licence
HydrothermalFoam is free software: you can redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.  See the [LICENSE](./LICENSE).