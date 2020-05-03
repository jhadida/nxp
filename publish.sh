#!/usr/bin/env bash

source bashlib.sh

usage() {
cat <<EOF
Publish package to PyPI, and tagged version to Github.

    ./publish.sh <Version> -m <Message>

The version should follow the semver format (https://semver.org/).

Checklist before you publish:

1. package.json accurate?
2. Did you include a LICENSE.txt (see 'jhtpl license')?
3. setup.py up-to-date (classifiers, JSON fields renaming, 'packages' field, etc.)?
4. Did you commit all changes in this repository?
5. Did you update the release notes in README.md?
6. If there were notable changes, have you updated CHANGELOG.md?
7. Are you in the master branch?

If no encrypted token is available (see token.sh utility), the publishing
tool will prompt for a username/password for the account on PyPI. This is
normal the first time you publish.

After the first publish, you may want to create a Personal Access Token 
with limited access for this project only (see token.sh for the steps to
follow). This is safer than using a username/password.

EOF
exit 0
}

# ------------------------------------------------------------------------

[ $# -lt 3 ] && usage "Not enough inputs"
[[ $2 != '-m' ]] && usage "Second argument should be '-m'"
Version=$1
shift

# decrypt token if any
Token=$(./token.sh get)
if [ -n "$Token" ]; then
    Args=(
        --username '__token__' 
        --password "$Token"
    )
else 
    Args=()
fi

# cleanup
rm -rf build dist *.egg-info src/*.egg-info

# update version
echo "$Version" >| version.txt
git commit version.txt "$@" || echoerr "Failed to commit"
git tag "v$Version" "$@" || echoerr "Failed to create tag"
git push origin master --tags || echoerr "Failed to push to Github"

# rebuild
python3 setup.py sdist bdist_wheel || echoerr "Failed to build package"
python3 -m twine upload "${Args[@]}" dist/*
