import sys
from pathlib import Path

from pybin.sync import load_rule


def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/build_from_yaml.py <rule.yaml>", file=sys.stderr)
        sys.exit(1)

    rule_path = Path(sys.argv[1])
    if not rule_path.exists():
        print(f"Rule file not found: {rule_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Building from {rule_path}")
    rule = load_rule(rule_path)
    release = rule.source()
    for target in rule.targets:
        target.build(release)


if __name__ == "__main__":
    main()
