# Apply the complete desktop profile and live-session configuration before generating boot assets.
import pathlib
import re
import shutil
from common import chroot,copy_tree,write


def configure(repository,root,archive):
    copy_tree(repository/'shared/overlay',root)
    copy_tree(repository/'amogos-debian/overlay',root)
    for path in (root/'etc/xdg').glob('*'):
        if path.is_file():
            destination=root/'etc/skel/.config'/path.name
            destination.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(path,destination)
    for name in ('amogos.installer.desktop','amogos.appstore.desktop','amogos.music.desktop','amogos.notes.desktop','amogos-calamares-fallback.desktop'):
        source=root/'usr/share/applications'/name
        destination=root/'etc/skel/Desktop'/name
        destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,destination)
        destination.chmod(0o755)
    theme=root/'usr/share/plasma/look-and-feel/org.amogos.desktop/contents/previews/preview.png'
    theme.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(root/'usr/share/wallpapers/AmogOSEngine/img1.png',theme)
    provenance=archive/'app-sources/amogos-store/third_party/ASSETS.md'
    shutil.copyfile(provenance,root/'usr/share/doc/amogos-store/ASSETS.md')
    with (root/'etc/bash.bashrc').open('a') as stream:
        stream.write('\nif [ -r /etc/amogos/bash/fastfetch.sh ]; then . /etc/amogos/bash/fastfetch.sh; fi\n')
    write(root,'etc/locale.gen','en_US.UTF-8 UTF-8\nen_GB.UTF-8 UTF-8\n')
    write(root,'etc/locale.conf','LANG=en_US.UTF-8\n')
    write(root,'etc/hostname','amogos\n')
    write(root,'etc/hosts','127.0.0.1 localhost\n127.0.1.1 amogos\n::1 localhost ip6-localhost\n')
    chroot(root,['locale-gen'])
    chroot(root,['systemctl','enable','sddm','NetworkManager','amogos-root-ownership','amogos-live-shortcuts','amogos-installed-cleanup'])
    chroot(root,['systemctl','set-default','graphical.target'])
    chroot(root,['plymouth-set-default-theme','amogos2pro'])
    for name in ('usr/local/bin/amogos-calamares-fallback','usr/local/libexec/amogos-live-shortcuts','etc/initramfs-tools/hooks/amogos-broadcom'):
        (root/name).chmod(0o755)
    for config,name,value in [('org.kde.plasma.taskmanager','launchers','applications:org.kde.dolphin.desktop,applications:firefox-esr.desktop,applications:amogos.music.desktop'),('org.kde.plasma.kickoff','icon','/usr/share/pixmaps/amogos-menu.png')]:
        path=root/'usr/share/plasma/plasmoids'/config/'contents/config/main.xml'
        pattern=r'(<entry name="'+name+r'" type="[^"]+">.*?<default>).*?(</default>)'
        content,count=re.subn(pattern,lambda match:match[1]+value+match[2],path.read_text(),flags=re.S)
        if count!=1:
            raise RuntimeError('Plasma default layout changed upstream: '+config)
        path.write_text(content)
    chroot(root,['update-initramfs','-u','-k','all'])


def finalize(root):
    chroot(root,['apt-get','clean'])
    chroot(root,['systemd-hwdb','update'])
    chroot(root,['journalctl','--update-catalog'])
    chroot(root,['ldconfig'])
    for name in ('var/lib/dkms/mok.key','var/lib/dkms/mok.pub','var/cache/apt/pkgcache.bin','var/cache/apt/srcpkgcache.bin','root/.bash_history','usr/sbin/policy-rc.d'):
        (root/name).unlink(missing_ok=True)
    for path in (root/'etc/ssh').glob('ssh_host_*'):
        path.unlink()
    machine=root/'etc/machine-id'
    machine.unlink(missing_ok=True)
    machine.write_text('')
