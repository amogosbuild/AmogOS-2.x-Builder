#!/usr/bin/env bash
iso_name="AmogOS-2-Pro-Arch"
iso_label="AMOGOS_ARCH_$(date -u --date="@${SOURCE_DATE_EPOCH:-$(date +%s)}" +%Y%m)"
iso_publisher="AmogOS"
iso_application="AmogOS 2 Pro (Arch)"
iso_version="$(date -u --date="@${SOURCE_DATE_EPOCH:-$(date +%s)}" +%Y.%m.%d)"
install_dir="amogos"
buildmodes=('iso')
bootmodes=('bios.syslinux' 'uefi.grub')
pacman_conf="pacman.conf"
airootfs_image_type="squashfs"
airootfs_image_tool_options=('-comp' 'zstd' '-Xcompression-level' '8' '-b' '256K' '-processors' '4')
file_permissions=(
    ["/usr/lib/amogos-arch/live-session"]="0:0:755"
    ["/usr/lib/amogos-arch/seed-catalog"]="0:0:755"
    ["/etc/skel/Desktop/amogosarch.installer.desktop"]="0:0:755"
)
