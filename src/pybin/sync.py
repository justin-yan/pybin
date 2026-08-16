from pathlib import Path
from typing import cast

import yaml

from pybin.registry.ghcr import GHCRReleaseTarget
from pybin.registry.github import GithubReleasePuller
from pybin.registry.pypi import PyPIReleaseTarget
from pybin.types import ReleaseTarget, SyncRule


def parse_sync_rule(config: dict[str, object]) -> SyncRule:
    source_config = config["source"]
    match source_config:
        case {"github": source_options}:
            source = GithubReleasePuller.from_config(cast(dict[str, object], source_options))
        case _:
            raise ValueError(f"Unknown source: {source_config}")

    targets: list[ReleaseTarget] = []
    for target_config in cast(list[dict[str, object]], config["targets"]):
        match target_config:
            case {"pypi": target_options}:
                targets.append(PyPIReleaseTarget.from_config(cast(dict[str, object], target_options)))
            case {"ghcr": target_options}:
                targets.append(GHCRReleaseTarget.from_config(cast(dict[str, object], target_options)))
            case _:
                raise ValueError(f"Unknown target: {target_config}")

    return SyncRule(source=source, targets=targets)


def _build(rule: SyncRule) -> None:
    release = rule.source()
    for target in rule.targets:
        target.build(release)


def build(path: Path) -> None:
    rule = parse_sync_rule(yaml.safe_load(path.read_text()))
    _build(rule)


def push(path: Path) -> None:
    rule = parse_sync_rule(yaml.safe_load(path.read_text()))
    release = rule.source()
    for target in rule.targets:
        target.push(release)


def sync(path: Path) -> None:
    build(path)
