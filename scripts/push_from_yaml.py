import sys
from pathlib import Path

from pybin.sync import push


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python scripts/push_from_yaml.py <rule.yaml>", file=sys.stderr)
        sys.exit(1)

    rule_path = Path(sys.argv[1])
    if not rule_path.exists():
        print(f"Rule file not found: {rule_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Building and pushing from {rule_path}")
    push(rule_path)


if __name__ == "__main__":
    main()
