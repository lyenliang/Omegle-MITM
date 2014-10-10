'''
Created on 2014/10/5

@author: Unlimited
'''
from httplib import BadStatusLine
import json
import random
import re
import threading
import time
import traceback
import urllib
from urllib2 import URLError

import mechanize
import util

SERVER_LIST = ['front1.omegle.com', 'front2.omegle.com', 'front3.omegle.com',
               'front4.omegle.com', 'front5.omegle.com', 'front6.omegle.com',
               'front7.omegle.com', 'front8.omegle.com', 'front9.omegle.com']
RECAPTCHA_CHALLENGE_URL = 'http://www.google.com/recaptcha/api/challenge?k=%s'
RECAPTCHA_IMAGE_URL = 'http://www.google.com/recaptcha/api/image?c=%s'
recaptcha_challenge_regex = re.compile(r"challenge\s*:\s*'(.+)'")

class Client(threading.Thread):
    STATUS_URL = 'http://%s/status?nocache=%s&randid=%s'
    START_URL = 'http://%s/start?rcs=%s&firstevents=%s&spid=%s&randid=%s&lang=%s'
    RECAPTCHA_URL = 'http://%s/recaptcha'
    EVENTS_URL = 'http://%s/events'
    TYPING_URL = 'http://%s/typing'
    STOPPED_TYPING_URL = 'http://%s/stoppedtyping'
    DISCONNECT_URL = 'http://%s/disconnect'
    SEND_URL = 'http://%s/send'

    def __init__(self, rcs=1, firstevents=1, spid='', random_id=None, topics=[], lang='en', event_delay=3, name='Stranger'):
        threading.Thread.__init__(self)
        self.rcs = rcs
        self.firstevents = firstevents
        self.spid = spid
        self.random_id = random_id or util.randid()
        self.topics = topics
        self.lang = lang
        self.event_delay = event_delay
        self.name = name
        self.other_client = None

        self.state = 'INIT'
        self.server = random.choice(SERVER_LIST)
        self.client_id = None
        self.connected = False
        self.browser = mechanize.Browser()
        self.browser.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:32.0) Gecko/20100101 Firefox/32.0')]
        self.event_handlers = {
            'waiting': self.handle_waiting,
            'connected': self.handle_connected,
            'recaptchaRequired': self.handle_recaptcha_required,
            'recaptchaRejected': self.handle_recaptcha_required,
            'commonLikes': self.handle_common_likes,
            'typing': self.handle_typing,
            'stoppedTyping': self.handle_stopped_typing,
            'gotMessage': self.handle_got_message,
            'strangerDisconnected': self.handle_stranger_disconnected,
            'statusInfo': self.handle_dummy,
            'identDigests': self.handle_dummy
        }
        self._stop = threading.Event()
        self.common_like_timeout = 10
        url = self.START_URL % (self.server, self.rcs, self.firstevents, self.spid, self.random_id, self.lang)
        if self.topics != [None]:
            parameter = urllib.urlencode({'topics': json.dumps(self.topics)})
            url += '&' + parameter
        self.start_url = url

    def run(self):
        response = self.browser.open(self.start_url)
        data = json.load(response)
        self.client_id = data['clientID']
        self._handle_events(data['events'])

        while not self.connected:
            # print self.name + ' not connected'
            self.event()
            if self._stop.isSet():
                self.disconnect()
                return
            time.sleep(self.event_delay)

        while self.connected:
            # print self.name + ' connected'
            self.event()
            if self._stop.isSet():
                self.disconnect()
                return
            time.sleep(self.event_delay)

    def stop(self):
        if self._stop.isSet(): return
        self.state = 'STOP'
        self._stop.set()

    def register_other_client(self, other_client):
        self.other_client = other_client

    def _handle_events(self, events):
        for event in events:
            name = event[0]
            # logPrint ['event: '] + event
            if name in self.event_handlers: # can handle this event
                if len(event) > 1:
                    try:
                        self.event_handlers[name](*event[1:])
                    except TypeError:
                        util.logPrint( (name, event, self.event_handlers), level='debug')
                else:
                    self.event_handlers[name]()
            else:
                util.logPrint('Unhandled event: %s' % event)

    def handle_dummy(self, *args):
        pass

    def handle_waiting(self):
        self.state = 'WAITING'
        util.logPrint("Looking for someone you can chat with...")

    def handle_connected(self):
        self.state = 'CONNECTED'
        self.connected = True
        util.logPrint ("You're now chatting with a random stranger. Say hi!")

    def handle_recaptcha_required(self, challenge):
        self.state = 'RECAPTCHA_REQUIRED'
        util.logPrint('Captcha required. Please go to www.omegle.com and enter the captcha manually.')
        util.logPrint('Disconnecting...')
        self.stop()
        '''url = RECAPTCHA_CHALLENGE_URL % challenge
        source = self.browser.open(url).read()
        challenge = recaptcha_challenge_regex.search(source).groups()[0]
        url = RECAPTCHA_IMAGE_URL % challenge
        util.logPrint ('Recaptcha required: %s' % url)
        response = raw_input('Response: ')
        self.recaptcha(challenge, response)'''

    def handle_common_likes(self, likes):
        util.logPrint( '[%s] You both like %s.' % (self.name, ', '.join(likes)))

    def handle_typing(self):
        util.logPrint( '[%s] Stranger is typing...' % self.name)
        self.other_client.typing()

    def handle_stopped_typing(self):
        self.other_client.stopped_typing()
        #logPrint 'Stranger has stopped typing.'

    def handle_got_message(self, message):
        try:
            util.logPrint( '[%s] Stranger: %s' % (self.name, message))
        except Exception, e:
            util.logPrint( str(e))
            traceback.print_exc()
        for _ in range(3):
            try:
                self.other_client.send(message.encode('utf-8'))
                break
            except Exception:
                pass

    def handle_stranger_disconnected(self):
        self.connected = False
        util.logPrint( '[%s] Stranger has disconnected.' % self.name)
        self.disconnect()
        self.other_client.disconnect()

    def status(self):
        server = random.choice(SERVER_LIST)
        url = self.STATUS_URL % (server, util.nocache(), self.random_id)
        response = self.browser.open(url)
        data = json.load(response)
        return data

    def recaptcha(self, challenge, response):
        url = self.RECAPTCHA_URL % self.server
        data = {'id': self.client_id, 'challenge':
                challenge, 'response': response}
        try:
            self.browser.open(url, urllib.urlencode(data))
        except BadStatusLine:
            return

    def event(self):
        url = self.EVENTS_URL % self.server
        data = {'id': self.client_id}
        try:
            #print self.name + ' state: ' + self.state
            if self.state == 'CONNECTED':
                response = self.browser.open(url, urllib.urlencode(data))
            else:
                response = self.browser.open(url, urllib.urlencode(data), util.WAIT_TIMEOUT)
            data = json.load(response)
        except URLError, e:
            if (self.topics[0] != None) and (e.reason.message == 'timed out'):
                util.logPrint('Failed to find anyone with interest ' + self.topics[0])
                self.stop()
                # TODO: send stoplookingforcommonlikes to omegle server
            return
        except Exception:
            return
        if data:
            self._handle_events(data)

    def typing(self):
        url = self.TYPING_URL % self.server
        data = {'id': self.client_id}
        try:
            self.browser.open(url, urllib.urlencode(data))
        except BadStatusLine:
            return

    def stopped_typing(self):
        url = self.STOPPED_TYPING_URL % self.server
        data = {'id': self.client_id}
        try:
            self.browser.open(url, urllib.urlencode(data))
        except BadStatusLine:
            return

    def send(self, message):
        url = self.SEND_URL % self.server
        data = {'msg': message, 'id': self.client_id}
        try:
            self.browser.open(url, urllib.urlencode(data))
        except BadStatusLine:
            return

    def disconnect(self):
        self.connected = False
        url = self.DISCONNECT_URL % self.server
        data = {'id': self.client_id}
        try:
            self.browser.open(url, urllib.urlencode(data))
        except BadStatusLine:
            return