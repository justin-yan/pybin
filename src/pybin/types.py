from dataclasses import dataclass
from enum import Enum


class Architecture(str, Enum):
    X86_64 = "x86_64"
    ARM64 = "arm64"
    ARMV7 = "armv7"


class Platform(str, Enum):
    LINUX = "linux"
    LINUX_GNU = "linux_gnu"
    LINUX_MUSL = "linux_musl"
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
    binaries: list[Binary]
