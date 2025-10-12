from pybin.buildlib import build_wheels
from pybin.platform_tags import *

NAME = 'usql'
UPSTREAM_REPO = 'https://github.com/xo/usql'
VERSION = '0.19.25'
PYPI_VERSION = '0.19.25'
LICENSE = "MIT"

TARGET_TAG = {
    'darwin-arm64': MACOS_ARM,
    'darwin-amd64': MACOS_X86,
    'linux-arm64': LINUX_ARM,
    'linux-amd64': LINUX_X86,
}
URL_TAG = {f"{UPSTREAM_REPO}/releases/download/v{VERSION}/{NAME}-{VERSION}-{target}.tar.bz2": tag for target, tag in TARGET_TAG.items()}


if __name__ == "__main__":
    build_wheels(
        NAME,
        PYPI_VERSION,
        URL_TAG,
        UPSTREAM_REPO,
        LICENSE,
        )
