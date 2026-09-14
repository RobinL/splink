import json
import tempfile
import unittest
from pathlib import Path

from package_notebooks import COLAB_PREFIX, package_notebooks


class PackageNotebooksTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.docs = Path(self.temp.name) / "docs"
        self.site = Path(self.temp.name) / "site"
        (self.docs / "demos").mkdir(parents=True)
        (self.site / "demos").mkdir(parents=True)
        self.link = COLAB_PREFIX + "demos/example.ipynb"
        self.notebook = self.docs / "demos/example.ipynb"
        self.notebook.write_text(json.dumps({"cells": [{"source": [f'<a href="{self.link}">Colab</a>']}]}))
        (self.docs / "demos/example.nb.py").write_text(f'# <a href="{self.link}">Colab</a>')
        (self.site / "demos/example.html").write_text(f'<a href="{self.link}">Colab</a>')

    def test_preserves_notebook_bytes_and_html(self):
        html = (self.site / "demos/example.html").read_bytes()
        self.assertEqual(package_notebooks(self.docs, self.site), 1)
        self.assertEqual((self.site / "demos/example.ipynb").read_bytes(), self.notebook.read_bytes())
        self.assertEqual((self.site / "demos/example.html").read_bytes(), html)

    def test_rejects_partial_render(self):
        (self.docs / "demos/missing.nb.py").touch()
        with self.assertRaisesRegex(ValueError, "Missing rendered notebook"):
            package_notebooks(self.docs, self.site)

    def test_rejects_wrong_filename_in_built_page(self):
        (self.site / "index.html").write_text(f'<a href="{COLAB_PREFIX}demos/missing.ipynb">Colab</a>')
        with self.assertRaisesRegex(ValueError, "Missing Colab target"):
            package_notebooks(self.docs, self.site)

    def test_rejects_stale_branch_in_notebook(self):
        self.notebook.write_text(self.notebook.read_text().replace("docs-notebooks/", "master/"))
        with self.assertRaisesRegex(ValueError, "Unexpected Colab repository or branch"):
            package_notebooks(self.docs, self.site)

    def test_rejects_empty_build(self):
        self.notebook.unlink()
        with self.assertRaisesRegex(ValueError, "No rendered notebooks"):
            package_notebooks(self.docs, self.site)


if __name__ == "__main__":
    unittest.main()
