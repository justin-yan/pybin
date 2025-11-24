import re
import urllib.request
import json
from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path


projects_dir = Path(__file__).parent


def project_list() -> list[Path]:
    return [
        p for p in projects_dir.iterdir() if p.is_dir() and (p / "build.py").exists()
    ]


def extract_version(tag: str) -> str:
    # Look for MAJOR.MINOR.PATCH without prerelease/build metadata
    # \d+\.\d+\.\d+ - capture the three numeric segments
    match = re.search(r'\d+\.\d+\.\d+', tag)
    if match:
        return match.group(0)
    raise ValueError(f"Could not extract MAJOR.MINOR.PATCH from tag: {tag!r}")


def get_latest_version(upstream_url: str) -> str:
    repo, name = upstream_url.split("/")[-2:]
    with urllib.request.urlopen(
        f"https://api.github.com/repos/{repo}/{name}/releases/latest"
    ) as response:
        data = response.read().decode("utf-8")
        tag = json.loads(data)["tag_name"]
        return extract_version(tag)


def import_module_from_path(path: Path):
    # Ensure the path is absolute
    path = path.resolve()
    # Create a module spec
    spec = spec_from_file_location("toolpkg", path)
    if spec is None:
        raise ImportError(f"Cannot load module toolpkg from path {path}")
    # Create a new module based on the spec
    module = module_from_spec(spec)
    # Execute the module
    spec.loader.exec_module(module)
    return module


def main():
    for project in project_list():
        build_file = project / "build.py"

        try:
            m = import_module_from_path(build_file)
            UPSTREAM_REPO = m.UPSTREAM_REPO
            VERSION = m.VERSION
        except IndexError:
            print(f"Skipping {project.name}")
            continue

        latest_tag = get_latest_version(UPSTREAM_REPO)

        if latest_tag == VERSION:
            print(f"{project.name} is already up to date")
            continue

        new_content = build_file.read_text().replace(VERSION, latest_tag)
        build_file.write_text(new_content)
        print(f"{project.name} {VERSION} -> {latest_tag}")


if __name__ == "__main__":
    main()
