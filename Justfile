######
### Project Variables
######
NAME := "pybin"
DEV_IMAGE:='ghcr.io/justin-yan/image/dev-all:latest'

######
### Python Variables
######
SRC_FOLDER:='src'
TEST_FOLDER:='tests'


@default:
    just --list

######
### Environment
######
@init:
    uv lock --check-exists && echo "Lockfile already exists" || just lock
    just sync

@run +COMMAND:
    uv run --no-sync {{COMMAND}}

@shell:
    #!/usr/bin/env bash
    pipenv shell

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

@repl:
    uv run --no-sync python

######
### LintCycle
######
@lint:
    uv run --no-sync ruff check {{SRC_FOLDER}} {{TEST_FOLDER}}
    uv run --no-sync ruff format --check {{SRC_FOLDER}} {{TEST_FOLDER}}

@typecheck:
    uv run --no-sync mypy --explicit-package-bases -p {{NAME}}
    uv run --no-sync mypy --allow-untyped-defs tests

# Run tests. Optionally specify a specific test target e.g. `just test tests/path/to/test.py::test_name`
@test TARGET=TEST_FOLDER:
    uv run --no-sync pytest {{TARGET}}

@format:
    uv run --no-sync ruff check --fix-only {{SRC_FOLDER}} {{TEST_FOLDER}}
    uv run --no-sync ruff format {{SRC_FOLDER}} {{TEST_FOLDER}}

@stats:
    uv run --no-sync coverage run -m pytest {{TEST_FOLDER}}
    uv run --no-sync coverage report -m
    scc --by-file --include-ext py

@verify: lint typecheck test
    echo "Done with Verification"

# Run tests with a specific mark e.g. `just testmark slow`
testmark MARK="" TARGET=TEST_FOLDER:
    #!/usr/bin/env bash
    set -euo pipefail
    uv run --no-sync pytest -m '{{MARK}}' {{TARGET}}

######
### Virt
######
@virt +COMMAND:
    #!/usr/bin/env bash
    set -euo pipefail

    project_dir={{quote(justfile_directory())}}
    python="$("$project_dir/.venv/bin/python" -c 'import os, sys; print(os.path.realpath(sys.executable))')"
    python_root="$(dirname "$(dirname "$python")")"

    docker run -it --rm \
        --name "{{NAME}}-virt" \
        -v "$project_dir:$project_dir" \
        -v "$python_root:$python_root:ro" \
        -w "$project_dir" \
        {{DEV_IMAGE}} just {{COMMAND}}

######
### Development Cycle
######
@build APP_NAME: init
    echo "Building {{APP_NAME}}"
    uv run --no-sync python scripts/build_from_yaml.py rules/{{APP_NAME}}.yaml

@cicd-pr: init verify
    echo "PR is successful!"

@cicd-register:
    git diff --name-only HEAD^1 HEAD -G"^    version:" "rules/*.yaml" | xargs -n1 basename | sed 's/\.yaml$//' | xargs -I {} sh -c 'just _register {}'

@_register APP_NAME: init
    uv run --no-sync python scripts/sync_from_yaml.py rules/{{APP_NAME}}.yaml

######
### Custom Commands Section Begin
######

# Validate a single sync rule, e.g. `just validate codex`
@validate RULE: init
    just testmark integration "tests/integration/test_validation.py::test_rule_builds_installable_wheels[{{RULE}}]"

@update: init
    uv run --no-sync python scripts/update.py {{justfile_directory()}}/rules

######
### Custom Commands Section End
######
