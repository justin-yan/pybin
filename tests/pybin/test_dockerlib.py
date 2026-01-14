from pathlib import Path

import pytest

from pybin.config import load_config
from pybin.docker_tags import DOCKER_ARCH_MAP, DOCKER_AMD64, DOCKER_ARM64
from pybin.dockerlib import get_extraction_command, generate_dockerfile

TOOLS_DIR = Path(__file__).parent.parent.parent / "tools"


def get_all_tool_names():
    return sorted(f.stem for f in TOOLS_DIR.glob("*.yaml"))


def test_docker_arch_map_covers_linux_platforms():
    """All linux_* platform names should have Docker architecture mappings."""
    linux_platforms = [
        "linux_arm",
        "linux_x86",
        "linux_gnu_arm",
        "linux_gnu_x86",
        "linux_musl_arm",
        "linux_musl_x86",
    ]
    for platform in linux_platforms:
        assert platform in DOCKER_ARCH_MAP, f"Missing Docker mapping for {platform}"
        assert DOCKER_ARCH_MAP[platform] in (DOCKER_AMD64, DOCKER_ARM64)


def test_extraction_command_tar_gz():
    cmd = get_extraction_command("https://example.com/file.tar.gz", "mybin")
    assert "tar xzf" in cmd
    assert "find . -name" in cmd
    assert "mybin" in cmd


def test_extraction_command_tar_bz2():
    cmd = get_extraction_command("https://example.com/file.tar.bz2", "mybin")
    assert "tar xjf" in cmd
    assert "find . -name" in cmd
    assert "mybin" in cmd


def test_extraction_command_zip():
    cmd = get_extraction_command("https://example.com/file.zip", "mybin")
    assert "unzip" in cmd
    assert "find . -name" in cmd
    assert "mybin" in cmd


def test_extraction_command_raw():
    cmd = get_extraction_command("https://example.com/mybin", "mybin")
    assert cmd == "mv archive mybin"


@pytest.mark.parametrize("tool_name", get_all_tool_names())
def test_config_has_docker_targets(tool_name: str):
    """All tools should have at least one Linux target for Docker builds."""
    config = load_config(TOOLS_DIR / f"{tool_name}.yaml")
    docker_targets = config.get_docker_targets()

    # Every tool should have at least one Linux target
    assert len(docker_targets) > 0, f"{tool_name} has no Linux targets for Docker"


@pytest.mark.parametrize("tool_name", get_all_tool_names())
def test_dockerfile_generation(tool_name: str):
    """Test Dockerfile generation for tools with both amd64 and arm64 targets."""
    config = load_config(TOOLS_DIR / f"{tool_name}.yaml")
    docker_targets = config.get_docker_targets()

    # Skip tools without both architectures
    if DOCKER_AMD64 not in docker_targets or DOCKER_ARM64 not in docker_targets:
        pytest.skip(f"{tool_name} doesn't have both amd64 and arm64 targets")

    dockerfile = generate_dockerfile(config)

    assert config.name in dockerfile
    assert config.version in dockerfile
    assert "FROM scratch" in dockerfile
    assert "build-amd64" in dockerfile
    assert "build-arm64" in dockerfile
