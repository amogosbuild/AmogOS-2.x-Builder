# Exercise real filesystem boundaries without mounting or changing any physical disks.
import pathlib
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'builder'))
from common import copy_tree,write
from validate import check
from debian_configure import finalize


class BoundaryTests(unittest.TestCase):
    def test_file_and_parent_symlinks_cannot_escape_target(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder=pathlib.Path(temporary)
            root=folder/'root'
            root.mkdir()
            outside=folder/'outside'
            outside.mkdir()
            (outside/'secret').write_text('unchanged')
            (root/'linked').symlink_to(outside,target_is_directory=True)
            with self.assertRaises(RuntimeError):
                write(root,'linked/secret','wrong')
            with self.assertRaises(RuntimeError):
                write(root,'../outside/secret','wrong')
            self.assertEqual((outside/'secret').read_text(),'unchanged')

    def test_overlay_does_not_walk_unrelated_target_directories(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder=pathlib.Path(temporary)
            source=folder/'source'
            target=folder/'target'
            outside=folder/'outside'
            (source/'etc').mkdir(parents=True)
            target.mkdir()
            outside.mkdir(mode=0o700)
            (target/'unrelated').symlink_to(outside,target_is_directory=True)
            (source/'etc/config').write_text('fixture')
            (source/'etc/config').chmod(0o777)
            copy_tree(source,target)
            self.assertEqual((target/'etc/config').read_text(),'fixture')
            self.assertEqual((target/'etc/config').stat().st_mode&0o777,0o644)
            self.assertEqual(outside.stat().st_mode&0o777,0o700)

    def test_escaping_overlay_destination_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder=pathlib.Path(temporary)
            for name in ('source/etc','target','outside'):
                (folder/name).mkdir(parents=True)
            (folder/'source/etc/config').write_text('fixture')
            (folder/'target/etc').symlink_to(folder/'outside',target_is_directory=True)
            with self.assertRaises(RuntimeError):
                copy_tree(folder/'source',folder/'target')
            self.assertFalse((folder/'outside/config').exists())

    def test_complete_repository_policy(self):
        check(pathlib.Path(__file__).resolve().parents[1])

    def test_finalization_discards_build_time_machine_identifiers(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=pathlib.Path(temporary)
            for name in ('etc','var/lib/dbus','var/lib/systemd'):
                (root/name).mkdir(parents=True,exist_ok=True)
            (root/'etc/machine-id').write_text('build-id')
            (root/'var/lib/dbus/machine-id').write_text('build-id')
            (root/'var/lib/systemd/random-seed').write_bytes(b'build-seed')
            with patch('debian_configure.chroot'):
                finalize(root)
            self.assertEqual((root/'etc/machine-id').read_text(),'')
            self.assertTrue((root/'var/lib/dbus/machine-id').is_symlink())
            self.assertEqual(str((root/'var/lib/dbus/machine-id').readlink()),'/etc/machine-id')
            self.assertFalse((root/'var/lib/systemd/random-seed').exists())


if __name__=='__main__':
    unittest.main()
