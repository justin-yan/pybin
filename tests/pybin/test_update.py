import pytest

from pybin import update


def test_extract_version_handles_prefixed_tag():
    assert update.extract_version("rust-v0.63.0") == "0.63.0"


def test_extract_version_handles_plain_semver():
    assert update.extract_version("0.63.0") == "0.63.0"


def test_extract_version_finds_embedded_semver():
    assert update.extract_version("fastfetch-2.55.1.tar.gz") == "2.55.1"


def test_extract_version_raises_without_semver():
    with pytest.raises(ValueError):
        update.extract_version("no-version-present")
