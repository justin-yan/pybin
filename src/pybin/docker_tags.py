"""Docker platform architecture mappings."""

DOCKER_AMD64 = "linux/amd64"
DOCKER_ARM64 = "linux/arm64"

DOCKER_ARCH_MAP = {
    "linux_arm": DOCKER_ARM64,
    "linux_x86": DOCKER_AMD64,
    "linux_gnu_arm": DOCKER_ARM64,
    "linux_gnu_x86": DOCKER_AMD64,
    "linux_musl_arm": DOCKER_ARM64,
    "linux_musl_x86": DOCKER_AMD64,
}


def get_docker_arch(platform_name: str) -> str | None:
    """Return Docker architecture for a symbolic platform name, or None if not Linux."""
    return DOCKER_ARCH_MAP.get(platform_name)
