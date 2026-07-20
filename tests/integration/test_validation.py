import subprocess
import sys
from pathlib import Path
from platform import machine

import pytest

from pybin.sync import sync

pytestmark = pytest.mark.integration
PROJECT_DIRECTORY = Path(__file__).parents[2]
RULES_DIRECTORY = PROJECT_DIRECTORY / "rules"


@pytest.mark.parametrize("rule_path", sorted(RULES_DIRECTORY.glob("*.yaml")), ids=lambda path: path.stem)
def test_rule_builds_installable_wheels(
    rule_path: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    sync(rule_path)

    wheels = sorted(tmp_path.glob("*-dist/*.whl"))
    assert wheels
    for wheel in wheels:
        assert wheel.stat().st_size >= 500_000, f"{wheel.name} does not contain a substantial binary payload"

    linux_x86_wheels = [wheel for wheel in wheels if "manylinux2014_x86_64" in wheel.name]
    assert len(linux_x86_wheels) == 1
    if sys.platform != "linux" or machine() != "x86_64":
        return

    environment = tmp_path / "environment"
    subprocess.run(["uv", "venv", "--python", sys.executable, environment], check=True, capture_output=True, text=True)
    subprocess.run(
        ["uv", "pip", "install", "--python", environment / "bin/python", linux_x86_wheels[0]],
        check=True,
        capture_output=True,
        text=True,
    )
