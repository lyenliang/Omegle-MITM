import logging
import math
import random
import sys
import time

RANDID_SELECTION = '23456789ABCDEFGHJKLMNPQRSTUVWXYZ'
accTime = 0
PERIOD = 0.5
WAIT_TIMEOUT = 5
    
def logPrint(message, level='info'):
    if level == 'info':
        logging.info(message)
    elif level == 'debug':
        logging.debug(message)
    print(message)
    
def getLogFileName():
    return time.strftime("%Y-%m-%d_%H-%M-%S") + '.log'

def initLogs():
    logging.basicConfig(filename=getLogFileName(), level=logging.DEBUG, format='%(asctime)s %(message)s')
    
def nocache():
    return '%r' % random.random()
    
def randid():
    randid = ''
    for _ in range(0, 8):
        c = int(math.floor(32 * random.random()))
        randid += RANDID_SELECTION[c]
    return randid

def waitForClient(client, topic):
    while client.state == 'WAITING' or client.state == 'INIT':
        # print client.state
        time.sleep(PERIOD) 
    if client.state == 'STOP' or client.state == 'RECAPTCHA_REQUIRED':
        sys.exit(0)
            