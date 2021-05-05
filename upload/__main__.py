from os import remove, popen
from .__init__ import transfer
from .sqlMerge import upload_sp
from datetime import datetime

import socket

hostname = socket.gethostname()

timestamp=datetime.utcnow().strftime("%Y%m%d %H:%M:%S")

# if we are root, write to root dir
user = popen('echo $USER').read().strip()

if user == 'root': __RDIR__ = '/root'
else: __RDIR__ = '/home/'+user

filename = '/testfile'+hostname+'.txt'

with open (__RDIR__+filename,'w') as f:
    f.write ('File transfered from '+hostname+' at '+timestamp )

if 'BBServer' in hostname:

    if upload_sp(__RDIR__+'/testfile.txt'):
        print ('Upload-to-Sharepoint test passed!')
    else:
        print ('Upload-to-Sharepoint test failed!')
        print ('Check serverpi is connected to internet!')

else:

    source = __RDIR__+'/testfile.txt'
    destination = "/home/serverpi/datastaging"

    if transfer(source, destination, __RDIR__):
        print ('Upload-to-server test passed!')
    else:
        print ('Upload-to-server test failed!')
        print ('Check sensor in range of serverpi')

remove(__RDIR__+filename)
