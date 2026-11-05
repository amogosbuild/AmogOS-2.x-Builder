# Boot the exact ISO as optical and USB media under BIOS and UEFI in disposable software-emulated VMs.
import argparse
import concurrent.futures
import json
import pathlib
import re
import shutil
import socket
import subprocess
import tempfile
import time
from qemu import Monitor,connect


def test(iso,folder,firmware,media,timeout):
    name=firmware+'-'+media
    folder=folder/name
    folder.mkdir()
    monitor_path=folder/'qmp.sock'
    serial_path=folder/'serial.sock'
    command=['qemu-system-x86_64','-machine','q35,accel=tcg','-cpu','max','-smp','2','-m','1536','-display','none','-vga','std','-monitor','none','-no-reboot','-nic','none','-qmp','unix:'+str(monitor_path)+',server=on,wait=off','-chardev','socket,id=serial0,path='+str(serial_path)+',server=on,wait=off','-serial','chardev:serial0']
    if firmware=='uefi':
        shutil.copyfile('/usr/share/OVMF/OVMF_VARS_4M.fd',folder/'vars.fd')
        command+=['-drive','if=pflash,format=raw,readonly=on,file=/usr/share/OVMF/OVMF_CODE_4M.fd','-drive','if=pflash,format=raw,file='+str(folder/'vars.fd')]
    if media=='cdrom':
        command+=['-drive','file='+str(iso)+',format=raw,media=cdrom,readonly=on','-boot','order=d,strict=on']
    else:
        command+=['-drive','if=none,id=usbiso,file='+str(iso)+',format=raw,readonly=on','-device','qemu-xhci,id=xhci','-device','usb-storage,bus=xhci.0,drive=usbiso,bootindex=1,removable=on']
    process=monitor=serial=None
    start=time.monotonic()
    result=dict(firmware=firmware,media=media,passed=False)
    try:
        with (folder/'qemu.log').open('wb') as errors,(folder/'serial.log').open('wb',buffering=0) as log:
            process=subprocess.Popen(command,stdin=subprocess.DEVNULL,stdout=errors,stderr=errors)
            monitor=Monitor(monitor_path,process)
            serial=connect(serial_path,process)
            serial.settimeout(1)
            data=b''
            selected=False
            while time.monotonic()-start<timeout:
                try:
                    block=serial.recv(65536)
                except socket.timeout:
                    block=b''
                if block:
                    data+=block
                    log.write(block)
                clean=re.sub(rb'\x1b\[[0-?]*[ -/]*[@-~]',b'',data).replace(b'\r',b'')
                if not selected and b'boot diagnostics' in clean:
                    serial.sendall(b'd')
                    selected=True
                if b'Kernel panic' in clean or b'Unable to find a medium containing a live file system' in clean:
                    raise RuntimeError('Kernel or live filesystem boot failed.')
                root_guard=re.search(rb'Finished amogos-root-ownership[^\n]*',clean)
                tmpfiles=re.search(rb'Finished systemd-tmpfiles-setup\.se[^\n]*',clean)
                display=re.search(rb'Started [^\n]*Display Manager|Reached target [^\n]*Graphical Interface',clean)
                failed=re.search(rb'Failed to start (?:amogos-root-ownership|systemd-tmpfiles-setup\.se)',clean)
                if display and root_guard and tmpfiles and root_guard.start()<tmpfiles.start() and not failed:
                    result.update(passed=True,rootGuardBeforeTmpfiles=True,milestone=display.group().decode(errors='replace'))
                    break
                if process.poll() is not None:
                    raise RuntimeError('QEMU exited during boot.')
            if not result['passed']:
                result['error']='Timed out before the display manager and root guard completed.'
            monitor.command('quit')
            process.wait(timeout=15)
    except Exception as error:
        result['error']=str(error)
    finally:
        if serial:
            serial.close()
        if monitor:
            monitor.close()
        if process and process.poll() is None:
            process.terminate()
            process.wait(timeout=15)
    result['seconds']=round(time.monotonic()-start,1)
    print(json.dumps(result),flush=True)
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('iso',type=pathlib.Path)
    parser.add_argument('--work-dir',type=pathlib.Path,default=pathlib.Path('.work'))
    parser.add_argument('--timeout',type=int,default=600)
    args=parser.parse_args()
    args.work_dir.mkdir(parents=True,exist_ok=True)
    folder=pathlib.Path(tempfile.mkdtemp(prefix='boot-',dir=args.work_dir)).resolve()
    iso=args.iso.resolve(strict=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        results=list(pool.map(lambda pair:test(iso,folder,*pair,args.timeout),[('bios','cdrom'),('uefi','cdrom'),('bios','usb'),('uefi','usb')]))
    iso.with_suffix('.boot.json').write_text(json.dumps(results,indent=2)+'\n')
    raise SystemExit(0 if all(item['passed'] for item in results) else 1)


if __name__=='__main__':
    main()
