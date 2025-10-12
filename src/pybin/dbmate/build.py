from pybin.buildlib import build_wheels
from pybin.platform_tags import *

NAME = 'dbmate'
UPSTREAM_REPO = 'https://github.com/amacneil/dbmate'
VERSION = '2.28.0'
PYPI_VERSION = '2.28.0'
LICENSE = "MIT"

TARGET_TAG = {
    'macos-arm64': MACOS_ARM,
    'linux-arm64': LINUX_ARM,
    'macos-amd64': MACOS_X86,
    'linux-amd64': LINUX_X86,
}
URL_TAG = {f"{UPSTREAM_REPO}/releases/download/v{VERSION}/{NAME}-{target}": tag for target, tag in TARGET_TAG.items()}


if __name__ == "__main__":
    build_wheels(
        NAME,
        PYPI_VERSION,
        URL_TAG,
        UPSTREAM_REPO,
        LICENSE,
        )
