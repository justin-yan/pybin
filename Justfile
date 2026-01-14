@default:
    just --list

@init:
    [ -f uv.lock ] && echo "Lockfile already exists" || just lock
    just sync

lock UPGRADE="noupgrade" PACKAGE="":
    #!/usr/bin/env bash
    if [ "{{UPGRADE}}" = "--upgrade" ] && [ -n "{{PACKAGE}}" ]; then
        uv lock --upgrade-package "{{PACKAGE}}"
    elif [ "{{UPGRADE}}" = "--upgrade" ] || [ "{{UPGRADE}}" = "-U" ]; then
        uv lock --upgrade
    else
        uv lock
    fi

sync FORCE="noforce":
    #!/usr/bin/env bash
    if [ "{{FORCE}}" = "--force" ]  || [ "{{FORCE}}" = "-f" ]; then
        rm -rf {{justfile_directory()}}/.venv
    fi
    uv sync --frozen

@build APP_NAME: init
    echo "Building {{APP_NAME}}"
    uv run --no-sync python scripts/build_from_yaml.py tools/{{APP_NAME}}.yaml

@build-docker APP_NAME: init
    echo "Building Docker images for {{APP_NAME}}"
    uv run --no-sync python scripts/build_docker.py tools/{{APP_NAME}}.yaml

@push-docker APP_NAME: init
    echo "Building and pushing Docker images for {{APP_NAME}}"
    uv run --no-sync python scripts/build_docker.py tools/{{APP_NAME}}.yaml --push

@register:
    git diff --name-only HEAD^1 HEAD -G"^pypi_version:" "tools/*.yaml" | xargs -n1 basename | sed 's/\.yaml$//' | xargs -I {} sh -c 'just _register {}'

@_register APP_NAME: init (build APP_NAME)
    uv run --no-sync twine upload -u $PYPI_USERNAME -p $PYPI_PASSWORD {{APP_NAME}}-dist/*

@register-docker:
    git diff --name-only HEAD^1 HEAD -G"^pypi_version:" "tools/*.yaml" | xargs -n1 basename | sed 's/\.yaml$//' | xargs -I {} sh -c 'just push-docker {}'

@update: init
    uv run --no-sync python scripts/update.py {{justfile_directory()}}/tools

@test:
    uv run pytest tests

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
