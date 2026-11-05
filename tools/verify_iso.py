# Verify a produced ISO using its manifest, boot catalog and embedded system configuration.
import argparse
import email.parser
import hashlib
import json
import pathlib
import re
import subprocess
import tempfile


def command(args):
    return subprocess.check_output(list(map(str,args)),stderr=subprocess.STDOUT)


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('iso',type=pathlib.Path)
    parser.add_argument('--work-dir',type=pathlib.Path,default=pathlib.Path('.work'))
    args=parser.parse_args()
    iso=args.iso.resolve(strict=True)
    manifest=json.loads(iso.with_suffix('.manifest.json').read_text())
    assert digest(iso)==manifest['sha256'] and iso.stat().st_size==manifest['bytes']
    catalog=command(['xorriso','-indev',iso,'-report_el_torito','plain','-report_system_area','plain']).decode()
    assert 'BIOS' in catalog and 'UEFI' in catalog
    args.work_dir.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='verify-',dir=args.work_dir) as temporary:
        folder=pathlib.Path(temporary)
        image=folder/'filesystem.squashfs'
        command(['xorriso','-osirrox','on','-indev',iso,'-extract','/live/filesystem.squashfs',image])
        listing=command(['unsquashfs','-lln','-max-depth','0',image]).decode()
        assert re.search(r'(?m)^drwxr-xr-x\s+0/0\s',listing)
        def read(name):
            return command(['unsquashfs','-cat',image,name])
        identity=read('usr/lib/os-release').decode()
        assert 'ID=amogos' in identity and 'OS_VERSION="2.1"' in identity
        assert b'Before=systemd-tmpfiles-setup.service sysinit.target' in read('usr/lib/systemd/system/amogos-root-ownership.service')
        assert b'AmogOS 2.1 Pro (Debian edition) developed by CursedMC64 and techtimefor.' in read('usr/bin/amogos-credits')
        assert b'URIs: https://amogosbuild.github.io/amogos-debian' in read('etc/apt/sources.list.d/amogos.sources')
        assert b'amogos.music.desktop' in read('usr/share/plasma/plasmoids/org.kde.plasma.taskmanager/contents/config/main.xml')
        assert b'LookAndFeelPackage=org.amogos.desktop' in read('etc/skel/.config/kdeglobals')
        status={}
        for paragraph in read('var/lib/dpkg/status').decode().split('\n\n'):
            fields=dict(email.parser.Parser().parsestr(paragraph).items())
            if fields.get('Status')=='install ok installed':
                status[fields['Package']]=fields['Version']
        assert all(status.get(name)==version for name,version in manifest['amogosPackages'].items())
        drivers=json.loads(read('usr/share/amogos/offline-drivers/manifest.json'))
        for package in drivers['packages']:
            process=subprocess.Popen(['unsquashfs','-cat',str(image),'usr/share/amogos/offline-drivers/archives/'+package['file']],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            checksum=hashlib.sha256()
            length=0
            while block:=process.stdout.read(1048576):
                checksum.update(block)
                length+=len(block)
            assert process.wait()==0 and length==package['bytes'] and checksum.hexdigest()==package['sha256']
        result=dict(passed=True,iso=iso.name,sha256=manifest['sha256'],root='0:0:0755',biosAndUefiCatalog=True,amogosPackages=manifest['amogosPackages'],offlineDriverArchives=len(drivers['packages']),persistentDefaults=True,credits=True)
    iso.with_suffix('.verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
