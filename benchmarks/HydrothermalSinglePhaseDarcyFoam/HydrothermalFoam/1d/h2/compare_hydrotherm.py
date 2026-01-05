#!/Users/zguo/.pyenv/shims/python
# -*- coding:utf-8 -*-
# Plot 1D result of HydrothermalFoam vs USGS HYDROTHERMAL (no enthalpy case)
# ---------------------------------------------------------------
# Zhikui Guo, 2020/05/22 (refreshed)
# ---------------------------------------------------------------

import os
import sys
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

# --- Matplotlib aesthetics ---
mpl.rcParams['font.family'] = 'Arial'
mpl.rcParams['mathtext.fontset'] = 'cm'
mpl.rcParams['figure.dpi'] = 120

def usage(argv):
    basename = os.path.basename(argv[0])
    desc = "Plot 1D HydrothermalFoam vs HYDROTHERMAL (temperature & pressure)"
    pad = max(0, (len(desc) + 20 - len(basename)) // 2)
    head = '='*pad + basename + '='*pad
    print(head)
    print(desc)
    print('Example: {} time(7884000000)'.format(basename))
    print('='*len(head))

def _interp_to(x_src, y_src, x_target):
    """Linear interpolation y(x_src)->y(x_target); returns NaNs outside overlap."""
    y = np.interp(x_target, x_src, y_src, left=np.nan, right=np.nan)
    return y

def _err_metrics(y_ref_on_our_grid, y_our):
    """Compute RMSE and Linf on overlapping (non-NaN) region."""
    m = np.isfinite(y_ref_on_our_grid) & np.isfinite(y_our)
    if not np.any(m):
        return np.nan, np.nan
    diff = y_our[m] - y_ref_on_our_grid[m]
    rmse = np.sqrt(np.mean(diff**2))
    linf = np.max(np.abs(diff))
    return rmse, linf

def plot_1d(time_str):
    # --- labels & file paths (unchanged) ---
    label2 = 'temperature'
    label3 = 'USGS HYDROTHERM'
    filename2 = label2 + '/postProcessing/linesample/' + time_str + '/data.xy'
    filename_HT = '../../../USGS_HYDROTHERMAL/1d/h2/h2_T_p_120.0.txt'

    # --- load our results ---
    data2 = np.loadtxt(filename2)
    x2 = data2[:, 0] / 1000.0             # km
    T2 = data2[:, 1] - 273.15             # °C
    p2 = data2[:, 2] / 1e6                 # MPa

    # --- load HYDROTHERMAL reference ---
    if os.path.exists(filename_HT):
        data3 = np.loadtxt(filename_HT, skiprows=1)
        x3 = data3[:, 0] / 1000.0             # km
        T3 = data3[:, 1]                       # °C
        p3 = data3[:, 2] / 10                  # MPa (bar to MPa)
    else:
        x3 = x2
        T3 = np.full_like(x2, np.nan)
        p3 = np.full_like(x2, np.nan)

    # --- interpolate reference onto our x for simple error metrics ---
    T3_on_x2 = _interp_to(x3, T3, x2)
    p3_on_x2 = _interp_to(x3, p3, x2)
    rmse_T, linf_T = _err_metrics(T3_on_x2, T2)
    rmse_p, linf_p = _err_metrics(p3_on_x2, p2)

    # --- figure & axes ---
    fig, axT = plt.subplots(figsize=(6.2, 4.2))
    axP = axT.twinx()

    # --- plot Temperature ---
    ln_T2, = axT.plot(
        x2, T2, linestyle=':', linewidth=2.0, marker='o', markersize=3.0,
        label=f'{label2} (ours)'
    )
    ln_T3, = axT.plot(
        x3, T3, linestyle='-.', linewidth=1.8, marker=None,
        label=f'{label3} – T'
    )

    # --- plot Pressure ---
    ln_p2, = axP.plot(
        x2, p2, linestyle=':', linewidth=2.0, marker='s', markersize=3.0,
        label=f'{label2} (ours) – p'
    )
    ln_p3, = axP.plot(
        x3, p3, linestyle='-.', linewidth=1.8, marker=None,
        label=f'{label3} – p'
    )

    # --- axis limits (union of both codes) with small padding ---
    xmin = min(np.nanmin(x2), np.nanmin(x3))
    xmax = max(np.nanmax(x2), np.nanmax(x3))
    def _pad(vmin, vmax, frac=0.04):
        if not np.isfinite(vmin) or not np.isfinite(vmax) or vmin == vmax:
            return vmin, vmax
        span = vmax - vmin
        return vmin - frac*span, vmax + frac*span

    T_min = np.nanmin([np.nanmin(T2), np.nanmin(T3)])
    T_max = np.nanmax([np.nanmax(T2), np.nanmax(T3)])
    P_min = np.nanmin([np.nanmin(p2), np.nanmin(p3)])
    P_max = np.nanmax([np.nanmax(p2), np.nanmax(p3)])

    axT.set_xlim(xmin, xmax)
    axT.set_ylim(*_pad(T_min, T_max))
    axP.set_ylim(*_pad(P_min, P_max))

    # --- ticks & grids ---
    axT.xaxis.set_major_locator(MultipleLocator(1))
    axT.xaxis.set_minor_locator(MultipleLocator(0.2))
    axT.yaxis.set_major_locator(MultipleLocator(50))
    axT.yaxis.set_minor_locator(MultipleLocator(10))
    axP.yaxis.set_major_locator(MultipleLocator(5))
    axP.yaxis.set_minor_locator(MultipleLocator(1))

    axT.grid(True, which='major', alpha=0.35, linestyle='-')
    axT.grid(True, which='minor', alpha=0.15, linestyle=':')

    # --- labels ---
    axT.set_xlabel('Distance (km)')
    axT.set_ylabel('Temperature ($^{\\circ}$C)', color=ln_T2.get_color())
    axP.set_ylabel('Pressure (MPa)', color=ln_p2.get_color())

    axT.tick_params(axis='y', which='both', colors=ln_T2.get_color())
    axP.tick_params(axis='y', which='both', colors=ln_p2.get_color())

    # --- legend (combine both axes) ---
    lines = [ln_T2, ln_T3, ln_p2, ln_p3]
    labels = [l.get_label() for l in lines]
    leg = axT.legend(lines, labels, loc='best', frameon=True, fontsize=9)
    leg.get_frame().set_alpha(0.9)

    # --- title with basic error metrics ---
    title = (f'1-D benchmark @ time={time_str}\n'
             f'T: RMSE={rmse_T:.3g} °C, L∞={linf_T:.3g} °C    '
             f'p: RMSE={rmse_p:.3g} MPa, L∞={linf_p:.3g} MPa')
    axT.set_title(title, fontsize=11)

    plt.tight_layout()

    # --- save & (on macOS) open PDF ---
    plt.savefig('results.pdf', bbox_inches='tight')
    plt.savefig('results.png', dpi=300, bbox_inches='tight')
    try:
        os.system('open results.pdf')  # macOS; harmless elsewhere
    except Exception:
        pass
    # plt.show()

def main(argv):
    if len(argv) != 2:
        usage(argv)
        return 0
    plot_1d(argv[1])
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
