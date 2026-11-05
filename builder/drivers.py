# Bundle authenticated NVIDIA and Broadcom packages with a manifest used by offline installation.
import json
from common import chroot
from sources import digest

GROUPS={'nvidia-driver':['nvidia-driver','nvidia-kernel-dkms','nvidia-driver-libs:i386'],'nvidia-tesla-535-driver':['nvidia-tesla-535-driver','nvidia-tesla-535-kernel-dkms','nvidia-tesla-535-driver-libs:i386'],'broadcom-sta-dkms':['broadcom-sta-dkms']}


def cache(root):
    directory=root/'usr/share/amogos/offline-drivers'
    (directory/'archives/partial').mkdir(parents=True)
    for packages in GROUPS.values():
        chroot(root,['apt-get','install','-y','--no-remove','--no-install-recommends','--download-only','--reinstall','-o','Dir::Cache::archives=/usr/share/amogos/offline-drivers/archives/',*packages])
    packages=[]
    for path in sorted((directory/'archives').glob('*.deb')):
        values=chroot(root,['dpkg-deb','-f','/usr/share/amogos/offline-drivers/archives/'+path.name,'Package','Version','Architecture'],text=True,stdout=-1).stdout
        fields=dict(line.split(': ',1) for line in values.splitlines())
        packages.append(dict(file=path.name,package=fields['Package'],version=fields['Version'],architecture=fields['Architecture'],sha256=digest(path),bytes=path.stat().st_size))
    (directory/'manifest.json').write_text(json.dumps(dict(schema=1,source='Debian authenticated APT repositories',groups=GROUPS,packages=packages),indent=2)+'\n')
    for path in directory.rglob('*'):
        path.chmod(0o755 if path.is_dir() else 0o644)
