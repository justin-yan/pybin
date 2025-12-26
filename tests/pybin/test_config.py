from pathlib import Path

import pytest

from pybin.config import load_config, PLATFORM_TAG_MAP

TOOLS_DIR = Path(__file__).parent.parent.parent / "tools"


def get_all_tool_names():
    return sorted(f.stem for f in TOOLS_DIR.glob("*.yaml"))


@pytest.mark.parametrize("tool_name", get_all_tool_names())
def test_config_loads_successfully(tool_name: str):
    config = load_config(TOOLS_DIR / f"{tool_name}.yaml")
    assert config.name == tool_name
    assert config.version
    assert config.pypi_version
    assert config.upstream_repo.startswith("https://github.com/")
    assert config.license
    assert config.url_template
    assert config.targets


@pytest.mark.parametrize("tool_name", get_all_tool_names())
def test_config_targets_resolve(tool_name: str):
    config = load_config(TOOLS_DIR / f"{tool_name}.yaml")
    resolved = config.get_resolved_targets()

    # All targets should resolve to known platform tags
    for target, platform_name in config.targets.items():
        assert platform_name in PLATFORM_TAG_MAP, f"Unknown platform: {platform_name}"
        assert target in resolved


@pytest.mark.parametrize("tool_name", get_all_tool_names())
def test_config_url_generation(tool_name: str):
    config = load_config(TOOLS_DIR / f"{tool_name}.yaml")
    url_tag_map = config.get_url_tag_map()

    assert len(url_tag_map) == len(config.targets)
    for url, tag in url_tag_map.items():
        assert url.startswith("https://")
        assert config.version in url
        assert tag  # Platform tag should not be empty
