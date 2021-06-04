import subprocess as sp
import os
from threading import Thread
import time
import yaml
import sys

def monitor(group):
	if 'cmd' not in group:
		print('No command for', ', '.join([elem['name'] for elem in group['students']]))
		return lambda:None
	name = groupName(group)
	proc = None
	thread = None
	port = group['port']
	cmd = group['cmd'].format(port)
	running = True
	restarted = 0
	state = ''
	cwd = os.path.join('.', 'groups', str(port))
	log = open(os.path.join(cwd, 'log.txt'), 'w')

	def setState(s):
		nonlocal state
		state = s
		print(f'{name}: {state}')

	def start():
		nonlocal proc
		proc = sp.Popen(cmd, stdout=log, stderr=sp.STDOUT, cwd=cwd)
		time.sleep(0.5)
		setState('started')

	def ok():
		return proc.poll() is None
	
	def stop():
		nonlocal running
		running = False
		thread.join()
		setState("monitor stopped")
	
	def loop():
		nonlocal restarted
		setState('starting')
		start()
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
	print('Starting monitoring for {}...'.format(groupName(group)))
	thread.start()
	return stop


def groupName(group):
	return '{} ({})'.format(group['port'], ', '.join([student['matricule'] for student in group['students']]))

def start(filename):
	with open(filename, encoding='utf8') as file:
		groups = yaml.load(file.read(), Loader=yaml.SafeLoader)['groups']

	print('type \'stop\' to stop')

	try:
		stops = []
		for group in groups:
			stops.append(monitor(group))
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
	start(sys.argv[1])