#!/bin/bash
# Debug wrapper for HTFoam that ensures proper OpenFOAM environment

# Get absolute path of HTFoam executable
HTFOAM_PATH=$(realpath "$1")

# Source OpenFOAM environment
source /Volumes/OpenFoam/OpenFOAM-10/etc/bashrc

# Change to the case directory
cd "/Users/lruepke/git-geomar/HydrothermalFoam/tutorials/Regular2DBox"

# Run HTFoam with the absolute path
exec "$HTFOAM_PATH"