from pybin.buildlib import build_wheels
from pybin.platform_tags import *

NAME = 'caddy'
UPSTREAM_REPO = "https://github.com/caddyserver/caddy"
VERSION = '2.10.2'
PYPI_VERSION = '2.10.2'
LICENSE = "Apache-2.0"

TARGET_TAG = {
    'mac_arm64': MACOS_ARM,
    'linux_arm64': LINUX_ARM,
    'mac_amd64': MACOS_X86,
    'linux_amd64': LINUX_X86,
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
