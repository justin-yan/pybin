from pybin.buildlib import build_wheels
from pybin.platform_tags import *

NAME = 'dive'
UPSTREAM_REPO = 'https://github.com/wagoodman/dive'
VERSION = '0.13.1'
PYPI_VERSION = '0.13.1'
LICENSE = "MIT"

TARGET_TAG = {
    'darwin_amd64': MACOS_X86,
    'darwin_arm64': MACOS_ARM,
    'linux_amd64': LINUX_X86,
    'linux_arm64': LINUX_ARM,
}
URL_TAG = {f"{UPSTREAM_REPO}/releases/download/v{VERSION}/{NAME}_{VERSION}_{target}.tar.gz": tag for target, tag in TARGET_TAG.items()}


if __name__ == "__main__":
    build_wheels(
        NAME,
        PYPI_VERSION,
        URL_TAG,
        UPSTREAM_REPO,
        LICENSE,
        )
