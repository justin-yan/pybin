import subprocess
from pathlib import Path

import pytest

from pybin.registry.ghcr import GHCRReleaseTarget
from pybin.types import Architecture, Binary, Platform, Release


@pytest.fixture
def release() -> Release:
    return Release(
        name="example-tool",
        version="1.2.3",
        license="MIT",
        upstream_url="https://github.com/example/example-tool",
        binaries=[
            Binary(b"amd64 binary", Architecture.X86_64, Platform.LINUX),
            Binary(b"arm64 binary", Architecture.ARM64, Platform.LINUX),
            Binary(b"macos binary", Architecture.ARM64, Platform.MACOS),
        ],
    )


def test_builds_linux_images(release: Release, monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[list[str], str, bytes]] = []

    def run(
        command: list[str],
        *,
        check: bool,
        input: str,
        text: bool,
    ) -> None:
        assert check
        assert text
        calls.append((command, input, Path(command[-1], "binary").read_bytes()))

    monkeypatch.setattr(subprocess, "run", run)

    GHCRReleaseTarget().build(release)

    assert [call[0][7] for call in calls] == ["linux/amd64", "linux/arm64"]
    assert [call[0][9] for call in calls] == [
        "ghcr.io/justin-yan/tool-example-tool:1.2.3-amd64",
        "ghcr.io/justin-yan/tool-example-tool:1.2.3-arm64",
    ]
    assert [call[2] for call in calls] == [b"amd64 binary", b"arm64 binary"]
    assert calls[0][1] == "\n".join(
        (
            "FROM scratch",
            'COPY --chmod=755 ["binary", "/example-tool"]',
        )
    )


def test_pushes_architecture_images_and_manifest(
    release: Release,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = GHCRReleaseTarget()
    builds: list[Release] = []
    monkeypatch.setattr(GHCRReleaseTarget, "build", lambda self, release: builds.append(release))
    calls: list[list[str]] = []

    def run(command: list[str], *, check: bool) -> None:
        assert check
        calls.append(command)

    monkeypatch.setattr(subprocess, "run", run)

    target.push(release)

    assert builds == [release]
    assert calls == [
        ["docker", "push", "ghcr.io/justin-yan/tool-example-tool:1.2.3-amd64"],
        ["docker", "push", "ghcr.io/justin-yan/tool-example-tool:1.2.3-arm64"],
        [
            "docker",
            "buildx",
            "imagetools",
            "create",
            "--tag",
            "ghcr.io/justin-yan/tool-example-tool:1.2.3",
            "ghcr.io/justin-yan/tool-example-tool:1.2.3-amd64",
            "ghcr.io/justin-yan/tool-example-tool:1.2.3-arm64",
        ],
    ]
