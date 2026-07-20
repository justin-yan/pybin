import os
from pathlib import Path
from time import perf_counter

import pytest

from pybin.buildlib import build_wheels_from_config
from pybin.config import load_config
from pybin.sync import sync

pytestmark = pytest.mark.integration
PROJECT_DIRECTORY = Path(__file__).parents[2]
TOOLS_DIRECTORY = PROJECT_DIRECTORY / "tools"
RULES_DIRECTORY = PROJECT_DIRECTORY / "rules"


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
    monkeypatch.chdir(new_root)
    new_start = perf_counter()
    sync(RULES_DIRECTORY / config_path.name)
    new_elapsed = perf_counter() - new_start
    print(f"\n{config.name}: buildlib={legacy_elapsed:.3f}s sync={new_elapsed:.3f}s")
    if output_directory:
        print(f"output: {compatibility_root}")

    legacy_files = {path.relative_to(legacy_distribution): path.read_bytes() for path in legacy_distribution.rglob("*") if path.is_file()}
    new_files = {path.relative_to(new_distribution): path.read_bytes() for path in new_distribution.rglob("*") if path.is_file()}
    if new_files.keys() != legacy_files.keys():
        pytest.fail(f"Distribution files differ: new={sorted(new_files)}, legacy={sorted(legacy_files)}")
    for path, content in new_files.items():
        if content != legacy_files[path]:
            pytest.fail(f"Distribution file differs: {path}")
