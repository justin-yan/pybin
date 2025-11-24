import pytest

from pybin.update import extract_version


def test_extract_version_handles_prefixed_tag():
    assert extract_version("rust-v0.63.0") == "0.63.0"


def test_extract_version_handles_plain_semver():
    assert extract_version("0.63.0") == "0.63.0"


def test_extract_version_finds_embedded_semver():
    assert extract_version("fastfetch-2.55.1.tar.gz") == "2.55.1"


def test_extract_version_raises_without_semver():
    with pytest.raises(ValueError):
        extract_version("no-version-present")
