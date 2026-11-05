# Shared command, file and mount helpers keep build mutations inside a new workspace.
import contextlib
import os
import pathlib
import shutil
import subprocess


ENV=dict(os.environ,LC_ALL='C',DEBIAN_FRONTEND='noninteractive',MAKEFLAGS='-j1',OMP_NUM_THREADS='1')


def run(arguments,**kwargs):
    print('+ '+' '.join(map(str,arguments)),flush=True)
    return subprocess.run(list(map(str,arguments)),check=True,env=ENV,**kwargs)


def capture(arguments):
    return run(arguments,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT).stdout.strip()


def write(root,name,value,mode=0o644):
    path=root/name.lstrip('/')
    if '..' in pathlib.PurePosixPath(name).parts or not path.parent.resolve().is_relative_to(root.resolve()):
        raise RuntimeError('Build path escapes its target: '+name)
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.is_symlink():
        raise RuntimeError('Refusing to replace a symbolic link: '+name)
    path.write_text(value,encoding='utf-8',newline='\n')
    path.chmod(mode)
    return path


def copy_tree(source,target):
    for path in source.rglob('*'):
        destination=target/path.relative_to(source)
        if path.is_symlink() or destination.is_symlink() or not destination.parent.resolve().is_relative_to(target.resolve()):
            raise RuntimeError('Unsafe overlay path: '+str(path.relative_to(source)))
    shutil.copytree(source,target,dirs_exist_ok=True)
    target.chmod(0o755)
    for path in source.rglob('*'):
        if path.is_symlink():
            continue
        (target/path.relative_to(source)).chmod(0o755 if path.is_dir() else 0o644)


def chroot(root,arguments,**kwargs):
    return run(['chroot',root,*arguments],**kwargs)


@contextlib.contextmanager
def mounted(root):
    mounts=[]
    try:
        for folder in ('dev','proc','sys','run','tmp'):
            (root/folder).mkdir(exist_ok=True)
        for folder,command in [('dev',['mount','--rbind','/dev']),('proc',['mount','-t','proc','proc']),('sys',['mount','-t','sysfs','-o','ro','sysfs']),('run',['mount','-t','tmpfs','-o','mode=755','tmpfs']),('tmp',['mount','-t','tmpfs','-o','mode=1777','tmpfs'])]:
            run([*command,root/folder])
            mounts.append(root/folder)
            if folder=='dev':
                run(['mount','--make-rslave',root/folder])
        resolver=root/'etc/resolv.conf'
        resolver.unlink(missing_ok=True)
        resolver.write_bytes(pathlib.Path('/etc/resolv.conf').read_bytes())
        yield
    finally:
        for path in reversed(mounts):
            run(['umount','-R',path])


def require_tools(names):
    missing=[name for name in names if not shutil.which(name)]
    if missing:
        raise RuntimeError('Missing build tools: '+', '.join(missing)+'. Use --install-dependencies or --container.')
