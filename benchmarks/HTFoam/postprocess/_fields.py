"""Existing structured 2D field readers and interpolation; no formula changes."""
from pathlib import Path
import re
import numpy as np
YEAR = 31557600

def numeric_field(path):
    s = path.read_text()
    m = re.search('internalField\\s+uniform\\s+([^;]+);', s)
    if m:
        return np.fromstring(m[1].replace('(', '').replace(')', ''), sep=' ')
    m = re.search('internalField\\s+nonuniform\\s+List<\\w+>\\s+\\d+\\s*\\((.*?)\\)\\s*;', s, re.S)
    return np.fromstring(m[1].replace('(', '').replace(')', ''), sep=' ')

def mesh_points(case):
    return np.array(re.findall('\\(\\s*([\\deE+.-]+)\\s+([\\deE+.-]+)\\s+([\\deE+.-]+)\\s*\\)', (case / 'constant/polyMesh/points').read_text()), float)

def faces(case):
    return [list(map(int, m.split())) for m in re.findall('\\d+\\(([^()]*)\\)', (case / 'constant/polyMesh/faces').read_text())]

def labels(path):
    return np.fromstring(re.search('\\n\\s*\\d+\\s*\\n?\\(\\s*([\\s\\d]+)\\s*\\)', path.read_text())[1], dtype=int, sep=' ')

def centres(case):
    pts = mesh_points(case)
    f = faces(case)
    own = labels(case / 'constant/polyMesh/owner')
    nei = labels(case / 'constant/polyMesh/neighbour')
    cell_count = int(max(own.max(), nei.max(initial=-1))) + 1
    vertices = [set() for _ in range(cell_count)]
    for i, indices in enumerate(f):
        vertices[own[i]].update(indices)
        if i < len(nei):
            vertices[nei[i]].update(indices)
    return np.array([pts[list(v)].mean(axis=0) for v in vertices])

def bilinear(x, y, values, qx, qy):
    assert qx.min() >= x.min() and qx.max() <= x.max() and (qy.min() >= y.min()) and (qy.max() <= y.max()), 'No extrapolation permitted'
    ix = np.clip(np.searchsorted(x, qx, side='right') - 1, 0, len(x) - 2)
    iy = np.clip(np.searchsorted(y, qy, side='right') - 1, 0, len(y) - 2)
    tx = (qx - x[ix]) / (x[ix + 1] - x[ix])
    ty = (qy - y[iy]) / (y[iy + 1] - y[iy])
    return (1 - ty) * ((1 - tx) * values[iy, ix] + tx * values[iy, ix + 1]) + ty * ((1 - tx) * values[iy + 1, ix] + tx * values[iy + 1, ix + 1])

def measures(a, b, mask):
    d = (a - b)[mask]
    return dict(nodes=int(mask.sum()), rms=float(np.sqrt(np.mean(d * d))), max_abs=float(abs(d).max()), mean_signed=float(d.mean()))

def case_directory(run):
    run = Path(run)
    return run / 'case' if (run / 'case/system').is_dir() else run


def horizontal_mass_flux(case, folder, elevation=-1100):
    """Actual internal phi faces, upward kg/(m2 s), with geometric face areas."""
    xyz = centres(case)
    points = mesh_points(case)
    topology = faces(case)
    own = labels(case/'constant/polyMesh/owner')
    nei = labels(case/'constant/polyMesh/neighbour')
    cf = np.array([points[indices].mean(axis=0) for indices in topology[:len(nei)]])
    selected = np.flatnonzero(np.isclose(cf[:, 1], elevation, rtol=0, atol=1e-8))
    selected = selected[np.argsort(cf[selected, 0])]
    if not len(selected) or not np.all(xyz[own[selected], 1] != xyz[nei[selected], 1]):
        raise ValueError('Expected internal horizontal faces at the permeability interface')
    areas = []
    for index in selected:
        vertices = points[topology[index]]
        area = .5*np.linalg.norm(np.cross(vertices, np.roll(vertices, -1, axis=0)).sum(axis=0))
        areas.append(area)
    areas = np.array(areas)
    phi = numeric_field(folder/'phi')
    phi = np.full(len(nei), phi[0]) if len(phi) == 1 else phi
    sign = np.sign(xyz[nei[selected], 1]-xyz[own[selected], 1])
    return cf[selected, 0], phi[selected]*sign/areas, areas
