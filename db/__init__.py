import sqlite3,os,socket

hostname = socket.gethostname()

if "BBServer" in hostname:
    filename = '/server.db'
else:
    filename = '/sensor.db'

# if we are root, write to root dir
user = os.popen('echo $USER').read().strip()


if user == 'root': __RDIR__ = '/root'
else: __RDIR__ = '/home/'+user

conn = sqlite3.connect(__RDIR__+filename)