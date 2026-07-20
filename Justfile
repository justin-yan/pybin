PACKAGE_NAME := "pybin"
SRC_FOLDER := "src"
TEST_FOLDER := "tests"

@default:
    just --list

@init:
    uv lock --check-exists && echo "Lockfile already exists" || just lock
    just sync

lock UPGRADE="noupgrade" PACKAGE="":
    #!/usr/bin/env bash
    set -euo pipefail
    if [ "{{UPGRADE}}" = "--upgrade" ] && [ -n "{{PACKAGE}}" ]; then
        uv lock --upgrade-package "{{PACKAGE}}"
    elif [ "{{UPGRADE}}" = "--upgrade" ] || [ "{{UPGRADE}}" = "-U" ]; then
        uv lock --upgrade
    else
        uv lock
    fi

sync FORCE="noforce":
    #!/usr/bin/env bash
    set -euo pipefail
    if [ "{{FORCE}}" = "--force" ]  || [ "{{FORCE}}" = "-f" ]; then
        rm -rf {{justfile_directory()}}/.venv
    fi
    uv sync --frozen

@build APP_NAME: init
    echo "Building {{APP_NAME}}"
    uv run --no-sync python scripts/build_from_yaml.py rules/{{APP_NAME}}.yaml

@register:
    git diff --name-only HEAD^1 HEAD -G"^    version:" "rules/*.yaml" | xargs -n1 basename | sed 's/\.yaml$//' | xargs -I {} sh -c 'just _register {}'

@_register APP_NAME: init (build APP_NAME)
    uv publish --trusted-publishing always {{APP_NAME}}-dist/*

@update: init
    uv run --no-sync python scripts/update.py {{justfile_directory()}}/rules

# Run tests. Optionally specify a specific test target e.g. `just test tests/path/to/test.py::test_name`
@test TARGET=TEST_FOLDER:
    uv run --no-sync pytest {{TARGET}}

# Run tests with a specific mark e.g. `just testmark slow`
testmark MARK="" TARGET=TEST_FOLDER:
    #!/usr/bin/env bash
    set -euo pipefail
    uv run --no-sync pytest -m '{{MARK}}' {{TARGET}}

@lint:
    uv run --no-sync ruff check {{SRC_FOLDER}} {{TEST_FOLDER}}
    uv run --no-sync ruff format --check {{SRC_FOLDER}} {{TEST_FOLDER}}

@format:
    uv run --no-sync ruff check --fix-only {{SRC_FOLDER}} {{TEST_FOLDER}}
    uv run --no-sync ruff format {{SRC_FOLDER}} {{TEST_FOLDER}}

@typecheck:
    uv run --no-sync mypy --explicit-package-bases -p {{PACKAGE_NAME}}
    uv run --no-sync mypy --allow-untyped-defs {{TEST_FOLDER}}

@run +COMMAND:
    uv run --no-sync {{COMMAND}}

@verify: lint typecheck test
    echo "Done with Verification"

@cicd-pr: init verify
    echo "PR is successful!"

########
### Custom Commands
########

# Validate a single sync rule, e.g. `just validate codex`
@validate RULE: init
    just testmark integration "tests/integration/test_validation.py::test_rule_builds_installable_wheels[{{RULE}}]"
