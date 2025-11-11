from pybin.buildlib import build_wheels
from pybin.platform_tags import *

NAME = 'temporal'
UPSTREAM_REPO = "https://github.com/temporalio/cli"
VERSION = '1.5.1'
PYPI_VERSION = '1.5.1'
LICENSE = "MIT"

TARGET_TAG = {
    'darwin_arm64': MACOS_ARM,
    'linux_arm64': LINUX_ARM,
    'darwin_amd64': MACOS_X86,
    'linux_amd64': LINUX_X86,
}
URL_TAG = {f"{UPSTREAM_REPO}/releases/download/v{VERSION}/{NAME}_cli_{VERSION}_{target}.tar.gz": tag for target, tag in TARGET_TAG.items()}

if __name__ == "__main__":
    build_wheels(
        NAME,
        PYPI_VERSION,
        URL_TAG,
        UPSTREAM_REPO,
        LICENSE,
        )
