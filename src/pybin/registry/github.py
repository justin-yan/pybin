import json
import urllib.request
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path, PurePosixPath
from typing import cast
from urllib.parse import urlparse

import zstandard

from pybin.format.tar import TarUnpacker
from pybin.format.zip import ZipUnpacker
from pybin.types import Architecture, Binary, Platform, Release

_CACHE_DIRECTORY = Path("/tmp/pybin")


def _target_platform(target: str) -> Platform:
    normalized = target.lower()
    if "linux" in normalized:
        return Platform.LINUX
    elif "windows" in normalized:
        return Platform.WINDOWS
    elif any(name in normalized for name in ("apple", "darwin", "macos", "osx", "mac_")):
        return Platform.MACOS
    else:
        raise ValueError(f"Could not determine platform from target: {target}")


def _target_architecture(target: str) -> Architecture:
    normalized = target.lower()
    if "aarch64" in normalized or "arm64" in normalized:
        return Architecture.ARM64
    elif "x86_64" in normalized or "amd64" in normalized:
        return Architecture.X86_64
    else:
        raise ValueError(f"Could not determine architecture from target: {target}")


@dataclass(frozen=True)
class GithubReleasePuller:
    repository: str
    version: str
    release_slug: str
    targets: list[str]
    bin_name: str | None = None  # Needed when desired CLI name does not match repository name, e.g. cli/cli vs. gh

    @classmethod
    def from_config(cls, config: dict[str, object]) -> "GithubReleasePuller":
        bin_name = config.get("bin_name")
        return cls(
            repository=str(config["repository"]),
            version=str(config["version"]),
            release_slug=str(config["release_slug"]),
            targets=[str(target) for target in cast(list[object], config["targets"])],
            bin_name=str(bin_name) if bin_name is not None else None,
        )

    @property
    def _bin_name(self) -> str:
        """
        For ease of configuration, we prefer deriving the binary name from the repository name, but allow for an
          explicit override in cases where these do not match
        """
        if self.bin_name is not None:
            return self.bin_name
        _, bin_name = self.repository.split("/")
        return bin_name

    def _license_name(self) -> str:
        with urllib.request.urlopen(f"https://api.github.com/repos/{self.repository}/license") as response:
            return json.load(response)["license"]["spdx_id"]

    def _read_url(self, url: str) -> bytes:
        """
        This method encapsulates a small local caching setup which is mostly useful when running repeated integration
          tests and you don't need to re-download the asset over and over.
        """
        cache_path = _CACHE_DIRECTORY / sha256(url.encode()).hexdigest()
        if cache_path.exists():
            return cache_path.read_bytes()

        with urllib.request.urlopen(url) as response:
            content = response.read()
        _CACHE_DIRECTORY.mkdir(parents=True, exist_ok=True)
        cache_path.write_bytes(content)
        return content

    def _pull_binary(self, target: str) -> Binary:
        # TODO: it's possible that we want to map these explicitly instead of deriving them with these heuristics.
        #   however, that adds a lot more per-project onboarding work.  So let's derive these automatically for now
        #   and we can revisit this if the logic here becomes extremely unwieldy.
        platform = _target_platform(target)
        arch = _target_architecture(target)

        # Construct the download URL and retrieve the asset payload.
        release_slug = self.release_slug.format(
            name=self._bin_name,
            version=self.version,
            target=target,
        )
        asset_url = f"https://github.com/{self.repository}/releases/download/{release_slug}"
        distribution = self._read_url(asset_url)

        # Derive how to unpack the target binary
        asset_path = PurePosixPath(urlparse(asset_url).path)
        asset_suffixes = tuple(asset_path.suffixes)
        extract_spec = f"{self._bin_name}.exe" if platform == Platform.WINDOWS else self._bin_name
        if asset_suffixes[-2:] in ((".tar", ".gz"), (".tar", ".bz2")):
            content = TarUnpacker(extract_spec=extract_spec)(distribution)
        elif asset_suffixes[-1:] == (".zip",):
            content = ZipUnpacker(extract_spec=extract_spec)(distribution)
        elif asset_suffixes[-1:] == (".zst",):
            content = zstandard.ZstdDecompressor().decompress(distribution)
        else:
            content = distribution

        return Binary(
            content=content,
            architecture=arch,
            platform=platform,
        )

    def __call__(self) -> Release:
        return Release(
            name=self._bin_name,
            version=self.version,
            license=self._license_name(),
            upstream_url=f"https://github.com/{self.repository}",
            binaries=[self._pull_binary(target) for target in self.targets],
        )
