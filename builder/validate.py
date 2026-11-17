# Check repository inputs, portable paths and the single-comment convention without requiring root.
import ast
import io
import json
import pathlib
import re
import tokenize


def check(repository):
    total=0
    suffixes={'.py','.sh','.conf','.cfg','.list','.desktop','.service','.ps1','.yml','.yaml','.jsonc','.js','.rules','.desc'}
    for path in repository.rglob('*'):
        relative=path.relative_to(repository)
        if not path.is_file() or any(part in ('.git','.work','out','__pycache__') for part in relative.parts):
            continue
        if path.suffix not in suffixes and path.name not in ('Containerfile','.gitignore','.gitattributes','defaults','amogos-calamares-fallback','amogos-live-shortcuts','amogos-broadcom'):
            continue
        source=path.read_text(encoding='utf-8')
        if path.suffix=='.py':
            ast.parse(source,filename=str(relative))
            count=sum(item.type==tokenize.COMMENT for item in tokenize.generate_tokens(io.StringIO(source).readline))
        elif path.suffix in ('.js','.jsonc') or 'polkit-1' in path.parts:
            count=len(re.findall(r'(?m)^\s*//',source))
        else:
            count=len(re.findall(r'(?m)^\s*#',source))
        if count!=1:
            raise RuntimeError(str(relative)+': expected one comment, found '+str(count))
        if re.search(r'/(?:srv)/[A-Za-z0-9_.-]+',source) or re.search(r'(?i)\b[A-Z]:[/\\]Users[/\\][A-Za-z0-9_.-]+',source):
            raise RuntimeError('Private deployment path in '+str(relative))
        total+=1
    lock=json.loads((repository/'amogos-debian/sources.lock.json').read_text())
    if not re.fullmatch('[0-9a-f]{40}',lock['commit']) or len(lock['packages'])!=7:
        raise RuntimeError('Invalid application source lock.')
    for package in lock['packages']:
        if not re.fullmatch('[0-9a-f]{64}',package['sha256']) or not package['filename'].startswith('pool/') or '..' in pathlib.PurePosixPath(package['filename']).parts:
            raise RuntimeError('Invalid locked package path or checksum.')
    if {package['package'] for package in lock['packages']}!={'amogos-installer','amogos-store','amogos-music','amogos-notes','amogos-system','amogos-update','amogos-archive-keyring'}:
        raise RuntimeError('The locked archive is missing required AmogOS packages.')
    for name in ('etc/xdg/kdeglobals','usr/share/pixmaps/amogos-menu.png','usr/share/plasma/look-and-feel/org.amogos.desktop/metadata.json'):
        if not (repository/'shared/overlay'/name).is_file():
            raise RuntimeError('Missing shared overlay input: '+name)
    for number in range(9):
        if not (repository/'shared/overlay/usr/share/wallpapers/AmogOSEngine'/('img'+str(number)+'.png')).is_file():
            raise RuntimeError('A numbered wallpaper is missing.')
    arch=repository/'amogos-arch/amogosiso'
    arch_packages={line.strip() for line in (arch/'packages.x86_64').read_text().splitlines()
                   if line.strip() and not line.startswith('#')}
    required={'linux-zen','linux-zen-headers','amogos-arch-store','amogos-arch-installer',
              'amogos-arch-onboarding','amogos-arch-system','amogos-music','amogos-notes',
              'nvidia-open-dkms','steam'}
    forbidden={'linux','amogos-store','amogos-installer'}
    if required-arch_packages or arch_packages&forbidden:
        raise RuntimeError('Unexpected packages in the Arch image.')
    for config in ('pacman.conf','airootfs/etc/pacman.conf'):
        text=(arch/config).read_text()
        if '[amogos-arch]' not in text or '[chaotic-aur]' not in text or 'SigLevel = Never' in text:
            raise RuntimeError('Arch package signing or repository configuration is invalid.')
    for name in ('grub/grub.cfg','grub/loopback.cfg','syslinux/syslinux-linux.cfg'):
        text=(arch/name).read_text()
        if 'AmogOS 2 Pro (Arch)' not in text or 'vmlinuz-linux-zen' not in text or 'initramfs-linux-zen.img' not in text:
            raise RuntimeError('The Arch boot menu must use the Zen kernel and Arch branding.')
    print(json.dumps(dict(passed=True,maintainedFiles=total,editions=['amogos-debian','amogos-arch'],sourceRevision=lock['commit']),indent=2))
