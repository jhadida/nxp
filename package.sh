#!/usr/bin/env bash

if [ -n "$1" ]; then
    Token=.token-pypi-test.enc
    Args=(
        --skip-existing
        --repository-url 'https://test.pypi.org/legacy/'
    )
else
    Token=.token-pypi.enc
    Args=()
fi

Token=$(openssl enc -aes-256-cbc -md sha512 -pbkdf2 -iter 10000 -salt -d -in "$Token")
Args=(
    --username '__token__'
    --password "$Token"
    "${Args[@]}"
)

# cleanup
rm -rf build dist *.egg-info

# rebuild
python3 setup.py sdist bdist_wheel
python3 -m twine upload "${Args[@]}" dist/*
