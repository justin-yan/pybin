import os
from pathlib import Path
from time import perf_counter

import pytest

from pybin.buildlib import build_wheels_from_config
from pybin.config import load_config
from pybin.registry.github import GithubReleasePuller
from pybin.registry.pypi import PyPIReleasePusher

pytestmark = pytest.mark.integration
TOOLS_DIRECTORY = Path(__file__).parents[2] / "tools"


@pytest.mark.parametrize("config_path", sorted(TOOLS_DIRECTORY.glob("*.yaml")), ids=lambda path: path.stem)
def test_distribution_matches_buildlib(config_path: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SOURCE_DATE_EPOCH", "1701388800")
    config = load_config(config_path)
    output_directory = os.environ.get("PYBIN_COMPATIBILITY_OUTPUT_DIRECTORY")
    compatibility_root = Path(output_directory).resolve() / f"{config.name}-compatibility" if output_directory else tmp_path

    legacy_root = compatibility_root / "before"
    legacy_root.mkdir(parents=True, exist_ok=True)
    monkeypatch.chdir(legacy_root)
    legacy_start = perf_counter()
    build_wheels_from_config(config)
    legacy_elapsed = perf_counter() - legacy_start
    legacy_distribution = legacy_root / f"{config.name}-dist"

    new_root = compatibility_root / "after"
    new_root.mkdir(parents=True, exist_ok=True)
    new_distribution = new_root / f"{config.name}-dist"
    repository = config.upstream_repo.removeprefix("https://github.com/")
    release_slug = config.url_template.removeprefix("{repo}/releases/download/")
    if config.name == "codex":
        release_slug = release_slug.removesuffix(".tar.gz") + ".zst"
    new_start = perf_counter()
    release = GithubReleasePuller(
        repository=repository,
        version=config.version,
        release_slug=release_slug,
        targets=list(config.targets),
        bin_name=config.name,
    )()
    PyPIReleasePusher(output_directory=new_distribution)(release)
    new_elapsed = perf_counter() - new_start
    print(f"\n{config.name}: buildlib={legacy_elapsed:.3f}s github+pypi={new_elapsed:.3f}s")
    if output_directory:
        print(f"output: {compatibility_root}")

    legacy_files = {path.relative_to(legacy_distribution): path.read_bytes() for path in legacy_distribution.rglob("*") if path.is_file()}
    new_files = {path.relative_to(new_distribution): path.read_bytes() for path in new_distribution.rglob("*") if path.is_file()}
    if new_files.keys() != legacy_files.keys():
        pytest.fail(f"Distribution files differ: new={sorted(new_files)}, legacy={sorted(legacy_files)}")
    for path, content in new_files.items():
        if content != legacy_files[path]:
            pytest.fail(f"Distribution file differs: {path}")
