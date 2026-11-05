"""Driver preflight and preparation checks; no OpenFOAM build or run required.

From benchmarks/HTFoam: poetry run python -m unittest discover -s tests -v
"""
import hashlib
import json
import os
import re
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class RunDriverTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='htfoam-driver-test-')
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.environment = os.environ.copy()
        for name in ('HTFOAM_SOLVER', 'HTFOAM_LIBRARY'):
            self.environment.pop(name, None)
        self.environment['PYTHONDONTWRITEBYTECODE'] = '1'

    def driver(self, *arguments):
        return subprocess.run(
            [sys.executable, str(ROOT/'run.py'), *map(str, arguments)],
            env=self.environment, capture_output=True, text=True,
        )

    def snapshot(self, directory):
        return {str(p.relative_to(directory)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in directory.rglob('*') if p.is_file()}

    def test_missing_solver_creates_no_output_or_parent(self):
        library = self.directory/'library.so'
        library.write_text('Preflight fixture; never loaded.\n')
        output = self.directory/'new-parent/run'
        result = self.driver('--case', 'h1', '--output', output,
                             '--solver', self.directory/'missing-solver',
                             '--library', library)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn('Provide a built --solver', result.stderr)
        self.assertFalse(output.parent.exists())

    def test_missing_library_creates_no_output_or_parent(self):
        output = self.directory/'new-parent/run'
        result = self.driver('--case', 'h1', '--output', output,
                             '--solver', sys.executable,
                             '--library', self.directory/'missing-library.so')
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn('Provide a built --solver', result.stderr)
        self.assertFalse(output.parent.exists())

    def test_all_seven_cases_prepare_without_runtime_dependencies(self):
        for name in ('h1', 'h2', 'h3', 'v1', 'v2', 'v3', '2d'):
            with self.subTest(case=name):
                output = self.directory/name
                result = self.driver('--case', name, '--output', output,
                                     '--prepare-only', '--solver', self.directory/'missing')
                self.assertEqual(result.returncode, 0, result.stderr)
                metadata = json.loads((output/'run.json').read_text())
                self.assertEqual(metadata['case'], name)
                self.assertEqual(metadata['completed_phases'], [])
                self.assertTrue((output/'case/0/T').is_file())
                self.assertTrue((output/'case/0/p').is_file())
                self.assertTrue((output/'case/system/blockMeshDict').is_file())

    def test_prepared_case_can_resume_and_failed_preflight_preserves_it(self):
        output = self.directory/'prepared'
        arguments = ('--case', 'h1', '--output', output,
                     '--solver', self.directory/'missing-solver')
        result = self.driver(*arguments, '--prepare-only')
        self.assertEqual(result.returncode, 0, result.stderr)
        before = self.snapshot(output)
        result = self.driver(*arguments, '--prepare-only', '--resume')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.snapshot(output), before)
        result = self.driver(*arguments, '--resume',
                             '--library', self.directory/'missing-library.so')
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(self.snapshot(output), before)

    def test_layered_grids_and_resume(self):
        for variant in ('coarse', 'fine'):
            output = self.directory/variant
            arguments = ('--case', '2d-layered', '--output', output,
                         '--prepare-only') + (('--refine',) if variant == 'fine' else ())
            result = self.driver(*arguments)
            self.assertEqual(result.returncode, 0, result.stderr)
            metadata = json.loads((output/'run.json').read_text())
            self.assertEqual(metadata['refine'], variant == 'fine')
            self.assertEqual(metadata['full_end_seconds'], 5000*31557600)
            self.assertTrue((output/'reference.input').is_file())
            nx, nz = (180, 60) if variant == 'fine' else (90, 30)
            mesh = (output/'case/system/blockMeshDict').read_text()
            self.assertIn(f'({nx} {nz} 1)', mesh)
            permeability = (output/'case/0/permeability').read_text().split('internalField',1)[1].split('boundaryField',1)[0]
            self.assertEqual(permeability.count('1e-15'), nx*19*(2 if variant == 'fine' else 1))
            self.assertEqual(permeability.count('1e-14'), nx*11*(2 if variant == 'fine' else 1))
            temperature = (output/'case/0/T').read_text()
            q = re.search(r'q nonuniform List<scalar> \d+\s*\(([^)]+)\)', temperature)[1]
            values = list(map(float,q.split()))
            self.assertEqual(len(values), nx)
            self.assertAlmostEqual(sum(values)*9000/nx, 5390)
            self.assertFalse((output/'case/0/kr').exists())
            reference = (output/'reference.input').read_text()
            self.assertIn(f'{nx}     1     {nz}', reference)
            if variant == 'fine':
                self.assertIn('TEMPERATURE (C)\nFREE_FORMAT\nBOTTOM\n', reference)
                self.assertIn('302.4873100744045', reference)

            before = self.snapshot(output)
            result = self.driver(*arguments, '--resume')
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(self.snapshot(output), before)
            other = ('--refine',) if variant == 'coarse' else ()
            result = self.driver('--case', '2d-layered', '--output', output,
                                 '--prepare-only', '--resume', *other)
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertEqual(self.snapshot(output), before)

    def test_layered_cannot_extend_past_5kyr(self):
        for year in (15000, 50000):
            output = self.directory/str(year)
            result = self.driver('--case', '2d-layered', '--output', output,
                                 '--prepare-only', '--until-year', year)
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertFalse(output.exists())


if __name__ == '__main__':
    unittest.main()
