from pybin.buildlib import build_wheels
from pybin.platform_tags import *

NAME = 'atuin'
UPSTREAM_REPO = "https://github.com/atuinsh/atuin"
VERSION = '18.10.0'
PYPI_VERSION = '18.10.0'
LICENSE = "MIT"

TARGET_TAG = {
    'aarch64-apple-darwin.tar.gz': MACOS_ARM,
    'x86_64-apple-darwin.tar.gz': MACOS_X86,
    'aarch64-unknown-linux-gnu.tar.gz': LINUX_GNU_ARM,
    'x86_64-unknown-linux-gnu.tar.gz': LINUX_GNU_X86,
    'aarch64-unknown-linux-musl.tar.gz': LINUX_MUSL_ARM,
    'x86_64-unknown-linux-musl.tar.gz': LINUX_MUSL_X86,
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
