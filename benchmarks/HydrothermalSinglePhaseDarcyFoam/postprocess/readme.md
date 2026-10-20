

# Extract T and p from results of HYDROTHERMAL

The python scripts for extracting pressure and temperature of HYDROTHERMAL results.
Just input the extension name of result file,
and then the python script will extract T and P, and write to files named, e.g., `dx10_T_p_50.0.txt`, which means temperature and pressure at 50 year.

```bash
python extractT_p_2D.py dx10
```