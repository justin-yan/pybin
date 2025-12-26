"""
Tests to verify YAML configs produce equivalent URL/tag mappings
to the existing build.py files.
"""
import pytest
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec

from pybin.config import load_config, load_all_configs


TOOLS_DIR = Path(__file__).parent.parent.parent / "tools"
SRC_DIR = Path(__file__).parent.parent.parent / "src" / "pybin"


def import_build_module(tool_name: str):
    """Import a build.py module by tool name."""
    build_path = SRC_DIR / tool_name / "build.py"
    if not build_path.exists():
        return None
    spec = spec_from_file_location(f"{tool_name}_build", build_path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def get_all_tool_names():
    """Get list of tools that have both build.py and yaml config."""
    tools = []
    for yaml_file in TOOLS_DIR.glob("*.yaml"):
        tool_name = yaml_file.stem
        build_path = SRC_DIR / tool_name / "build.py"
        if build_path.exists():
            tools.append(tool_name)
    return sorted(tools)


@pytest.mark.parametrize("tool_name", get_all_tool_names())
def test_config_matches_build_py(tool_name: str):
    """Verify YAML config matches build.py metadata and targets."""
    config = load_config(TOOLS_DIR / f"{tool_name}.yaml")
    build_module = import_build_module(tool_name)
    assert build_module is not None, f"No build.py found for {tool_name}"

    # Metadata
    assert config.name == build_module.NAME
    assert config.version == build_module.VERSION
    assert config.pypi_version == build_module.PYPI_VERSION
    assert config.upstream_repo == build_module.UPSTREAM_REPO
    assert config.license == build_module.LICENSE

    # Targets
    assert config.get_resolved_targets() == build_module.TARGET_TAG

    # URL generation
    assert config.get_url_tag_map() == build_module.URL_TAG
