# OSC test


import argparse
import random
import time

from pythonosc.udp_client import SimpleUDPClient
from threading import Thread
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer


class MessageSender:
    def __init__(self):
        self.client = SimpleUDPClient("127.0.0.1", 6000)

    def sendMessage(self, adress, messages):
        self.client.send_message(adress, messages)

sender = MessageSender()


class MessageReceiver(Thread):
    def __init__(self, port):
        Thread.__init__(self)
        self.dispatcher = Dispatcher()
        self.server = BlockingOSCUDPServer(('127.0.0.1', port), self.dispatcher)
        self.dispatcher.set_default_handler(self.handler)
        self.start()

    def run(self):
        self.server.serve_forever()

    def handler(self, adress, *args):
        print(f'handler: {adress}: {args}')

    def addHandler(self, message, handler):
        self.dispatcher.map(message, handler)

    def setDefaultHandler(self, handler):
        self.dispatcher.set_default_handler(handler)
'''

receiver = MessageReceiver(5000)

def wheelLeftHandler(adress, *args):
    print('receiver')
    sender.sendMessage('global/', f'left tick handled: {args}')

def wheelRightHandler(adress, *args):
    sender.sendMessage('global/', f'right tick handled {args}')



receiver.addHandler('/*', wheelLeftHandler)
receiver.addHandler('/wheel/right/*', wheelRightHandler)

print('end')
'''
