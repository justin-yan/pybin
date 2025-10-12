from pybin.buildlib import build_wheels
from pybin.platform_tags import *

NAME = 'litestream'
UPSTREAM_REPO = 'https://github.com/benbjohnson/litestream'
VERSION = '0.3.13'
PYPI_VERSION = '0.3.13'
LICENSE = "Apache-2.0"

TARGET_TAG = {
    'darwin-arm64.zip': MACOS_ARM,
    'linux-arm64.tar.gz': LINUX_ARM,
    'darwin-amd64.zip': MACOS_X86,
    'linux-amd64.tar.gz': LINUX_X86,
}
URL_TAG = {f"{UPSTREAM_REPO}/releases/download/v{VERSION}/{NAME}-V{VERSION}-{target}": tag for target, tag in TARGET_TAG.items()}


if __name__ == "__main__":
    build_wheels(
        NAME,
        PYPI_VERSION,
        URL_TAG,
        UPSTREAM_REPO,
        LICENSE,
        )
