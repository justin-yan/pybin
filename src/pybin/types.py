from dataclasses import dataclass
from enum import Enum
from typing import Protocol


class Architecture(str, Enum):
    X86_64 = "x86_64"
    ARM64 = "arm64"


class Platform(str, Enum):
    LINUX = "linux"
    MACOS = "macos"
    WINDOWS = "windows"


@dataclass(frozen=True)
class Binary:
    content: bytes
    architecture: Architecture
    platform: Platform


@dataclass(frozen=True)
class Release:
    name: str
    version: str
    license: str
    upstream_url: str
    binaries: list[Binary]


class ReleaseSource(Protocol):
    def __call__(self) -> Release: ...


class ReleaseTarget(Protocol):
    def __call__(self, release: Release) -> None: ...


@dataclass(frozen=True)
class SyncRule:
    source: ReleaseSource
    targets: list[ReleaseTarget]
