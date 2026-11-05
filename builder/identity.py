# Preserve Debian vendor identity through a diversion before writing the AmogOS release files.
from common import chroot,write


def configure(root):
    chroot(root,['dpkg-divert','--local','--rename','--add','/usr/lib/os-release'])
    write(root,'usr/lib/os-release','PRETTY_NAME="AmogOS 2 Pro 2.1 (toppat)"\nNAME="AmogOS 2 Pro"\nVERSION_ID="2.1"\nOS_VERSION="2.1"\nVERSION="2.1 (toppat)"\nID=amogos\nID_LIKE=debian\nHOME_URL="https://amogosbuild.github.io"\n')
    release=root/'etc/os-release'
    release.unlink(missing_ok=True)
    release.symlink_to('../usr/lib/os-release')
    write(root,'etc/amogos-release','2.1\n')
    write(root,'etc/lsb-release','DISTRIB_ID=AmogOS\nDISTRIB_RELEASE=2.1\nDISTRIB_CODENAME=toppat\nDISTRIB_DESCRIPTION="AmogOS 2 Pro 2.1 (toppat)"\n')
    write(root,'etc/issue','AmogOS 2 Pro 2.1 (toppat) \\n \\l\n\n')
    write(root,'etc/issue.net','AmogOS 2 Pro 2.1 (toppat)\n')
