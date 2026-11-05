# Run Debian bootstrap, authenticated installation, desktop staging and hybrid image assembly in order.
import os
from common import mounted
from debian_bootstrap import prepare
from debian_configure import configure,finalize
from debian_packages import install
from drivers import cache
from identity import configure as identity
from iso import build as image
from sources import fetch


def build(repository,work,output,install_dependencies):
    root=prepare(work,install_dependencies)
    archive,lock=fetch(repository,work)
    with mounted(root):
        identity(root)
        install(repository,root,archive,lock)
        configure(repository,root,archive)
        cache(root)
        finalize(root)
    resolver=root/'etc/resolv.conf'
    resolver.unlink(missing_ok=True)
    resolver.symlink_to('/run/NetworkManager/resolv.conf')
    os.chown(root,0,0)
    root.chmod(0o755)
    return image(repository,work,root,output,lock)
