import sys
from pathlib import Path

from pybin.update import update_rules


def main(rules_directory: Path) -> None:
    update_rules(rules_directory)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/update.py <rules_directory>", file=sys.stderr)
        sys.exit(1)
    main(Path(sys.argv[1]))
