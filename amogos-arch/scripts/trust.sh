#!/usr/bin/env bash
set -euo pipefail
scratch=$1
amogos_key=$2
chaotic_fingerprint=EF925EA60F33D0CB85C44AD13056513887B78AEB
amogos_fingerprint=A5151F6594788958DC6D22ACFF0C180F04849F27
mkdir -p "$scratch"
curl --fail --silent --show-error --retry 2 \
    "https://keyserver.ubuntu.com/pks/lookup?op=get&search=0x$chaotic_fingerprint" \
    -o "$scratch/chaotic.asc"
for input in "$scratch/chaotic.asc:$chaotic_fingerprint" "$amogos_key:$amogos_fingerprint"; do
    file=${input%:*}
    expected=${input##*:}
    actual=$(gpg --batch --show-keys --with-colons "$file" | awk -F: '$1=="fpr" {print $10;exit}')
    test "$actual" = "$expected"
    pacman-key --add "$file"
    pacman-key --lsign-key "$expected"
done
for package in chaotic-keyring chaotic-mirrorlist; do
    source="https://cdn-mirror.chaotic.cx/chaotic-aur/$package.pkg.tar.zst"
    curl -fLsS --retry 2 "$source" -o "$scratch/$package.pkg.tar.zst"
    curl -fLsS --retry 2 "$source.sig" -o "$scratch/$package.pkg.tar.zst.sig"
    pacman-key --verify "$scratch/$package.pkg.tar.zst.sig" "$scratch/$package.pkg.tar.zst"
done
pacman -U --needed --noconfirm -- "$scratch/chaotic-keyring.pkg.tar.zst" "$scratch/chaotic-mirrorlist.pkg.tar.zst"
pacman-key --populate chaotic
