#!/bin/sh
set -eu
chmod 0755 /
sed -i 's/^#en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen
locale-gen
printf 'LANG=en_US.UTF-8\n' > /etc/locale.conf
printf 'amogos-arch\n' > /etc/hostname
passwd --lock root
rm -rf -- /etc/pacman.d/gnupg
systemctl enable NetworkManager sddm amogos-arch-live amogos-arch-onboarding-finish systemd-timesyncd
systemctl set-default graphical.target
mkinitcpio -p linux-zen
