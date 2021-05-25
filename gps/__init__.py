'''
A script to run a thread polling GPS sensors for the current location.

- If you are using a USB gps unit set `gpio = False`.



For a quick check we can look at `screen /dev/ttyS0 9600`
'''

import RPi.GPIO as GPIO
from threading import Thread,Lock,Event
lock = Lock()
import serial,time
from ..log_manager import getlog
log = getlog(__file__)

last = {'gpstime':None}
ser = None
gpio = False#True
log.info('GPIO GPS:%s'%gpio)
pin = 23#18 # BCM 12 / GPIO 18

stop_event = Event()

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

def pinon():
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin,GPIO.HIGH)
    time.sleep(1)
def pinoff():
    GPIO.setup(pin, GPIO.IN)
    time.sleep(1)

pinoff()
if gpio: pinon()



__all__ = 'last ser gpio connect bg_poll latlon'.split()

def connect():
    '''
    A function to ensure we are recieving information from the GPS unit
    '''
    global ser,gpio
    if gpio:
        ser = serial.Serial('/dev/ttyS0')#,9600)
        log.debug('GPIO GPS on /dev/ttyS0')
    else:
        for i in range(10):
            try:# each unplug registers as a new number, we dont expect more than 10 unplugs without a restart
                #try:ser = serial.Serial('/dev/ttyAMA%d'%i)
                #except:
                ser = serial.Serial('/dev/ttyACM%d'%i)

                log.debug( 'Connected serial on /dev/ttyACM%d'%i)
                break
            except:continue
    try:
        ser.flushInput()
        ser.flushOutput()
        return True
    except:
        return False


def bg_poll(ser,lock,stop_event):
        '''
        The background function which continuously polls the GPS unit within a separate thread.

        It is worth noting that eventhough we run this separately, the RPi Zero only has one core, so this ends up being multiplexed instead.
        A better solution for this may have been using async, however since the code can just as easily run on an RPI3, the multithreading seemed a more practical solution for code robustness
        '''


        global last,stopThread
        #ignored values to be named utc
        params = 'utc gpstime lat utc lon utc fix nsat HDOP alt utc WGS84 utc lastDGPS utc utc'.split()
        while not stop_event.is_set():
                try:
                    time.sleep(1)
                    line = str(ser.readline())

                except serial.SerialException:
                    log.debug('lost connection - reconnecting')
                    #last = {}
                    connect()
                    time.sleep(5)
                    continue

                if line.find('GGA') > 0:
                    lock.acquire()
                    last = dict(zip(params,line.split(',')))
                    lock.release()
                    #print(last)



def latlon():
    '''
    If there are no lat/lon results return 0
    '''
    global last
    if last['lat']=='' or last['lon']=='':
        return [0,0]
    else:
        return [float(last['lat']),float(last['lon'])]


def init(wait = False):
    '''
    A function to start the GPS threads
    '''

    if not connect():
        return False
    log.info('############# GPS daemon ############')
    stop_event.clear()

    daemon = Thread(target=bg_poll, args=(ser,lock,stop_event), name='location_daemon')
    daemon.setDaemon(True)#bg
    daemon.start()

    if wait:
        while last == {'gpstime':None}:
            log.info('waiting for gps result')
            time.sleep(4)

        while last['gpstime'] == '':
            log.debug(last)
            log.debug('GPS Connected, but not reading a result - please check volatge')
            time.sleep(4)

        while len(last['gpstime']) !=6 :
            log.debug(last)
            log.debug('GPS Connected, but not correct')
            time.sleep(1)



    log.info('GPS connected')
    log.debug(last)
    return daemon
