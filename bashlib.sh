
HERE=$( cd "$(dirname "$BASH_SOURCE")" && pwd -P )

echobye() {
    >&2 echo -e "$*"
    exit 0
}

echoerr() { 
    >&2 echo -e "$(tput setaf 1)$*$(tput sgr0)"
    exit 1
}

require() {
    [ -n "$(which "$1" 2>/dev/null)" ] || echoerr "Command missing: ${2:-1}"
}
