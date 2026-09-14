"""Copy rendered notebooks beside their HTML pages and check every Colab target."""

import argparse
import json
import re
import shutil
from pathlib import Path

COLAB_PREFIX = "https://colab.research.google.com/github/RobinL/splink/blob/docs-notebooks/"
COLAB_LINK = re.compile(r'https://colab\.research\.google\.com/github/[^\s"<>\)]+')


def package_notebooks(docs_dir: Path, site_dir: Path) -> int:
    notebooks = list(docs_dir.rglob("*.ipynb"))
    if not notebooks:
        raise ValueError("No rendered notebooks found; render notebooks before packaging")

    # A partial render must not publish a site with broken notebook links.
    for source in (docs_dir / "demos").rglob("*.nb.py"):
        rendered = source.with_name(source.name.removesuffix(".nb.py") + ".ipynb")
        if not rendered.is_file():
            raise ValueError(f"Missing rendered notebook: {rendered}")

    targets = {path.relative_to(docs_dir).as_posix() for path in notebooks}
    # Check both authoring sources and the actual HTML to catch stale generated links.
    for root, suffixes in ((docs_dir / "demos", {".py", ".md", ".ipynb"}), (site_dir, {".html"})):
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix not in suffixes:
                continue
            content = path.read_text()
            if path.suffix == ".ipynb":
                notebook = json.loads(content)
                content = "\n".join("".join(cell["source"]) for cell in notebook["cells"])
            for link in COLAB_LINK.findall(content):
                if not link.startswith(COLAB_PREFIX):
                    raise ValueError(f"Unexpected Colab repository or branch in {path}: {link}")
                target = link.removeprefix(COLAB_PREFIX).split("#", 1)[0].split("?", 1)[0]
                if target not in targets:
                    raise ValueError(f"Missing Colab target in {path}: {target}")

    for notebook in notebooks:
        destination = site_dir / notebook.relative_to(docs_dir)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(notebook, destination)
    return len(notebooks)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--docs-dir", type=Path, default=Path("docs"))
    parser.add_argument("--site-dir", type=Path, default=Path("site"))
    args = parser.parse_args()
    count = package_notebooks(args.docs_dir, args.site_dir)
    print(f"Packaged {count} notebooks with the documentation")
