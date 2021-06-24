import json
import socket
import sys
if __name__ == '__main__':
    host = 'localhost'
    port = 9090
    argv = sys.argv
    if len(argv) == 4:
        task = argv[1]
        task_type = argv[2]
        details = argv[3]
    elif len(argv) == 3:
        task = argv[1]
        task_type = '0'
        details = argv[2]
    with socket.create_connection((host, port)) as s:
        data = {'type': task_type, 'data': details, 'task': task}
        s.send(json.dumps(data).encode())
        result = s.recv(8192)
        ready = b''
        while result:
            ready += result
            result = s.recv(8192)
        print(ready.decode())
