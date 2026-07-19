import pytest

from pybin.registry.github import GithubReleasePuller
from pybin.types import Architecture, Platform

pytestmark = pytest.mark.integration


def test_just_homogeneous_case() -> None:
    # - repo name matches bin name
    # - asset name matches bin name
    # - tar format
    # - archive file extraction name matches bin name
    # - standard rust arch/platform annotations
    release = GithubReleasePuller(
        repository="casey/just",
        version="1.56.0",
        release_slug="{version}/{name}-{version}-{target}.tar.gz",
        targets=[
            "x86_64-unknown-linux-musl",
            "aarch64-apple-darwin",
            "aarch64-unknown-linux-musl",
        ],
    )()

    assert release.name == "just"
    assert release.version == "1.56.0"
    assert release.license == "CC0-1.0"
    assert [binary.architecture for binary in release.binaries] == [
        Architecture.X86_64,
        Architecture.ARM64,
        Architecture.ARM64,
    ]
    assert [binary.platform for binary in release.binaries] == [
        Platform.LINUX_MUSL,
        Platform.MACOS,
        Platform.LINUX_MUSL,
    ]
    assert release.binaries[0].content.startswith(b"\x7fELF")
    assert release.binaries[2].content.startswith(b"\x7fELF")
    assert all(len(binary.content) >= 250_000 for binary in release.binaries)


def test_caddy_golang_case() -> None:
    # - repo name matches bin name
    # - asset name matches bin name
    # - tar format
    # - archive file extraction name matches bin name
    # - standard golang arch/platform annotations
    release = GithubReleasePuller(
        repository="caddyserver/caddy",
        version="2.11.4",
        release_slug="v{version}/{name}_{version}_{target}.tar.gz",
        targets=[
            "mac_arm64",
            "mac_amd64",
            "linux_arm64",
            "linux_amd64",
        ],
    )()

    assert release.name == "caddy"
    assert release.version == "2.11.4"
    assert release.license == "Apache-2.0"
    assert [binary.architecture for binary in release.binaries] == [
        Architecture.ARM64,
        Architecture.X86_64,
        Architecture.ARM64,
        Architecture.X86_64,
    ]
    assert [binary.platform for binary in release.binaries] == [
        Platform.MACOS,
        Platform.MACOS,
        Platform.LINUX,
        Platform.LINUX,
    ]
    assert release.binaries[2].content.startswith(b"\x7fELF")
    assert release.binaries[3].content.startswith(b"\x7fELF")
    assert all(len(binary.content) >= 250_000 for binary in release.binaries)


def test_gh_heterogeneous_case() -> None:
    # - repo name does not match bin name
    # - download url does match target bin name
    # - zip and tar formats
    # - archive file extraction *doesn't* match bin name
    # - standard golang arch/platform annotations
    release = GithubReleasePuller(
        repository="cli/cli",
        version="2.96.0",
        release_slug="v{version}/{name}_{version}_{target}",
        targets=[
            "macOS_arm64.zip",
            "macOS_amd64.zip",
            "linux_arm64.tar.gz",
            "linux_amd64.tar.gz",
        ],
        bin_name="gh",
    )()

    assert release.name == "gh"
    assert release.version == "2.96.0"
    assert release.license == "MIT"
    assert [binary.architecture for binary in release.binaries] == [
        Architecture.ARM64,
        Architecture.X86_64,
        Architecture.ARM64,
        Architecture.X86_64,
    ]
    assert [binary.platform for binary in release.binaries] == [
        Platform.MACOS,
        Platform.MACOS,
        Platform.LINUX,
        Platform.LINUX,
    ]
    assert release.binaries[2].content.startswith(b"\x7fELF")
    assert release.binaries[3].content.startswith(b"\x7fELF")
    assert all(len(binary.content) >= 250_000 for binary in release.binaries)


def test_rclone_windows_case() -> None:
    # - repo name matches bin name
    # - zip format
    # - archive binary has an .exe suffix
    # - standard golang arch/platform annotations
    release = GithubReleasePuller(
        repository="rclone/rclone",
        version="1.74.4",
        release_slug="v{version}/{name}-v{version}-{target}.zip",
        targets=["windows-amd64"],
    )()

    assert release.name == "rclone"
    assert release.version == "1.74.4"
    assert release.license == "MIT"
    assert len(release.binaries) == 1
    assert release.binaries[0].architecture == Architecture.X86_64
    assert release.binaries[0].platform == Platform.WINDOWS
    assert release.binaries[0].content.startswith(b"MZ")
    assert len(release.binaries[0].content) >= 250_000


def test_dbmate_passthrough_case() -> None:
    # - repo name matches bin name
    # - assets are unarchived binaries
    # - standard golang arch/platform annotations
    release = GithubReleasePuller(
        repository="amacneil/dbmate",
        version="2.34.1",
        release_slug="v{version}/{name}-{target}",
        targets=[
            "macos-arm64",
            "macos-amd64",
            "linux-arm64",
            "linux-amd64",
        ],
    )()

    assert release.name == "dbmate"
    assert release.version == "2.34.1"
    assert release.license == "MIT"
    assert [binary.architecture for binary in release.binaries] == [
        Architecture.ARM64,
        Architecture.X86_64,
        Architecture.ARM64,
        Architecture.X86_64,
    ]
    assert [binary.platform for binary in release.binaries] == [
        Platform.MACOS,
        Platform.MACOS,
        Platform.LINUX,
        Platform.LINUX,
    ]
    assert release.binaries[2].content.startswith(b"\x7fELF")
    assert release.binaries[3].content.startswith(b"\x7fELF")
    assert all(len(binary.content) >= 250_000 for binary in release.binaries)


def test_fastfetch_case() -> None:
    # - repo name matches bin name
    # - tar format
    # - archive contains *two* files that match bin name, dirname is needed to disambiguate
    release = GithubReleasePuller(
        repository="fastfetch-cli/fastfetch",
        version="2.66.0",
        release_slug="{version}/{name}-{target}.tar.gz",
        targets=[
            "macos-aarch64",
            "macos-amd64",
            "linux-aarch64",
            "linux-amd64",
        ],
    )()

    assert release.name == "fastfetch"
    assert release.version == "2.66.0"
    assert release.license == "MIT"
    assert [binary.architecture for binary in release.binaries] == [
        Architecture.ARM64,
        Architecture.X86_64,
        Architecture.ARM64,
        Architecture.X86_64,
    ]
    assert [binary.platform for binary in release.binaries] == [
        Platform.MACOS,
        Platform.MACOS,
        Platform.LINUX,
        Platform.LINUX,
    ]
    assert release.binaries[2].content.startswith(b"\x7fELF")
    assert release.binaries[3].content.startswith(b"\x7fELF")
    assert all(len(binary.content) >= 250_000 for binary in release.binaries)


def test_codex_case() -> None:
    # - repo name matches bin name
    # - zstandard-compressed binary
    # - standard rust arch/platform annotations
    release = GithubReleasePuller(
        repository="openai/codex",
        version="0.144.1",
        release_slug="rust-v{version}/{name}-{target}.zst",
        targets=[
            "aarch64-apple-darwin",
            "x86_64-apple-darwin",
            "aarch64-unknown-linux-musl",
            "x86_64-unknown-linux-musl",
        ],
    )()

    assert release.name == "codex"
    assert release.version == "0.144.1"
    assert release.license == "Apache-2.0"
    assert [binary.architecture for binary in release.binaries] == [
        Architecture.ARM64,
        Architecture.X86_64,
        Architecture.ARM64,
        Architecture.X86_64,
    ]
    assert [binary.platform for binary in release.binaries] == [
        Platform.MACOS,
        Platform.MACOS,
        Platform.LINUX_MUSL,
        Platform.LINUX_MUSL,
    ]
    assert release.binaries[2].content.startswith(b"\x7fELF")
    assert release.binaries[3].content.startswith(b"\x7fELF")
    assert all(len(binary.content) >= 250_000 for binary in release.binaries)
