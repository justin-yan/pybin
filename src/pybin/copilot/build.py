from pybin.buildlib import build_wheels

NAME = 'copilot'
UPSTREAM_REPO = "https://github.com/aws/copilot-cli"
VERSION = '1.34.1'
PYPI_VERSION = '1.34.1'
LICENSE = "Apache-2.0"

TARGET_TAG = {
    'macOS_arm64': 'macosx_11_0_arm64',
    'linux_arm64': 'manylinux_2_17_aarch64.manylinux2014_aarch64.musllinux_1_1_aarch64',
    'macOS_amd64': 'macosx_10_9_x86_64',
    'linux_amd64': 'manylinux_2_12_x86_64.manylinux2010_x86_64.musllinux_1_1_x86_64',
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
