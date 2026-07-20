from pathlib import Path
from typing import cast

import yaml

from pybin.registry.github import GithubReleasePuller
from pybin.registry.pypi import PyPIReleasePusher
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
                targets.append(PyPIReleasePusher.from_config(cast(dict[str, object], target_options)))
            case _:
                raise ValueError(f"Unknown target: {target_config}")

    return SyncRule(source=source, targets=targets)


def sync(path: Path) -> None:
    rule = parse_sync_rule(yaml.safe_load(path.read_text()))
    release = rule.source()
    for target in rule.targets:
        target(release)
