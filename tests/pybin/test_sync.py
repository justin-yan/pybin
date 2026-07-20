from pathlib import Path

import pytest
import yaml

from pybin.registry.github import GithubReleasePuller
from pybin.registry.pypi import PyPIReleasePusher
from pybin.sync import parse_sync_rule
from pybin.types import SyncRule

PROJECT_DIRECTORY = Path(__file__).parents[2]
INVALID_RULES_DIRECTORY = PROJECT_DIRECTORY / "tests" / "fixtures" / "sync"


def test_parse_sync_rule() -> None:
    config = yaml.safe_load((PROJECT_DIRECTORY / "rules" / "codex.yaml").read_text())

    assert parse_sync_rule(config) == SyncRule(
        source=GithubReleasePuller(
            repository="openai/codex",
            version="0.144.1",
            release_slug="rust-v{version}/{name}-{target}.zst",
            targets=[
                "aarch64-apple-darwin",
                "x86_64-apple-darwin",
                "aarch64-unknown-linux-musl",
                "x86_64-unknown-linux-musl",
            ],
        ),
        targets=[PyPIReleasePusher(upstream_url="https://github.com/openai/codex")],
    )


@pytest.mark.parametrize(
    ("filename", "error"),
    [
        ("unknown_source.yaml", "Unknown source"),
        ("unknown_target.yaml", "Unknown target"),
    ],
)
def test_parse_sync_rule_rejects_invalid_rule(filename: str, error: str) -> None:
    config = yaml.safe_load((INVALID_RULES_DIRECTORY / filename).read_text())

    with pytest.raises(ValueError, match=error):
        parse_sync_rule(config)
