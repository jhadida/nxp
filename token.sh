#!/usr/bin/env bash

source bashlib.sh

# check openssl is installed
require openssl
algo() { openssl enc -aes-256-cbc -md sha512 -pbkdf2 -iter 10000 -salt "$@"; }
Target=.token.enc

# nice usage message
usage() {
cat <<EOF
Token management utility, using openssl.

    ./token.sh <Command> <Args...>

Commands (prompts for encryption password):

    set <Token>
        Encrypt input token and save as '$Target'.
        Prompts for encryption password (do NOT use your sudo password).

    get     
        Echo decrypted token to console.
        Prompts for encryption password used with 'set' command.

Information:

    To obtain a token for your project, follow these steps:

    1. Create a user account on: https://pypi.org/
    2. Login and go to: Account Settings > API tokens > Add API token
    3. Create a token for your project (only after the first publish)
    4. Copy the secret token to clipboard, and call: 
        ./token.sh set <Token>

EOF
exit 0
}

# ------------------------------------------------------------------------

[ $# -lt 1 ] && usage
Command=$1
shift

case $Command in 
    get|dec*)
        [ -f "$Target" ] || echoerr "No token found; did you previously call the 'set' command?"
        algo -d -in "$Target"
        ;;
    set|enc*)
        echo "$1" | algo -out "$Target"
        ;;
    *)
        echoerr "Unknown command: $Command"
        ;;
esac
