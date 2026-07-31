import subprocess
from pathlib import Path

import pytest

from pybin.registry.docker import DockerReleaseBuilder, generate_dockerfile
from pybin.types import Architecture, Binary, Platform, Release


def _release() -> Release:
    return Release(
        name="example-tool",
        version="1.2.3",
        license="MIT",
        upstream_url="https://github.com/example/tool",
        binaries=[
            Binary(b"amd64 binary", Architecture.X86_64, Platform.LINUX),
            Binary(b"arm64 binary", Architecture.ARM64, Platform.LINUX),
            Binary(b"macos binary", Architecture.ARM64, Platform.MACOS),
        ],
    )


def test_generates_scratch_dockerfile() -> None:
    assert (
        generate_dockerfile("example-tool")
        == """# syntax=docker/dockerfile:1
FROM scratch
ARG TARGETARCH
COPY --chmod=755 ${TARGETARCH} /example-tool
"""
    )


@pytest.mark.parametrize(
    ("builder", "output", "platforms", "tag"),
    [
        (DockerReleaseBuilder(), "--load", "linux/amd64", "tool-example-tool:1.2.3"),
        (
            DockerReleaseBuilder(repository="ghcr.io/example/{name}", push=True),
            "--push",
            "linux/amd64,linux/arm64",
            "ghcr.io/example/example-tool:1.2.3",
        ),
    ],
)
def test_builds_multi_platform_image(
    builder: DockerReleaseBuilder,
    output: str,
    platforms: str,
    tag: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[list[str]] = []
    contexts: list[dict[str, bytes]] = []

    def run(command: list[str], check: bool) -> None:
        assert check is True
        calls.append(command)
        context = Path(command[-1])
        contexts.append({path.name: path.read_bytes() for path in context.iterdir()})

    monkeypatch.setattr("pybin.registry.docker.machine", lambda: "x86_64")
    monkeypatch.setattr(subprocess, "run", run)
    builder(_release())

    assert contexts == [
        {
            "Dockerfile": generate_dockerfile("example-tool").encode(),
            "amd64": b"amd64 binary",
            "arm64": b"arm64 binary",
        }
    ]
    assert calls == [
        [
            "docker",
            "buildx",
            "build",
            output,
            "--platform",
            platforms,
            "--provenance=false",
            "--tag",
            tag,
            calls[0][-1],
        ]
    ]


def test_rejects_release_without_linux_binary() -> None:
    release = Release(
        name="example-tool",
        version="1.2.3",
        license="MIT",
        upstream_url="https://github.com/example/tool",
        binaries=[Binary(b"macos binary", Architecture.ARM64, Platform.MACOS)],
    )

    with pytest.raises(ValueError, match="has no Linux binaries"):
        DockerReleaseBuilder()(release)
