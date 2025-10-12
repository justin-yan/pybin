from pybin.buildlib import build_wheels
from pybin.platform_tags import *

NAME = 'hadolint'
UPSTREAM_REPO = 'https://github.com/hadolint/hadolint'
VERSION = '2.14.0'
PYPI_VERSION = '2.14.0'
LICENSE = "GPLv3"

TARGET_TAG = {
    'macos-arm64': MACOS_ARM,
    'macos-x86_64': MACOS_X86,
    'linux-arm64': LINUX_ARM,
    'linux-x86_64': LINUX_X86,
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
