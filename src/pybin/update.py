import json
import re
import urllib.request
from pathlib import Path


def extract_version(tag: str) -> str:
    """Extract MAJOR.MINOR.PATCH from a tag string."""
    match = re.search(r'\d+\.\d+\.\d+', tag)
    if match:
        return match.group(0)
    raise ValueError(f"Could not extract MAJOR.MINOR.PATCH from tag: {tag!r}")


def get_latest_tag(upstream_url: str) -> str:
    """Fetch the raw tag_name from the latest GitHub release."""
    repo, name = upstream_url.split("/")[-2:]
    with urllib.request.urlopen(
        f"https://api.github.com/repos/{repo}/{name}/releases/latest"
    ) as response:
        data = response.read().decode("utf-8")
        return json.loads(data)["tag_name"]


def get_latest_version(upstream_url: str) -> str:
    tag = get_latest_tag(upstream_url)
    return extract_version(tag)


def update_yaml_version(
    yaml_path: Path,
    old_version: str,
    new_version: str,
    old_pypi_version: str | None = None,
    new_pypi_version: str | None = None,
) -> None:
    if old_pypi_version is None:
        old_pypi_version = old_version
    if new_pypi_version is None:
        new_pypi_version = new_version

    content = yaml_path.read_text()
    content = re.sub(
        rf'^(version:\s*["\']?){re.escape(old_version)}(["\']?)$',
        rf'\g<1>{new_version}\g<2>',
        content,
        flags=re.MULTILINE,
    )
    content = re.sub(
        rf'^(pypi_version:\s*["\']?){re.escape(old_pypi_version)}(["\']?)$',
        rf'\g<1>{new_pypi_version}\g<2>',
        content,
        flags=re.MULTILINE,
    )
    yaml_path.write_text(content)
