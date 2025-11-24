from pybin.buildlib import build_wheels
from pybin.platform_tags import *

NAME = 'lazydocker'
UPSTREAM_REPO = 'https://github.com/jesseduffield/lazydocker'
VERSION = '0.24.2'
PYPI_VERSION = '0.24.2'
LICENSE = "MIT"

TARGET_TAG = {
    'Darwin_arm64': MACOS_ARM,
    'Darwin_x86_64': MACOS_X86,
    'Linux_arm64': LINUX_ARM,
    'Linux_x86_64': LINUX_X86,
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
