#!/usr/bin/env bash

[ $# -lt 3 ] && { echo "Usage: $0 <Version> -m <Message>"; exit 1; }

Version=$1
shift

TEST=0
if (( $TEST == 1 )); then
    Token=.token-test.enc
    Args=(
        --skip-existing
        --repository-url 'https://test.pypi.org/legacy/'
    )
else
    Token=.token.enc
    Args=()
fi

Token=$(openssl enc -aes-256-cbc -md sha512 -pbkdf2 -iter 10000 -salt -d -in "$Token")
Args=(
    --username '__token__'
    --password "$Token"
    "${Args[@]}"
)

# cleanup
rm -rf build dist *.egg-info src/*.egg-info

# update version
echo "$Version" >| version.txt
git commit -a "$@" || { echo "Failed to commit"; exit 1; }
git tag "v$Version" "$@" || { echo "Failed to create tag"; exit 1; }
git push --tags

# rebuild
python3 setup.py sdist bdist_wheel
python3 -m twine upload "${Args[@]}" dist/*
