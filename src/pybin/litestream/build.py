from pybin.buildlib import build_wheels
from pybin.platform_tags import *

NAME = 'litestream'
UPSTREAM_REPO = 'https://github.com/benbjohnson/litestream'
VERSION = '0.5.2'
PYPI_VERSION = '0.5.2'
LICENSE = "Apache-2.0"

TARGET_TAG = {
    'darwin-arm64': MACOS_ARM,
    'darwin-x86_64': MACOS_X86,
    'linux-arm64': LINUX_ARM,
    'linux-x86_64': LINUX_X86,
}
URL_TAG = {f"{UPSTREAM_REPO}/releases/download/v{VERSION}/{NAME}-{VERSION}-{target}.tar.gz": tag for target, tag in TARGET_TAG.items()}


if __name__ == "__main__":
    build_wheels(
        NAME,
        PYPI_VERSION,
        URL_TAG,
        UPSTREAM_REPO,
        LICENSE,
        )
