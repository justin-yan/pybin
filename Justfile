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
    echo "Building {{APP_NAME}} from YAML config"
    uv run --no-sync python scripts/build_from_yaml.py tools/{{APP_NAME}}.yaml

# Legacy build using build.py scripts (for conformance testing)
@_build-legacy APP_NAME: init
    echo "Building {{APP_NAME}} using legacy build.py"
    uv run --no-sync python -m pybin.{{APP_NAME}}.build

@register:
    git diff --name-only HEAD^1 HEAD -G"^pypi_version:" "tools/*.yaml" | xargs -n1 basename | sed 's/\.yaml$//' | xargs -I {} sh -c 'just _register {}'

@_register APP_NAME: init (build APP_NAME)
    uv run --no-sync twine upload -u $PYPI_USERNAME -p $PYPI_PASSWORD {{APP_NAME}}-dist/*

@update: init
    uv run --no-sync python scripts/update.py {{justfile_directory()}}/tools

@test:
    uv run pytest tests

compare-build APP_NAME: init
    #!/usr/bin/env bash
    set -e
    echo "=== Building {{APP_NAME}} using build.py (legacy) ==="
    just _build-legacy "{{APP_NAME}}"
    mv "{{APP_NAME}}-dist" "{{APP_NAME}}-dist-old"

    echo "=== Building {{APP_NAME}} using YAML config (new) ==="
    just build "{{APP_NAME}}"
    mv "{{APP_NAME}}-dist" "{{APP_NAME}}-dist-new"

    echo "=== Comparing wheel files ==="
    old_wheels=$(ls "{{APP_NAME}}-dist-old"/*.whl | xargs -n1 basename | sort)
    new_wheels=$(ls "{{APP_NAME}}-dist-new"/*.whl | xargs -n1 basename | sort)

    if [ "$old_wheels" != "$new_wheels" ]; then
        echo "ERROR: Wheel filenames differ"
        echo "Old: $old_wheels"
        echo "New: $new_wheels"
        exit 1
    fi

    all_match=true
    for wheel in $old_wheels; do
        old_size=$(stat -c%s "{{APP_NAME}}-dist-old/$wheel" 2>/dev/null || stat -f%z "{{APP_NAME}}-dist-old/$wheel")
        new_size=$(stat -c%s "{{APP_NAME}}-dist-new/$wheel" 2>/dev/null || stat -f%z "{{APP_NAME}}-dist-new/$wheel")
        if [ "$old_size" = "$new_size" ]; then
            echo "✓ $wheel: sizes match ($old_size bytes)"
        else
            echo "✗ $wheel: sizes differ (old=$old_size, new=$new_size)"
            all_match=false
        fi
    done

    # Cleanup
    rm -rf "{{APP_NAME}}-dist-old" "{{APP_NAME}}-dist-new"

    if [ "$all_match" = true ]; then
        echo "=== All wheels match! ==="
    else
        echo "=== Some wheels differ ==="
        exit 1
    fi

compare-build-all: init
    #!/usr/bin/env bash
    set -e
    for tool in caddy codex copilot dbmate dive fastfetch gh hadolint just lazydocker litestream rclone scc temporal traefik usql; do
        echo "========================================"
        echo "Testing: $tool"
        echo "========================================"
        just compare-build "$tool"
    done
    echo "========================================"
    echo "ALL TOOLS PASSED"
    echo "========================================"

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
