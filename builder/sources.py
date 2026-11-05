# Fetch the pinned public application archive and verify signatures and every locked package digest.
import hashlib
import json
import pathlib
from common import run


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()


def fetch(repository,work):
    lock=json.loads((repository/'amogos-debian/sources.lock.json').read_text())
    source=work/'sources'
    run(['git','init',source])
    run(['git','-C',source,'remote','add','origin',lock['repository']])
    run(['git','-C',source,'fetch','--depth','1','origin',lock['commit']])
    run(['git','-C',source,'checkout','--detach','FETCH_HEAD'])
    actual=run(['git','-C',source,'rev-parse','HEAD'],text=True,stdout=-1).stdout.strip()
    if actual!=lock['commit']:
        raise RuntimeError('Application source revision does not match the lock.')
    archive=source/'amogos-debian'
    keyring=archive/'keyrings/amogos-archive-keyring.gpg'
    if digest(keyring)!=lock['keyringSha256']:
        raise RuntimeError('Archive keyring differs from the pinned public key.')
    run(['python3',archive/'scripts/validate-repository.py'])
    for package in lock['packages']:
        path=archive/package['filename']
        if path.stat().st_size!=package['bytes'] or digest(path)!=package['sha256']:
            raise RuntimeError('Locked package verification failed: '+package['package'])
    return archive,lock
