#!/usr/bin/env python3
"""Compare and plot final pressure/temperature profiles for h1-h3 or v1-v3."""
import argparse
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
TIMES = {'h1': 7884000000, 'h2': 3786912000, 'h3': 47336400000,
         'v1': 23668200000, 'v2': 11045160000, 'v3': 47336400000}
REFERENCES = {'h1': 'h1_T_p_250.0.txt', 'h2': 'h2_T_p_120.0.txt',
              'h3': 'h3_T_p_1500.0.txt', 'v1': 'reference.csv',
              'v2': 'reference.csv', 'v3': 'reference.csv'}


def profile(path):
    data = np.loadtxt(path, comments='#', ndmin=2)
    if data.shape[1] != 3 or len(data) < 2 or not np.isfinite(data).all():
        raise ValueError(f'{path}: expected finite coordinate[m], T[K], p[Pa] rows')
    if not (np.diff(data[:, 0]) > 0).all():
        raise ValueError(f'{path}: coordinates must increase strictly')
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', choices=TIMES, required=True)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--run', type=Path, help='run directory produced by run.py')
    source.add_argument('--sample', type=Path, help='explicit coordinate/T/p sample file')
    parser.add_argument('--output', type=Path, required=True, help='new directory for comparison.png/pdf, profiles.csv and metrics.json')
    parser.add_argument('--time', help='seconds; must match the final reference time')
    parser.add_argument('--reference', type=Path, help='override using the same format as the selected case reference')
    args = parser.parse_args()
    try:
        time = Decimal(args.time or str(TIMES[args.case]))
        if not time.is_finite() or time != TIMES[args.case]:
            raise ValueError(f'{args.case}: reference is only available at {TIMES[args.case]} s')
        if args.sample:
            sample = args.sample
        else:
            case = args.run/'case' if (args.run/'case/system').is_dir() else args.run
            directory = case/'postProcessing/linesample'/str(TIMES[args.case])
            candidates = [directory/name for name in ('data.xy', 'data_T_p.xy') if (directory/name).is_file()]
            if len(candidates) != 1:
                raise ValueError(f'{directory}: expected one data.xy or data_T_p.xy')
            sample = candidates[0]
        reference = args.reference or ROOT/'USGS_HYDROTHERMAL/1d'/args.case/REFERENCES[args.case]
        solver = profile(sample)
        vertical = args.case.startswith('v')
        if vertical:
            ref = np.genfromtxt(reference, delimiter=',', names=True)
            x, refT, refP = ref['height_m'], ref['T_C'], ref['p_MPa']
        else:
            ref = profile(reference)
            x, refT, refP = ref[:, 0], ref[:, 1], ref[:, 2]/10
        if len(x) != 200 or not np.isfinite(np.r_[x, refT, refP]).all() or not (np.diff(x) > 0).all():
            raise ValueError('Expected complete finite reference at 200 increasing coordinates')
        if solver[0, 0] > x[0] or solver[-1, 0] < x[-1]:
            raise ValueError('Solver profile must cover every reference location; no extrapolation')
        # Retain the existing operation order, including the vertical workflow's
        # interpolation-before-unit-conversion and horizontal workflow's inverse.
        if vertical:
            T = np.interp(x, solver[:, 0], solver[:, 1])-273.15
            P = np.interp(x, solver[:, 0], solver[:, 2])/1e6
        else:
            solver[:, 1] -= 273.15
            solver[:, 2] /= 1e6
            T = np.interp(x, solver[:, 0], solver[:, 1])
            P = np.interp(x, solver[:, 0], solver[:, 2])
        metrics = {}
        interior = {}
        for quantity, predicted, expected in [('temperature_C', T, refT), ('pressure_MPa', P, refP)]:
            difference = predicted-expected
            metrics[quantity] = dict(rmse=float(np.sqrt(np.mean(difference**2))),
                                     max_abs=float(np.max(np.abs(difference))))
            if args.case != 'h1':
                metrics[quantity]['max_abs_at_m'] = float(x[np.argmax(np.abs(difference))])
            if vertical:
                d = difference[(x > 5) & (x < 1995)]
                interior[quantity] = dict(rmse=float(np.sqrt(np.mean(d**2))),
                                          max_abs=float(abs(d).max()))
    except (OSError, ValueError, InvalidOperation) as error:
        parser.exit(1, f'Comparison failed: {error}\n')
    args.output.mkdir(parents=True, exist_ok=False)
    fig, axes = plt.subplots(2, 1, figsize=(7, 6), sharex=not vertical)
    for ax, data, expected, quantity, label in [(axes[0], T, refT, 'temperature_C', 'Temperature (C)'),
                                                (axes[1], P, refP, 'pressure_MPa', 'Pressure (MPa)')]:
        if vertical:
            ax.plot(expected, x/1000, label='HYDROTHERM')
            ax.plot(data, x/1000, '--', label='HTFoam')
            ax.set(xlabel=label, ylabel='Height (km)')
        else:
            ax.plot(x/1000, expected, label='HYDROTHERM')
            ax.plot(x/1000, data, '--', label='HTFoam')
            ax.set(xlabel='Distance (km)', ylabel=label)
        error = metrics[quantity]
        ax.set_title(f"RMSE={error['rmse']:.5g}; max |error|={error['max_abs']:.5g}")
        ax.grid(alpha=.3)
        ax.legend()
    fig.suptitle(f'{args.case}: {TIMES[args.case]} s')
    fig.tight_layout()
    for suffix in ('png', 'pdf'):
        fig.savefig(args.output/f'comparison.{suffix}', dpi=180)
    plt.close(fig)
    np.savetxt(args.output/'profiles.csv', np.column_stack((x, refT, T, refP, P)), delimiter=',',
               header='coordinate_m,reference_T_C,HTFoam_T_C,reference_p_MPa,HTFoam_p_MPa', comments='')
    report = dict(case=args.case, time_seconds=str(time), sample=str(sample.resolve()),
                  reference=str(reference.resolve()), reference_points=len(x), metrics=metrics,
                  acceptance_thresholds=None)
    if vertical:
        report['interior_metrics'] = interior
    (args.output/'metrics.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
