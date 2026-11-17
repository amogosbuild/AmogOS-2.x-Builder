# AmogOS 2 Pro (Arch)

Build on an x86_64 Arch Linux host with a populated Arch signing keyring and
archiso, grub, dosfstools, python and curl installed.

    sudo pacman -Syu --needed archiso grub dosfstools python curl
    sudo ./build.sh amogos-arch

The profile includes Plasma for offline installations, linux-zen, firmware,
Intel and AMD graphics, NVIDIA DKMS with Zen headers, Broadcom DKMS, Steam,
AmogOS Music and Notes, and virtual-machine guest tools. During installation GNOME and LXQt are
downloaded from signed repositories. Plasma remains available as a fallback.
The desktop package supplies lightweight Plasma defaults and zstd compressed
swap. The profile copies the same settings into the user skeleton for live
and installed accounts.
The ISO boot menu supports BIOS through Syslinux and UEFI through GRUB, with
normal Plymouth, basic graphics and diagnostics entries.

The [AmogOS Arch Apps](https://github.com/amogosbuild/AmogOS-Arch-Apps)
repository provides separate source and Arch package recipes for the store,
installer, onboarding and system appearance. Packages come from the signed
[AmogOS Arch archive](https://amogosbuild.github.io/amogos-arch/). The installer
keeps the configured Arch, AmogOS and Chaotic-AUR repositories in the installed
system. Direct AUR builds are controlled separately in the store's settings.

For development with a signed package directory, pass
--package-repository /path/to/x86_64. The build uses that source while the
installer and live environment retain the public repository URL.

Profile layout and boot conventions were checked against the
[AmogOS GitLab builder](https://gitlab.com/amogos-2.x/Builder) and the Archiso
releng profile. See the Arch apps repository for the wallpaper and splash
artwork notice.
