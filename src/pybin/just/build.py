from pybin.buildlib import build_wheels
from pybin.platform_tags import *

NAME = 'just'
UPSTREAM_REPO = 'https://github.com/casey/just'
VERSION = '1.45.0'
PYPI_VERSION = '1.45.0'
LICENSE = "CC0 1.0 Universal"

TARGET_TAG = {
    'aarch64-apple-darwin': MACOS_ARM,
    'aarch64-unknown-linux-musl': LINUX_ARM,
    'x86_64-apple-darwin': MACOS_X86,
    'x86_64-unknown-linux-musl': LINUX_X86,
}
URL_TAG = {f"{UPSTREAM_REPO}/releases/download/{VERSION}/{NAME}-{VERSION}-{target}.tar.gz": tag for target, tag in TARGET_TAG.items()}


if __name__ == "__main__":
    build_wheels(
        NAME,
        PYPI_VERSION,
        URL_TAG,
        UPSTREAM_REPO,
        LICENSE,
        )
