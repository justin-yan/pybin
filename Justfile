@default:
    just --list

@init:
    [ -f Pipfile.lock ] && echo "Lockfile already exists" || PIPENV_VENV_IN_PROJECT=1 pipenv lock
    PIPENV_VENV_IN_PROJECT=1 pipenv sync --dev

@build APP_NAME: init
    pipenv run python -m pybin.{{APP_NAME}}.build

@register:
    git diff --name-only HEAD^1 HEAD -G"^PYPI_VERSION =" "*build.py" | uniq | xargs -n1 dirname | xargs -n1 basename | xargs -I {} sh -c 'just _register {}'

@_register APP_NAME: init (build APP_NAME)
    pipenv run twine upload -u $PYPI_USERNAME -p $PYPI_PASSWORD {{APP_NAME}}-dist/*

@update: init
    pipenv run python -m pybin.update
