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
    uv run --no-sync python scripts/build_from_yaml.py tools/{{APP_NAME}}.yaml

@register:
    git diff --name-only HEAD^1 HEAD -G"^pypi_version:" "tools/*.yaml" | xargs -n1 basename | sed 's/\.yaml$//' | xargs -I {} sh -c 'just _register {}'

@_register APP_NAME: init (build APP_NAME)
    uv publish --trusted-publishing always {{APP_NAME}}-dist/*

@update: init
    uv run --no-sync python scripts/update.py {{justfile_directory()}}/tools

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

@validate: init
    #!/usr/bin/env bash
    set -ex
    for yaml_file in {{justfile_directory()}}/tools/*.yaml; do
        app_name=$(basename "$yaml_file" .yaml)
        echo "Validating $app_name..."
        just build "$app_name"

        for wheel in "$app_name-dist/"*.whl; do
            if [ -f "$wheel" ]; then
                size=$(stat -c%s "$wheel" 2>/dev/null || stat -f%z "$wheel" 2>/dev/null)
                if [ "$size" -lt 500000 ]; then
                    echo "ERROR: $wheel is only $size bytes, suggesting no binary was properly downloaded"
                    exit 1
                fi
                echo "✓ $wheel is $(($size / 1048576))MB"
            fi
        done
        # Install the Linux x86 wheel
        wheel_file=$(ls "$app_name-dist/"*manylinux2014_x86_64*.whl 2>/dev/null | head -n1)
        if [ -n "$wheel_file" ]; then
            echo "Installing $wheel_file..."
            uv pip install --force-reinstall "$wheel_file"
        else
            echo "Warning: No Linux x86 wheel found for $app_name"
        fi
        # Clean up dist folder
        rm -rf "$app_name-dist"
    done
