from pybin.buildlib import build_wheels
from pybin.platform_tags import *

NAME = 'fastfetch'
UPSTREAM_REPO = "https://github.com/fastfetch-cli/fastfetch"
VERSION = '2.56.0'
PYPI_VERSION = '2.56.0'
LICENSE = "MIT"

TARGET_TAG = {
    'macos-aarch64': MACOS_ARM,
    'macos-amd64': MACOS_X86,
    'linux-amd64': LINUX_X86,
    'linux-aarch64': LINUX_ARM,
}
URL_TAG = {f"{UPSTREAM_REPO}/releases/download/{VERSION}/{NAME}-{target}.tar.gz": tag for target, tag in TARGET_TAG.items()}


if __name__ == "__main__":
    build_wheels(
        NAME,
        PYPI_VERSION,
        URL_TAG,
        UPSTREAM_REPO,
        LICENSE,
        )
