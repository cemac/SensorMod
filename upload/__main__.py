import sqlite3
import os
from .__init__ import transfer
from .sqlMerge import upload_sp
from datetime import datetime

import socket

hostname = socket.gethostname()

timestamp=datetime.utcnow().strftime("%Y%m%d %H:%M:%S")

# if we are root, write to root dir
user = os.popen('echo $USER').read().strip()

if user == 'root': __RDIR__ = '/root'
else: __RDIR__ = '/home/'+user

filename = '/testfile'+hostname+'.txt'

with open (__RDIR__+filename,'w') as f:
    f.write ('File transfered from '+hostname+' at '+timestamp )

if 'BBServer' in hostname:

    if upload_sp(__RDIR__+'/testfile.txt'):
        print ('Upload-to-Sharepoint test passed!')

else:

    source = __RDIR__+'/testfile.txt'
    destination = "/home/serverpi/datastaging"

    if transfer(source, destination, __RDIR__):
        print ('Upload-to-server test passed!')
