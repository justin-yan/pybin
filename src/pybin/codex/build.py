from pybin.buildlib import build_wheels
from pybin.platform_tags import *

NAME = 'codex'
UPSTREAM_REPO = "https://github.com/openai/codex"
VERSION = '0.65.0'
PYPI_VERSION = '0.65.0'
LICENSE = "Apache-2.0"

TARGET_TAG = {
    'aarch64-apple-darwin': MACOS_ARM,
    'x86_64-apple-darwin': MACOS_X86,
    'aarch64-unknown-linux-gnu': LINUX_GNU_ARM,
    'aarch64-unknown-linux-musl': LINUX_MUSL_ARM,
    'x86_64-unknown-linux-gnu': LINUX_GNU_X86,
    'x86_64-unknown-linux-musl': LINUX_MUSL_X86,
}
URL_TAG = {f"{UPSTREAM_REPO}/releases/download/rust-v{VERSION}/{NAME}-{target}.tar.gz": tag for target, tag in TARGET_TAG.items()}

if __name__ == "__main__":
    build_wheels(
        NAME,
        PYPI_VERSION,
        URL_TAG,
        UPSTREAM_REPO,
        LICENSE,
        )
