#!/usr/bin/env python3
"""Plot canonical 2D pressure/temperature against the frozen HYDROTHERM fields."""
import argparse
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
try:
    from ._fields import YEAR, numeric_field, centres, bilinear, measures, case_directory, horizontal_mass_flux
except ImportError:
    from _fields import YEAR, numeric_field, centres, bilinear, measures, case_directory, horizontal_mass_flux

ROOT = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', choices=('2d', '2d-layered'), default='2d')
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--time', type=int, default=50000, help='Julian years; layered comparisons also permit shorter times')
    parser.add_argument('--reference', type=Path, help='same format as the frozen reference CSV')
    parser.add_argument('--output', type=Path, required=True, help='new directory for comparison.png/pdf, profiles.csv and metrics.json')
    parser.add_argument('--interface-reference', type=Path, help='layered only: true HY face CSV with x_m,j_up_kg_m2_s; never nodal plot vectors')
    args = parser.parse_args()
    if args.interface_reference and args.case != '2d-layered':
        parser.error('--interface-reference requires --case 2d-layered')
    layered = args.case == '2d-layered'
    if args.time <= 0 or (not layered and args.time not in (5000, 15000, 50000)):
        parser.error('Use a positive year for layered checks, or 5000/15000/50000 for the homogeneous case')
    reference = args.reference or ROOT/(f'USGS_HYDROTHERMAL/2d/layered/reference-{args.time}yr.csv'
                                      if layered else f'USGS_HYDROTHERMAL/2d/reference-{args.time}yr.csv')
    if layered and not reference.is_file():
        parser.error('No qualified layered reference exists yet; supply an explicit --reference for comparison')
    case = case_directory(args.run)
    xyz = centres(case)
    order = np.lexsort((xyz[:, 0], xyz[:, 1]))
    x, y = np.unique(xyz[:, 0]), np.unique(xyz[:, 1])
    folder = case/str(args.time*YEAR)
    T = numeric_field(folder/'T')[order].reshape(len(y), len(x))-273.15
    P = numeric_field(folder/'p')[order].reshape(len(y), len(x))/1e6
    ref = np.genfromtxt(reference, delimiter=',', names=True)
    qx, qy = ref['x_m'], ref['OpenFOAM_y_m']
    if layered:
        assert len(ref) == len(x)*len(y)
        assert len(np.unique(ref['i'])) == len(x) and len(np.unique(ref['k'])) == len(y)
        assert np.array_equal(np.unique(qx), x) and np.array_equal(np.unique(qy), y)
        assert 'ibc' in ref.dtype.names, 'Layered references must retain native boundary flags'
        assert (ref['ibc'][ref['k'] == ref['k'].max()] == 10).all(), 'Expected an IBC=10 open top'
        # IBC=10 leaves temperature free at the top node. Use native centres;
        # never append a fictitious fixed-temperature plane or omit that row.
    else:
        assert len(ref) == 2700 and len(np.unique(ref['i'])) == 90 and len(np.unique(ref['k'])) == 30
    Ti, Pi = bilinear(x, y, T, qx, qy), bilinear(x, y, P, qx, qy)
    assert np.isfinite(np.r_[Ti, Pi, ref['T_C'], ref['p_MPa']]).all()
    # Original comparison masks and interpolation, with no pressure correction.
    fixed = ref['k'] == ref['k'].max() if layered else (ref['k'] == 30) & (ref['i'] >= 2) & (ref['i'] <= 89)
    assert fixed.sum() == (len(x) if layered else 88)
    regions = [('all_nodes', np.ones(len(ref), bool)),
               ('interior_below_300m', qy < -300), ('top_nodes', fixed)] if layered else [
               ('all_nodes', np.ones(len(ref), bool)), ('free_nodes', ~fixed), ('fixed_top_nodes', fixed)]
    results = {}
    for name, mask in regions:
        results[name] = dict(temperature_C=measures(Ti, ref['T_C'], mask),
                             pressure_MPa=measures(Pi, ref['p_MPa'], mask))
    for name, mask in regions[:2]:
        for quantity, data, expected in [('temperature_C', Ti, ref['T_C']), ('pressure_MPa', Pi, ref['p_MPa'])]:
            indices = np.flatnonzero(mask)
            index = indices[np.argmax(abs((data-expected)[mask]))]
            results[name][quantity]['max_error_node'] = [int(ref['i'][index]), int(ref['k'][index])]
    args.output.mkdir(parents=True, exist_ok=False)
    fig, axes = plt.subplots(2, 3, figsize=(15, 8), constrained_layout=True)
    px, py = np.unique(qx)/1000-4.5, (np.unique(ref['z_m'])-3000)/1000
    reference_shape = (len(np.unique(qy)), len(np.unique(qx)))
    for row, (expected, actual, label) in enumerate([(ref['T_C'], Ti, 'Temperature (C)'), (ref['p_MPa'], Pi, 'Pressure (MPa)')]):
        difference = actual-expected
        fields = [expected, actual, difference]
        vmin, vmax = min(expected.min(), actual.min()), max(expected.max(), actual.max())
        for col, (data, title) in enumerate(zip(fields, ('HYDROTHERM', 'HTFoam', 'HTFoam minus HYDROTHERM'))):
            ax = axes[row, col]
            if col == 2:
                bound = max(abs(difference).max(), 1e-12)
                image = ax.pcolormesh(px, py, data.reshape(reference_shape), shading='nearest', cmap='RdBu_r', vmin=-bound, vmax=bound)
            else:
                image = ax.pcolormesh(px, py, data.reshape(reference_shape), shading='nearest', cmap='viridis', vmin=vmin, vmax=vmax)
            fig.colorbar(image, ax=ax, label=label)
            ax.set(title=title, xlabel='Distance from centre (km)', ylabel='y (km)', aspect='equal')
            if layered:
                ax.set_ylim(-3, 0)
    title = 'Layered 2D convection' if layered else 'Original-top 2D convection'
    fig.suptitle(f'{title}: {args.time} years; absolute pressure, unchanged coordinates')
    for suffix in ('png', 'pdf'):
        fig.savefig(args.output/f'comparison.{suffix}', dpi=180)
    plt.close(fig)
    np.savetxt(args.output/'profiles.csv', np.column_stack((ref['i'], ref['k'], qx, qy, ref['T_C'], Ti, ref['p_MPa'], Pi)),
               delimiter=',', header='i,k,x_m,y_m,reference_T_C,HTFoam_T_C,reference_p_MPa,HTFoam_p_MPa', comments='')
    if args.interface_reference:
        rx = np.genfromtxt(args.interface_reference, delimiter=',', names=True)
        fx, flux, area = horizontal_mass_flux(case, folder)
        if not np.array_equal(rx['x_m'], fx) or not np.isfinite(rx['j_up_kg_m2_s']).all():
            raise ValueError('Reference must contain finite fluxes at the identical physical faces')
        expected = rx['j_up_kg_m2_s']
        results['permeability_interface'] = dict(
            elevation_m=-1100, upward_flux_kg_m2_s=measures(flux, expected, np.ones(len(fx),bool)),
            HT_gross_up_kg_s=float((np.maximum(flux,0)*area).sum()),
            HY_gross_up_kg_s=float((np.maximum(expected,0)*area).sum()),
            HT_gross_down_kg_s=float((-np.minimum(flux,0)*area).sum()),
            HY_gross_down_kg_s=float((-np.minimum(expected,0)*area).sum()),
            HT_net_up_kg_s=float((flux*area).sum()), HY_net_up_kg_s=float((expected*area).sum()),
            definition='Actual face flux; signed upward; rates per 1 m model thickness. HY precision/provenance belongs to supplied reference.')
        np.savetxt(args.output/'interface.csv', np.column_stack((fx,flux,expected)), delimiter=',',
                   header='x_m,HT_j_up_kg_m2_s,HY_j_up_kg_m2_s', comments='')
        fig, ax = plt.subplots(figsize=(8,3), constrained_layout=True)
        ax.plot(fx,expected,label='HYDROTHERM face'); ax.plot(fx,flux,'--',label='HTFoam phi/area')
        ax.set(xlabel='x (m)',ylabel='Upward mass flux (kg/m2/s)',title=f'Permeability interface y=-1100 m, {args.time} yr')
        ax.legend(); fig.savefig(args.output/'interface.png',dpi=160); plt.close(fig)
    report = dict(time_years=args.time, reference=str(reference.resolve()), metrics=results, acceptance_thresholds=None)
    (args.output/'metrics.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
