# Bootstrap an empty Debian filesystem without copying an existing ISO or build server root.
import pathlib
from common import capture,run,write,require_tools

DEPENDENCIES=['python3','debootstrap','git','ca-certificates','gnupg','dpkg-dev','grub-pc-bin','grub-efi-amd64-bin','grub-common','xorriso','squashfs-tools','mtools','dosfstools','util-linux','file']


def prepare(work,install_dependencies):
    identity=pathlib.Path('/etc/os-release').read_text()
    if 'ID=debian' not in identity or 'VERSION_ID="13"' not in identity:
        raise RuntimeError('Native builds require Debian 13. Use --container on another distribution.')
    if install_dependencies:
        run(['apt-get','update'])
        run(['apt-get','install','-y','--no-install-recommends',*DEPENDENCIES])
    require_tools(['debootstrap','git','gpgv','dpkg-deb','grub-mkrescue','grub-script-check','xorriso','mksquashfs','unsquashfs','mount','umount','chroot'])
    root=work/'rootfs'
    root.mkdir(mode=0o755)
    run(['debootstrap','--arch=amd64','--variant=minbase','--include=ca-certificates,gnupg','trixie',root,'https://deb.debian.org/debian'])
    write(root,'usr/sbin/policy-rc.d','#!/bin/sh\nexit 101\n',0o755)
    write(root,'etc/apt/sources.list','deb https://deb.debian.org/debian trixie main contrib non-free non-free-firmware\ndeb https://deb.debian.org/debian trixie-updates main contrib non-free non-free-firmware\ndeb https://security.debian.org/debian-security trixie-security main contrib non-free non-free-firmware\n')
    write(root,'etc/apt/apt.conf.d/80amogos-build','Acquire::Retries "3";\nAcquire::Languages "none";\n')
    return root
