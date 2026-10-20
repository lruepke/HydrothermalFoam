
1. Generate 2D porous media using [porespy](https://github.com/PMEAL/porespy). The generation commands are written in [vtiGen.py](./vtiGen.py)

```bash
./vtiGen.py vti/cube
 ```

2. Process vti file, extract network surface, triangulate, calculate connectivity and then save as vtu file. In this step, the paraview is required, and check whether `pvpython` path is correct in the first line of [process_paraview.py](./process_paraview.py)
```
./process_paraview.py vti/cube.vti
```

3. Split boundary patches and porous network surface, and then save as stl file. Get coordinate of point in the porous networks and save to `locationInMesh.txt` file. `blockMeshDict` file is also generated automatically according to bounding box of the vtu data. All the output files are save to the `stl` folder. All the process codes are written in [process_stl.py](./process_stl.py)
```bash
./process_stl.py vti/cube.vtu
```

