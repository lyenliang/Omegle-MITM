'''
Created on 2014/10/5

@author: Unlimited
'''
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

'''
def commonLikeSearchTimeout(topic):
    # FIXME: logic duplication with "response = self.browser.open(url, urllib.urlencode(data), util.WAIT_TIMEOUT)"
    if topic == None: return False
    global accTime
    global PERIOD
    accTime += PERIOD
    return (accTime >= WAIT_TIMEOUT)
'''

def waitForClient(client, topic):
    while client.state == 'WAITING' or client.state == 'INIT':
        # print client.state
        time.sleep(PERIOD) 
    if client.state == 'STOP' or client.state == 'RECAPTCHA_REQUIRED':
        sys.exit(0)
    
    '''
    global accTime
    accTime = 0
    while(not client.connected):
        time.sleep(PERIOD)
        if commonLikeSearchTimeout(topic):
            #logPrint('Failed to find anyone with interest ' + topic)
            return False
    return True
    '''
                
            