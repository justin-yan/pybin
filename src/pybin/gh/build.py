from pybin.buildlib import build_wheels
from pybin.platform_tags import *

NAME = 'gh'
UPSTREAM_REPO = "https://github.com/cli/cli"
VERSION = '2.83.1'
PYPI_VERSION = '2.83.1'
LICENSE = "MIT"

TARGET_TAG = {
    'macOS_arm64.zip': MACOS_ARM,
    'linux_arm64.tar.gz': LINUX_ARM,
    'macOS_amd64.zip': MACOS_X86,
    'linux_amd64.tar.gz': LINUX_X86,
}
URL_TAG = {f"{UPSTREAM_REPO}/releases/download/v{VERSION}/{NAME}_{VERSION}_{target}": tag for target, tag in TARGET_TAG.items()}


if __name__ == "__main__":
    build_wheels(
        NAME,
        PYPI_VERSION,
        URL_TAG,
        UPSTREAM_REPO,
        LICENSE,
        )
