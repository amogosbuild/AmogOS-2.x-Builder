# Install authenticated Debian dependencies and the exact locked AmogOS application packages.
import shutil
from common import chroot,write


def install(repository,root,archive,lock):
    staging=root/'var/tmp/amogos-packages'
    staging.mkdir()
    for package in lock['packages']:
        shutil.copyfile(archive/package['filename'],staging/package['filename'].rsplit('/',1)[-1])
    keyring=next(package for package in lock['packages'] if package['package']=='amogos-archive-keyring')
    chroot(root,['dpkg','-i','/var/tmp/amogos-packages/'+keyring['filename'].rsplit('/',1)[-1]])
    chroot(root,['dpkg','--add-architecture','i386'])
    chroot(root,['apt-get','-o','APT::Update::Error-Mode=any','update'])
    chroot(root,['debconf-set-selections'],input='firmware-ipw2x00 firmware-ipw2x00/license/accepted boolean true\n',text=True)
    names=[]
    for filename in ('desktop.list','hardware.list'):
        names.extend(line for line in (repository/'amogos-debian/packages'/filename).read_text().splitlines() if line and not line.startswith('#'))
    packages=['/var/tmp/amogos-packages/'+package['filename'].rsplit('/',1)[-1] for package in lock['packages'] if package['package']!='amogos-archive-keyring']
    chroot(root,['apt-get','install','-y','--no-remove','--no-install-recommends',*names,*packages])
    chroot(root,['apt-mark','manual','linux-image-amd64','linux-headers-amd64','amogos-update','amogos-system','amogos-store','steam-installer','steam-devices'])
    for package in lock['packages']:
        actual=chroot(root,['dpkg-query','-W','-f=${Version}',package['package']],text=True,stdout=-1).stdout.strip()
        if actual!=package['version']:
            raise RuntimeError('Installed version differs from the lock: '+package['package'])
    chroot(root,['apt-get','check'])
    audit=chroot(root,['dpkg','--audit'],text=True,stdout=-1).stdout.strip()
    if audit:
        raise RuntimeError(audit)
    shutil.rmtree(staging)
