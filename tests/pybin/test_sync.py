from pathlib import Path

import pytest
import yaml

from pybin.registry.docker import DockerReleaseBuilder
from pybin.registry.github import GithubReleasePuller
from pybin.registry.pypi import PyPIReleasePusher
from pybin.sync import parse_sync_rule
from pybin.types import SyncRule

PROJECT_DIRECTORY = Path(__file__).parents[2]
RULES_DIRECTORY = PROJECT_DIRECTORY / "rules"
INVALID_RULES_DIRECTORY = PROJECT_DIRECTORY / "tests" / "fixtures" / "sync"


def test_parse_sync_rule() -> None:
    config = yaml.safe_load((RULES_DIRECTORY / "codex.yaml").read_text())

    assert parse_sync_rule(config) == SyncRule(
        source=GithubReleasePuller(
            repository="openai/codex",
            version=config["source"]["github"]["version"],
            release_slug="rust-v{version}/{name}-{target}.zst",
            targets=[
                "aarch64-apple-darwin",
                "x86_64-apple-darwin",
                "aarch64-unknown-linux-musl",
                "x86_64-unknown-linux-musl",
            ],
        ),
        targets=[PyPIReleasePusher()],
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


def test_parse_sync_rule_with_docker_target() -> None:
    config = yaml.safe_load((RULES_DIRECTORY / "codex.yaml").read_text())
    config["targets"].append(
        {
            "docker": {
                "repository": "ghcr.io/example/{name}",
                "push": True,
            }
        }
    )

    rule = parse_sync_rule(config)

    assert rule.targets == [
        PyPIReleasePusher(),
        DockerReleaseBuilder(repository="ghcr.io/example/{name}", push=True),
    ]
