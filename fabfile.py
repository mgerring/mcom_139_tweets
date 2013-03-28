from fabric.api import *
from datetime import datetime

env.hosts = ['root@ummer.matthewgerring.com']

def deploy(m="lazy ass developer didn't write a commit message at %s" % datetime.now().strftime('%x %X') ):
	local('git add -A')
	local('git commit -m "%s"' % m)
	local('git push go master')
	with cd('/sites/debater'):
		run('git pull origin master')

def setup():
	with cd('/sites/debater'):
		run('git clone /sites/git/debater.git ./')