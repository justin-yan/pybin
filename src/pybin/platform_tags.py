"""
Standardizing platform compatibility tags for common build targets.

References:
- https://packaging.python.org/en/latest/specifications/platform-compatibility-tags/

A quick summary of the key points:

- Platform specifiers typially encode OS, stdlib version (glibc, musl), and architecture.
- For the most part, built binaries in release artifacts are assumed to be pretty broadly compatible.
- As such, we want to define standard tag sets that will match common build configurations as broadly as possible.

For linux: We use the `manylinux` tag instead of configuring a minimum glibc version, and then have arch-specific tags.
For mac: We use relatively old macos versions and have architecture-specific versions as well as the option for a mac universal binary
"""

LINUX_X86 = "manylinux2014_x86_64.musllinux_1_1_x86_64"
LINUX_ARM = "manylinux2014_aarch64.musllinux_1_1_aarch64"

MACOS_X86 = "macosx_10_9_x86_64"
MACOS_ARM = "macosx_11_0_arm64"  # Big Sur first version to support apple silicon
MACOS_UNIVERSAL = "macosx_11_0_universal2"  # Big Sur first version to support apple silicon
