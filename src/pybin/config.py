from dataclasses import dataclass
from pathlib import Path

import yaml

from pybin.platform_tags import (
    LINUX_ARM,
    LINUX_GNU_ARM,
    LINUX_GNU_X86,
    LINUX_MUSL_ARM,
    LINUX_MUSL_X86,
    LINUX_X86,
    MACOS_ARM,
    MACOS_UNIVERSAL,
    MACOS_X86,
)

# Map symbolic names in YAML to actual platform tags
PLATFORM_TAG_MAP = {
    "linux_arm": LINUX_ARM,
    "linux_x86": LINUX_X86,
    "linux_gnu_arm": LINUX_GNU_ARM,
    "linux_gnu_x86": LINUX_GNU_X86,
    "linux_musl_arm": LINUX_MUSL_ARM,
    "linux_musl_x86": LINUX_MUSL_X86,
    "macos_arm": MACOS_ARM,
    "macos_x86": MACOS_X86,
    "macos_universal": MACOS_UNIVERSAL,
}

# Map symbolic names to Docker platform strings (Linux only)
DOCKER_PLATFORM_MAP = {
    "linux_arm": "linux/arm64",
    "linux_x86": "linux/amd64",
    "linux_gnu_arm": "linux/arm64",
    "linux_gnu_x86": "linux/amd64",
    "linux_musl_arm": "linux/arm64",
    "linux_musl_x86": "linux/amd64",
}


@dataclass
class ToolConfig:
    name: str
    upstream_repo: str
    version: str
    pypi_version: str
    license: str
    url_template: str
    targets: dict[str, str]  # target suffix -> symbolic platform name

    def get_resolved_targets(self) -> dict[str, str]:
        """Resolve symbolic platform names to actual platform tags."""
        resolved = {}
        for target, platform_name in self.targets.items():
            platform_tag = PLATFORM_TAG_MAP.get(platform_name)
            if platform_tag is None:
                raise ValueError(
                    f"Unknown platform tag '{platform_name}' for target '{target}'"
                )
            resolved[target] = platform_tag
        return resolved

    def get_url_tag_map(self) -> dict[str, str]:
        """Generate the URL -> platform tag mapping."""
        return {
            self.url_template.format(
                repo=self.upstream_repo,
                version=self.version,
                name=self.name,
                target=target,
            ): tag
            for target, tag in self.get_resolved_targets().items()
        }

    def get_docker_targets(self) -> dict[str, tuple[str, str]]:
        """Generate Docker platform -> (download_url, target_name) mapping.

        Only returns Linux targets since Docker containers are Linux-based.
        """
        result = {}
        for target, platform_name in self.targets.items():
            docker_platform = DOCKER_PLATFORM_MAP.get(platform_name)
            if docker_platform is None:
                # Skip non-Linux platforms (macOS, etc.)
                continue
            # Skip if we already have this docker platform (e.g., both musl and gnu map to same)
            if docker_platform in result:
                continue
            download_url = self.url_template.format(
                repo=self.upstream_repo,
                version=self.version,
                name=self.name,
                target=target,
            )
            result[docker_platform] = (download_url, target)
        return result


def load_config(path: Path) -> ToolConfig:
    """Load a single tool config from a YAML file."""
    with open(path) as f:
        data = yaml.safe_load(f)

    return ToolConfig(
        name=data["name"],
        upstream_repo=data["upstream_repo"],
        version=str(data["version"]),
        pypi_version=str(data["pypi_version"]),
        license=data["license"],
        url_template=data["url_template"],
        targets=data["targets"],
    )


def load_all_configs(config_dir: Path) -> list[ToolConfig]:
    """Load all tool configs from a directory."""
    configs = []
    for yaml_file in sorted(config_dir.glob("*.yaml")):
        configs.append(load_config(yaml_file))
    return configs
