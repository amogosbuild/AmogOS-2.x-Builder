#!/bin/sh
set -eu
chmod 0755 /
sed -i 's/^#en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen
locale-gen
printf 'LANG=en_US.UTF-8\n' > /etc/locale.conf
printf 'amogos-arch\n' > /etc/hostname
ln -sfn /usr/share/zoneinfo/UTC /etc/localtime
passwd --lock root
rm -rf -- /etc/pacman.d/gnupg
install -d /usr/share/amogos-arch/pacman-sync
for index in /var/lib/pacman/sync/*.db /var/lib/pacman/sync/*.db.sig; do
    [ -f "$index" ] || continue
    install -m0644 "$index" /usr/share/amogos-arch/pacman-sync/
done
systemctl enable NetworkManager amogos-arch-catalog sddm amogos-arch-live amogos-arch-onboarding-finish systemd-timesyncd
systemctl set-default graphical.target
mkinitcpio -p linux-zen
