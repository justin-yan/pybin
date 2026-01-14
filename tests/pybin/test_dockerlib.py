from pathlib import Path

import pytest

from pybin.config import load_config
from pybin.dockerlib import (
    get_compression_mode,
    get_docker_targets,
    generate_dockerfile,
    DOCKER_ARCH_MAP,
)

TOOLS_DIR = Path(__file__).parent.parent.parent / "tools"


def get_all_tool_names():
    return sorted(f.stem for f in TOOLS_DIR.glob("*.yaml"))


class TestGetCompressionMode:
    def test_tar_gz(self):
        assert get_compression_mode("https://example.com/foo.tar.gz") == "gz"

    def test_tgz(self):
        assert get_compression_mode("https://example.com/foo.tgz") == "gz"

    def test_tar_bz2(self):
        assert get_compression_mode("https://example.com/foo.tar.bz2") == "bz2"

    def test_zip(self):
        assert get_compression_mode("https://example.com/foo.zip") == "zip"

    def test_raw_binary(self):
        assert get_compression_mode("https://example.com/foo") == "none"


class TestGetDockerTargets:
    @pytest.mark.parametrize("tool_name", get_all_tool_names())
    def test_docker_targets_valid_architectures(self, tool_name: str):
        config = load_config(TOOLS_DIR / f"{tool_name}.yaml")
        docker_targets = get_docker_targets(config)

        # All returned architectures should be amd64 or arm64
        for arch in docker_targets:
            assert arch in ["amd64", "arm64"]

    @pytest.mark.parametrize("tool_name", get_all_tool_names())
    def test_docker_targets_have_valid_urls(self, tool_name: str):
        config = load_config(TOOLS_DIR / f"{tool_name}.yaml")
        docker_targets = get_docker_targets(config)

        for arch, url in docker_targets.items():
            assert url.startswith("https://")
            assert config.version in url

    def test_prefers_musl_builds(self):
        """Verify that musl builds are preferred over gnu builds for Docker."""
        config = load_config(TOOLS_DIR / "just.yaml")
        docker_targets = get_docker_targets(config)

        # just.yaml uses musl targets, so URLs should contain 'musl'
        for arch, url in docker_targets.items():
            assert "musl" in url


class TestGenerateDockerfile:
    @pytest.mark.parametrize("tool_name", get_all_tool_names())
    def test_dockerfile_contains_binary_name(self, tool_name: str):
        config = load_config(TOOLS_DIR / f"{tool_name}.yaml")
        dockerfile = generate_dockerfile(config)

        # Final COPY should reference the binary name
        assert f"/bin/{config.name}" in dockerfile

    def test_dockerfile_uses_scratch_base(self):
        config = load_config(TOOLS_DIR / "just.yaml")
        dockerfile = generate_dockerfile(config)

        assert "FROM scratch" in dockerfile

    def test_dockerfile_uses_multistage_build(self):
        config = load_config(TOOLS_DIR / "just.yaml")
        dockerfile = generate_dockerfile(config)

        assert "FROM ubuntu:jammy AS build" in dockerfile
        assert "COPY --from=build" in dockerfile


class TestDockerArchMap:
    def test_all_linux_platforms_mapped(self):
        """Ensure all Linux platform names have Docker arch mappings."""
        linux_platforms = [
            "linux_arm",
            "linux_x86",
            "linux_gnu_arm",
            "linux_gnu_x86",
            "linux_musl_arm",
            "linux_musl_x86",
        ]
        for platform in linux_platforms:
            assert platform in DOCKER_ARCH_MAP

    def test_macos_platforms_not_mapped(self):
        """macOS platforms should not be in Docker arch map."""
        assert "macos_arm" not in DOCKER_ARCH_MAP
        assert "macos_x86" not in DOCKER_ARCH_MAP
        assert "macos_universal" not in DOCKER_ARCH_MAP
