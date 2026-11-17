#!/usr/bin/env bash
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
work="$here/../.work/arch-$(date -u +%Y%m%dT%H%M%SZ)"
output="$here/../out"
package_repository=
while (( $# )); do
    case "$1" in
        --work-dir) work=$2; shift 2 ;;
        --output-dir) output=$2; shift 2 ;;
        --package-repository) package_repository=$2; shift 2 ;;
        --help)
            echo "Usage: sudo $0 [--work-dir DIR] [--output-dir DIR] [--package-repository SIGNED_REPO_DIR]"
            exit 0 ;;
        *) echo "Unknown option: $1" >&2; exit 2 ;;
    esac
done
[[ $EUID == 0 && $(uname -m) == x86_64 ]] || { echo 'Run on an x86_64 Arch build host as root.' >&2; exit 1; }
command -v mkarchiso >/dev/null
work=$(realpath -m "$work")
output=$(realpath -m "$output")
[[ $work != / && $output != / && $work != "$output" && ! -e $work ]] || { echo 'Use a new work folder and a separate output folder.' >&2; exit 1; }
mkdir -p "$work/profile" "$output"
cp -a "$here/amogosiso/." "$work/profile/"
bash "$here/scripts/trust.sh" "$work/trust" "$work/profile/airootfs/usr/share/pacman/keyrings/amogos-arch.gpg"
if [[ -n $package_repository ]]; then
    package_repository=$(realpath -e "$package_repository")
    [[ -f $package_repository/amogos-arch.db && -f $package_repository/amogos-arch.db.sig ]]
    python3 - "$work/profile/pacman.conf" "$package_repository" <<'PY'
import pathlib
import sys
path=pathlib.Path(sys.argv[1])
local=pathlib.Path(sys.argv[2]).as_uri()
path.write_text(path.read_text().replace('https://amogosbuild.github.io/amogos-arch/x86_64',local))
PY
fi
mkarchiso -v -w "$work/archiso" -o "$output" "$work/profile"
