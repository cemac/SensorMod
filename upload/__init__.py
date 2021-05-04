'''
scripts to run if connected online
'''
import os
from datetime import date,datetime
from ..log_manager import getlog
log = getlog(__file__)
print = log.print

def online():

    cmd = '''
    PINGS=2
    TESTIP=8.8.8.8
    if ( ping -c $PINGS $TESTIP > /dev/null ) then
        echo "1"
    else
        echo "0"
    fi
    '''

    return int(os.popen(cmd).read())

def connected():
    cmd = '''
    PINGS=2
    TESTIP=10.3.141.1
    if ( ping -c $PINGS $TESTIP > /dev/null ) then
        echo "1"
    else
        echo "0"
    fi
    '''
    return int(os.popen(cmd).read())



def readpassphrase(__RDIR__):

    with open (os.path.join(__RDIR__,'.serverpi')) as f:
        lines = f.readlines()
        for line in lines:
            if 'serverpi_access_key = ' in line:
                private_key_pass = line[22:-1]

    return private_key_pass

def buildtables(conn):

    conn.execute('''
                 CREATE TABLE MEASUREMENTS
                 (
                     SERIAL       CHAR(16)    NOT NULL,
                     TYPE         INT         NOT NULL,
                     TIME         CHAR(6)     NOT NULL,
                     LOC          BLOB        NOT NULL,
                     PM1          REAL        NOT NULL,
                     PM3          REAL        NOT NULL,
                     PM10         REAL        NOT NULL,
                     T            REAL        NOT NULL,
                     RH           REAL        NOT NULL,
                     BINS         BLOB        NOT NULL,
                     SP           REAL        NOT NULL,
                     RC           INT         NOT NULL,
                     UNIXTIME     INT         NOT NULL
                     );
                 ''')

    conn.execute('''
                 CREATE TABLE PUSH
                 (
                    SERIAL       CHAR(16)    NOT NULL,
                    TIME         CHAR(6)     NOT NULL,
                    DATE         CHAR(8)     NOT NULL
                    );
                ''')

    conn.commit()

    return

def copydb(file_name,SERIAL):

    import sqlite3

    DATE = date.today().strftime("%d%m%Y")
    TIME = datetime.utcnow().strftime("%H%M%S")
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")

    hostname = os.popen('hostname').read().strip()

    newfilename = 'sensor_'+hostname+'_'+timestamp+'.db'
    newfiledir = '/home/sensorpi/upload_data'

    if not os.path.exists(newfiledir):
        os.makedirs(newfiledir)

    newfile = os.path.join(newfiledir,newfilename)

    if os.path.exists(newfile):
        os.remove(newfile)

    try:
        conn_dest = sqlite3.connect(newfile)
    except:
        print("Unable to create new file")

    try:
        buildtables(conn_dest)
    except:
        print("Unable to write to new db")

    cursor_dst = conn_dest.cursor()

    cursor_dst.execute("SELECT name FROM sqlite_master WHERE type='table';")

    table_list=[]
    for table_item in cursor_dst.fetchall():
        table_list.append(table_item[0])

    cmd = "attach ? as toMerge"
    cursor_dst.execute(cmd, (file_name, ))

    for table_name in table_list:

        try:
            cmd = "INSERT INTO {0} SELECT * FROM toMerge.{0};".format(table_name)
            cursor_dst.execute(cmd)
            conn_dest.commit()

        except sqlite3.OperationalError:
            print("ERROR!: Merge Failed for " + table_name)

        finally:
            if table_name == table_list[-1]:
                cmd = "detach toMerge"
                cursor_dst.execute(cmd, ())

    data = [(SERIAL,TIME,DATE,)]

    conn_dest.executemany("INSERT INTO PUSH (SERIAL,TIME,DATE) VALUES(?, ?, ?);", data )

    conn_dest.commit()

    conn_dest.close()

    return newfile


def sync(SERIAL,conn):

    from time import sleep
    from random import randint

    sleep(randint(10,300))  # Wait a random amount of time between 10 secs and 10 mins to limit overloading serverpi

    # if we are root, write to root dir
    user = os.popen('echo $USER').read().strip()

    if user == 'root': __RDIR__ = '/root'
    else: __RDIR__ = '/home/'+user

    db_file_path = os.path.join(__RDIR__,'sensor.db')

    if not os.path.exists(db_file_path):
        print ("Could not find the db file to upload")
        return False

    try:
        upload_file = copydb(db_file_path,SERIAL)
    except:
        print ("Failed to make a local copy of db file")

    destination = "/home/serverpi/datastaging"
    source = upload_file

    success=transfer(source, destination,__RDIR__)

    return success
    

def transfer (source, destination, __RDIR__):

    import pysftp

    private_key = os.path.join(__RDIR__,".ssh/id_rsa")  # can use password keyword in Connection instead

    key_pass = readpassphrase(__RDIR__)

    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None

    for i in range (10):
        try:
            with pysftp.Connection(host="10.3.141.1", username="serverpi", private_key=private_key, private_key_pass=key_pass, cnopts=cnopts) as srv:
                print ("Connection Open")
                #srv.timeout(10.0)
                if srv.exists(destination):
                    srv.chdir(destination)
                    print("Uploading db file to serverpi")
                    channel = srv.sftp_client.get_channel()
                    channel.lock.acquire()
                    channel.out_window_size += os.stat(source).st_size
                    channel.out_buffer_cv.notifyAll()
                    channel.lock.release()
                    srv.put(source)
                    print ("File transfered - "+source)
                else:
                    print("Destination does not exist")
                    success = False
                    continue
                success = True
                break
        except Exception as e:
            if i < 9:
                print ('Upload failed - attempt {} of 10\nError - {}\nRetrying'.format(i+1,e))
                continue
            else:
                print ('Upload failed - attempt 10 of 10\nError - {}\nAborting'.format(e))
                print ('Could not upload db to serverpi')
                success=False

        if not success:
            if os.path.exists(source):
                os.remove(source)

    return success

def stage(SERIAL,__RDIR__):

    import sqlite3
    from datetime import datetime, date

    DATE = date.today().strftime("%d%m%Y")
    TIME = datetime.utcnow().strftime("%H%M%S")
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")

    hostname = os.popen('hostname').read().strip()

    newfilename = 'server_'+hostname+'_'+timestamp+'.db'
    newfiledir = '/home/serverpi/datastaging'

    file_name = os.path.join(__RDIR__,'server.db')

    if not os.path.exists(newfiledir):
        os.makedirs(newfiledir)

    newfile = os.path.join(newfiledir,newfilename)

    if os.path.exists(newfile):
        os.remove(newfile)

    try:
        conn_dest = sqlite3.connect(newfile)
    except:
        print("Unable to create new file")
        return False

    try:
        buildtables(conn_dest)
    except:
        print("Unable to write to new db")
        conn_dest.close()
        return False

    cursor_dst = conn_dest.cursor()

    cursor_dst.execute("SELECT name FROM sqlite_master WHERE type='table';")

    table_list=[]
    for table_item in cursor_dst.fetchall():
        table_list.append(table_item[0])

    cmd = "attach ? as toMerge"
    cursor_dst.execute(cmd, (os.path.join(__RDIR__,'server.db'), ))

    for table_name in table_list:

        try:
            cmd = "INSERT INTO {0} SELECT * FROM toMerge.{0};".format(table_name)
            cursor_dst.execute(cmd)
            conn_dest.commit()
            success = True
        except sqlite3.OperationalError:
            print("ERROR!: Merge Failed for " + table_name)
            success = False
        finally:
            if table_name == table_list[-1]:
                cmd = "detach toMerge"
                cursor_dst.execute(cmd, ())

    if not success:
        conn_dest.close()
        return success

    else:
        data = [(SERIAL,TIME,DATE,)]

        try:
            conn_dest.executemany("INSERT INTO PUSH (SERIAL,TIME,DATE) VALUES(?, ?, ?);", data )

            conn_dest.commit()

        except:
            print ("Error! Could not write staging data to PUSH table at {}".format(timestamp))
            success = False

        conn_dest.close()

    return success

def upload():

    from .sqlMerge import sqlMerge
    from glob import glob

    merge=sqlMerge()

    dataloc = '/home/serverpi/datastaging'

    sensorfiles = glob(os.path.join(dataloc,'sensor*.db'))

    serverfiles = glob(os.path.join(dataloc,'server*.db'))

    if len (serverfiles) > 1:
        for file in serverfiles[1:]:
            sensorfiles.append(file)
    elif len (serverfiles) < 1:
        print ("Could not find server.db file for merge")
        return False

    print (serverfiles[0])
    print (sensorfiles)

    #Merge the various DB and upload to AWS
    success = merge.mergelist(serverfiles[0], sensorfiles)

    if success:
        return True
    else:
        return False
