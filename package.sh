#!/usr/bin/env bash

Token=${1:-.token-pypi.enc}
Token=$(openssl enc -aes-256-cbc -md sha512 -pbkdf2 -iter 10000 -salt -d -in "$Token")

# cleanup
rm -rf build dist *.egg-info

# rebuild
python3 setup.py sdist bdist_wheel
python3 -m twine upload --skip-existing --username '__token__' --password "$Token" --repository-url https://test.pypi.org/legacy/ dist/*
