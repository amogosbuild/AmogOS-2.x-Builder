# Dispatch isolated Debian builds and keep the reserved Arch edition unavailable until implemented.
import argparse
import datetime
import json
import os
import pathlib
import secrets
import subprocess
import sys

REPOSITORY=pathlib.Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser(description='Build the AmogOS Debian live ISO from public packages and source configuration.')
    parser.add_argument('edition',choices=['amogos-debian','debian'],nargs='?',default='amogos-debian')
    parser.add_argument('--work-dir',type=pathlib.Path,default=REPOSITORY/'.work')
    parser.add_argument('--output-dir',type=pathlib.Path,default=REPOSITORY/'out')
    parser.add_argument('--install-dependencies',action='store_true')
    parser.add_argument('--container',action='store_true',help='Build in the Debian container using Docker or Podman.')
    parser.add_argument('--engine',choices=['docker','podman'],default='docker')
    parser.add_argument('--check',action='store_true',help='Validate source/configuration without building or requiring root.')
    arguments=parser.parse_args()
    if arguments.check:
        from validate import check
        check(REPOSITORY)
        return
    if sys.platform!='linux':
        parser.error('Build on x86_64 Linux, including a Linux VM or WSL2 with a suitable container engine.')
    if os.uname().machine!='x86_64':
        parser.error('The current Debian edition targets x86_64.')
    for location in (arguments.work_dir,arguments.output_dir):
        if location.resolve()==pathlib.Path('/'):
            parser.error('Choose dedicated work and output directories.')
        location.mkdir(parents=True,exist_ok=True)
    if arguments.container:
        from containers import build
        build(REPOSITORY,arguments)
        return
    if os.geteuid()!=0:
        parser.error('Native builds require root; use sudo or --container.')
    if os.environ.get('AMOGOS_PRIVATE_MOUNT_NAMESPACE')!='1':
        os.execvp('unshare',['unshare','--mount','--fork','--propagation','private','env','AMOGOS_PRIVATE_MOUNT_NAMESPACE=1',sys.executable,str(pathlib.Path(__file__).resolve()),*sys.argv[1:]])
    from debian import build
    stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    work=arguments.work_dir.resolve()/('debian-'+stamp+'-'+secrets.token_hex(3))
    work.mkdir(mode=0o755)
    result=build(REPOSITORY,work,arguments.output_dir.resolve(),arguments.install_dependencies)
    print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':
    try:
        main()
    except (RuntimeError,subprocess.CalledProcessError) as error:
        raise SystemExit(str(error))
