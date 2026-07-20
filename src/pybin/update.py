import json
import re
import urllib.request
from pathlib import Path

import yaml


def extract_version(tag: str) -> str:
    """Extract MAJOR.MINOR.PATCH from a tag string."""
    match = re.search(r"\d+\.\d+\.\d+", tag)
    if match:
        return match.group(0)
    raise ValueError(f"Could not extract MAJOR.MINOR.PATCH from tag: {tag!r}")


def get_latest_version(repository: str) -> str:
    with urllib.request.urlopen(f"https://api.github.com/repos/{repository}/releases/latest") as response:
        data = response.read().decode("utf-8")
        tag = json.loads(data)["tag_name"]
        return extract_version(tag)


def update_rule_version(rule_path: Path, old_version: str, new_version: str) -> None:
    content = re.sub(
        rf'^([ \t]*version:\s*["\']?){re.escape(old_version)}(["\']?)$',
        rf"\g<1>{new_version}\g<2>",
        rule_path.read_text(),
        count=1,
        flags=re.MULTILINE,
    )
    rule_path.write_text(content)


def update_rules(rules_directory: Path) -> None:
    for rule_path in sorted(rules_directory.glob("*.yaml")):
        github = yaml.safe_load(rule_path.read_text())["source"]["github"]
        repository = str(github["repository"])
        version = str(github["version"])
        name = rule_path.stem

        try:
            latest_version = get_latest_version(repository)
        except Exception as error:
            print(f"Skipping {name}: {error}")
            continue

        if latest_version == version:
            print(f"{name} is already up to date")
            continue

        update_rule_version(rule_path, version, latest_version)
        print(f"{name} {version} -> {latest_version}")
