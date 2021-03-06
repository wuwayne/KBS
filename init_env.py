import os
import sys


def init_env(appname,migrate=True):
	if os.name == 'nt':
		os.system('set FLASK_APP={}'.format(appname))
		os.system('set FLASK_DEBUG=1')

	if os.name == 'posix':
		os.system('export FLASK_APP={}'.format(appname))
		os.system('export FLASK_DEBUG=1')
		
	if migrate:
		os.system('flask db migrate')		
		os.system('flask db upgrade')

	
	os.system('flask run')

if __name__ == '__main__':
	if len(sys.argv) == 2:
		init_env(sys.argv[1])
	else:
		init_env(sys.argv[1],sys.argv[2])
	# print(sys.argv)
	