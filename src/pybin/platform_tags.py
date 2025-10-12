"""
Standardizing platform compatibility tags for common build targets.

References:
- https://packaging.python.org/en/latest/specifications/platform-compatibility-tags/
"""

LINUX_X86 = "manylinux2014_x86_64.musllinux_1_1_x86_64"
LINUX_ARM = "manylinux2014_aarch64.musllinux_1_1_aarch64"

MACOS_X86 = "macosx_10_9_x86_64"
MACOS_ARM = "macosx_11_0_arm64"  # Big Sur first version to support apple silicon
