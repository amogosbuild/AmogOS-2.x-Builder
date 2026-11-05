# Socket helpers manage only the QEMU process created for one read-only boot test.
import json
import socket
import time


def connect(path,process):
    deadline=time.monotonic()+30
    while time.monotonic()<deadline:
        connection=socket.socket(socket.AF_UNIX)
        try:
            connection.connect(str(path))
            return connection
        except (FileNotFoundError,ConnectionRefusedError):
            connection.close()
            if process.poll() is not None:
                raise RuntimeError('QEMU stopped before its socket became ready.')
            time.sleep(.1)
    raise TimeoutError('QEMU socket was not created.')


class Monitor:
    def __init__(self,path,process):
        self.socket=connect(path,process)
        self.socket.settimeout(15)
        self.stream=self.socket.makefile('rb')
        self.stream.readline()
        self.command('qmp_capabilities')

    def command(self,name):
        self.socket.sendall(json.dumps(dict(execute=name)).encode()+b'\n')
        while line:=self.stream.readline():
            response=json.loads(line)
            if 'return' in response:
                return response['return']
            if 'error' in response:
                raise RuntimeError(str(response['error']))
        raise RuntimeError('QEMU monitor closed unexpectedly.')

    def close(self):
        self.stream.close()
        self.socket.close()
