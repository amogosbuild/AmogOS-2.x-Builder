# Pack a verified root and assemble one GRUB hybrid image for BIOS and UEFI boot.
import json
import os
import pathlib
import re
import shutil
import stat
from common import capture,run
from sources import digest


def verify_root(root):
    info=root.lstat()
    if not stat.S_ISDIR(info.st_mode) or (info.st_uid,info.st_gid,stat.S_IMODE(info.st_mode))!=(0,0,0o755):
        raise RuntimeError('Root filesystem must be a directory owned by root:root with mode 0755.')


def build(repository,work,root,output,lock):
    verify_root(root)
    tree=work/'iso-tree'
    (tree/'live').mkdir(parents=True)
    (tree/'boot/grub').mkdir(parents=True)
    kernels=list((root/'boot').glob('vmlinuz-*'))
    if not kernels:
        raise RuntimeError('The root contains no kernel.')
    kernel=sorted(kernels,key=lambda path:path.stat().st_mtime_ns)[-1]
    version=kernel.name.removeprefix('vmlinuz-')
    if not (root/'lib/modules'/version).is_dir():
        raise RuntimeError('Kernel and module tree do not match.')
    shutil.copyfile(kernel,tree/'live/vmlinuz')
    shutil.copyfile(root/'boot'/('initrd.img-'+version),tree/'live/initrd')
    (tree/'live/kernel-version').write_text(version+'\n')
    shutil.copyfile(repository/'amogos-debian/boot/grub.cfg',tree/'boot/grub/grub.cfg')
    run(['grub-script-check',tree/'boot/grub/grub.cfg'])
    run(['mksquashfs',root,tree/'live/filesystem.squashfs','-noappend','-comp','zstd','-b','262144','-Xcompression-level','15','-processors','4','-mem','2G','-no-progress'])
    listing=capture(['unsquashfs','-lln','-max-depth','0',tree/'live/filesystem.squashfs'])
    if not any(re.match(r'^drwxr-xr-x\s+0/0\s',line) for line in listing.splitlines()):
        raise RuntimeError('Packed filesystem root ownership is incorrect.')
    name='AmogOS-2.1-Pro-Debian-'+work.name.removeprefix('debian-')+'.iso'
    artifact=output/name
    partial=output/(name+'.partial')
    if artifact.exists() or partial.exists():
        raise RuntimeError('Refusing to overwrite an existing output.')
    run(['grub-mkrescue','--locales=','--themes=','--product-name=AmogOS','--product-version=2.1','-o',partial,'-V','AMOGOS_21',tree])
    report=capture(['xorriso','-indev',partial,'-report_el_torito','plain','-report_system_area','plain'])
    partial.rename(artifact)
    checksum=digest(artifact)
    artifact.with_suffix('.iso.sha256').write_text(checksum+'  '+artifact.name+'\n')
    manifest=dict(edition='amogos-debian',osVersion='2.1',iso=name,bytes=artifact.stat().st_size,sha256=checksum,kernel=version,amogosSourceCommit=lock['commit'],amogosPackages={item['package']:item['version'] for item in lock['packages']},root='0:0:0755',compression='zstd level 15, 256 KiB blocks')
    artifact.with_suffix('.manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    artifact.with_suffix('.packages.txt').write_bytes((root/'var/lib/dpkg/status').read_bytes())
    artifact.with_suffix('.boot-layout.txt').write_text(report+'\n')
    return manifest
