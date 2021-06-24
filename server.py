from time import sleep
import socket
import json
import threading


def server_reverse(s):
    sleep(2)
    return s[::-1]


def server_replace(s):
    sleep(5)
    res = ''
    for i in range(len(s) // 2):
        res += s[i * 2 + 1]
        res += s[i * 2]
    if len(s) % 2 == 1:
        res += s[-1]
    return res


def resolving(lock_queue, lock_results):
    while True:
        if server_queue:
            with lock_queue:
                task = server_queue.pop(0)
            if task['type'] == '1':
                func_res = server_reverse(task['data'])
            if task['type'] == '2':
                func_res = server_replace(task['data'])
            thread_res = {'type': task['type'],
                          'id': task['id'],
                          'data': func_res}
            with lock_results:
                results.append(thread_res)


def client_wait(connectionn, id):
    f = True
    while f:
        for i in results:
            if i['id'] == str(id):
                connectionn.send(
                    str(
                        'id ' + str(id) + ' Рузультат:' + i['data']
                    ).encode())
                f = False
                break
    connectionn.close()


def worker(connectionn, lock_queue):
    data = connectionn.recv(8192)
    data = json.loads(data)
    if data['task'] == '0':
        data['id'] = str(id[0])
        id[0] += 1
        with lock_queue:
            server_queue.append(data)
        connectionn.send(str(id[0] - 1).encode())
    if data['task'] == '1':
        check = True
        if check:
            for i in server_queue:
                if i['id'] == data['data']:
                    check = False
                    connectionn.send('в очереди'.encode())
        if check:
            for i in results:
                if i['id'] == data['data']:
                    check = False
                    connectionn.send('выполнено'.encode())
        if check:
            connectionn.send('выполняется'.encode())
    if data['task'] == '2':
        for i in results:
            if i['id'] == data['data']:
                connectionn.send(i['data'].encode())
    if data['task'] == '3':
        data['id'] = str(id[0])
        id[0] += 1
        with lock_queue:
            server_queue.append(data)
        threading.Thread(target=client_wait,
                         args=(connectionn, id[0] - 1),
                         daemon=True).start()
    if data['task'] != '3':
        connectionn.close()


if __name__ == '__main__':
    server_queue = list()
    results = list()
    lock_queue = threading.Lock()
    lock_results = threading.Lock()
    threading.Thread(target=resolving,
                     args=(lock_queue, lock_results),
                     daemon=True).start()
    id = [0]
    with socket.socket() as sock:
        sock.bind(('localhost', 9090))
        sock.listen()
        while True:
            connection, addr = sock.accept()
            threading.Thread(target=worker,
                             args=(connection, lock_queue),
                             daemon=True).start()
