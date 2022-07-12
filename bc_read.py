#!/usr/bin/env python3
import serial
from time import sleep
import logging
from tinydb import TinyDB, Query
from gpiozero import TonalBuzzer
from subprocess import call
BUZZER_PIN=26
p=TonalBuzzer(26)

#Watchdog device name - Node: WD disabled 
#WD=None
WD='/dev/watchdog'
#WD object
wdObj=None

def start_watchog(watchdog_device):
    dev=None
    if watchdog_device is not None:
        try:
            dev=open(watchdog_device,'w')
        except Exception as e:
            logging.info(e)
    logging.info("Watchdog {}".format('enabled' if dev is not None else 'disabled'))
    return(dev)

class bcr(object):
    def __init__(self,port='/dev/ttyACM0',timeout=1):
        self.bc=None
        self.running=False
        try:
            self.bc=serial.Serial(port=port,timeout=timeout)
            self.running=True
        except Exception as e:
            logging.error('{}'.format(e))
    def next(self):
        try:
            buffer=self.bc.readline()
            barcode=buffer.decode('UTF-8').strip() 
        except Exception as e:
            logging.error(e)
            self.running=False
        return(barcode if len(barcode)>0 else None)

def play(p,note,duration=.5):
    p.play(note)
    sleep(duration)
    p.stop()


def main():
    db=TinyDB('/opt/dmitri/data.json')
    q = Query()
    b=bcr()
    while not b.running:
        play(p,'A4')
        play(p,'A5')
        sleep(1)
        b=bcr()

    bc=0
    print("Database ",len(db))

    WD='/dev/watchdog'

    while b.running:
        #Pat watchdog if on
        if wdObj is not None:
            print('1',file = wdObj, flush = True)
        bc = b.next()
        if bc is not None:
            if bc[0] == '#':
                bc=bc[1:]
            try:
                search_res = db.search(q.sample == bc)
                if len(search_res)>0:
                    play(p,'C4',.1)
                    play(p,'A3',.1)
                    play(p,'C4',.1)
                    call(['aplay','/opt/dmitri/bleep_02.wav'])
                    logging.info('{}'.format(bc))
            except ValueError:
                pass

if __name__ == "__main__":
    logging.basicConfig(filename='/home/pi/dmitri.log',filemode='a',level=logging.INFO,format='%(message)s')
    #logging.basicConfig(level=logging.INFO,format='%(message)s')
    try:
        main()
    except KeyboardInterrupt:
        if wdObj is not None:
            print('V',file = wdObj, flush = True)
        print("\nExiting")
