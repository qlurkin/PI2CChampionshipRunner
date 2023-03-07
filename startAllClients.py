# Start and Monitor clients described in a YAML File
#
# clients:
# - students:
#   - name:
#     matricule:
#   cwd:
#   cmd: with {port} and {name} where the port number and name should go
#   port:
#   name:


import subprocess as sp
import os
from threading import Thread
import time
import yaml
import sys
import re

p = re.compile(r'\s+')


def monitor(client):
    if 'cmd' not in client:
        print('No command for', ', '.join([
            elem['name']
            for elem in client['students']
        ]))
        return lambda: None
    name = client['name']
    proc = None
    thread = None
    port = client['port']
    cmd = client['cmd'].format(port=port, name=name)
    running = True
    restarted = 0
    state = ''
    cwd = client['cwd']
    log = open(os.path.join(cwd, '../log.txt'), 'w')

    def setState(s):
        nonlocal state
        state = s
        print(f'{name}: {state}')

    def start():
        nonlocal proc
        proc = sp.Popen(p.split(cmd), stdout=log, stderr=sp.STDOUT, cwd=cwd)
        time.sleep(0.5)
        setState('started')

    def ok():
        assert proc is not None
        return proc.poll() is None

    def stop():
        nonlocal running
        running = False
        assert thread is not None
        thread.join()
        setState("monitor stopped")

    def loop():
        nonlocal restarted
        setState('starting')
        start()
        assert proc is not None
        while running:
            if not ok():
                proc.terminate()
                setState('restarting')
                start()
                restarted += 1
            time.sleep(2)

        proc.terminate()
        try:
            proc.wait(10)
        except TimeoutError:
            proc.kill()
        setState("process stopped")
        log.write(f'Restarted {restarted} times')
        log.close()

    thread = Thread(target=loop)
    print('Starting monitoring for {}...'.format(name))
    thread.start()
    return stop


def start(filename):
    with open(filename, encoding='utf8') as file:
        clients = yaml.load(file.read(), Loader=yaml.SafeLoader)['clients']

    print('type \'stop\' to stop')

    stops = []
    try:
        for client in clients:
            time.sleep(0.2)
            stops.append(monitor(client))
        command = ''
        while command != 'stop':
            command = input()
    except Exception as e:
        print(type(e), e)
    finally:
        print('stopping...')
        for stop in stops:
            stop()
        print('All processes stopped')


if __name__ == '__main__':
    time.sleep(2)
    start(sys.argv[1])
