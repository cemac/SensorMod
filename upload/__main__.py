import sqlite3
import os
from .__init__ import sync

filename = '/sensor.db'

# if we are root, write to root dir
user = os.popen('echo $USER').read().strip()


if user == 'root': __RDIR__ = '/root'
else: __RDIR__ = '/home/'+user

conn = sqlite3.connect(__RDIR__+filename)

SERIAL = os.popen('cat /sys/firmware/devicetree/base/serial-number').read() #16 char key

if sync(SERIAL, conn):
    print ('Upload test passed!')
