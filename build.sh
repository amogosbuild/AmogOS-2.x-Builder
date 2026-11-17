#!/bin/bash
set -euo pipefail
root="$(cd "$(dirname "$0")" && pwd)"
case "${1:-}" in
    amogos-arch|arch)
        shift
        if [[ ${1:-} != --check ]]; then
            exec "$root/amogos-arch/build-x86_64.sh" "$@"
        fi
        ;;
esac
exec python3 "$root/builder/cli.py" "$@"
