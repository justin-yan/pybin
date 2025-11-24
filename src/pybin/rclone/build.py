from pybin.buildlib import build_wheels
from pybin.platform_tags import *

NAME = 'rclone'
UPSTREAM_REPO = 'https://github.com/rclone/rclone'
VERSION = '1.72.0'
PYPI_VERSION = '1.72.0'
LICENSE = "MIT"

TARGET_TAG = {
    'osx-arm64': MACOS_ARM,
    'osx-amd64': MACOS_X86,
    'linux-arm': LINUX_ARM,
    'linux-amd64': LINUX_X86,
}
URL_TAG = {f"{UPSTREAM_REPO}/releases/download/v{VERSION}/{NAME}-v{VERSION}-{target}.zip": tag for target, tag in TARGET_TAG.items()}

if __name__ == "__main__":
    build_wheels(
        NAME,
        PYPI_VERSION,
        URL_TAG,
        UPSTREAM_REPO,
        LICENSE,
        )
