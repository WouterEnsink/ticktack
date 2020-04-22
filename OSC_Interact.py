# OSC test


import argparse
import random
import time

from pythonosc.udp_client import SimpleUDPClient
from threading import Thread
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer


class MessageSender:
    def __init__(self, port):
        self.client = SimpleUDPClient("127.0.0.1", port)

    def sendMessage(self, address, messages):
        print(f'sending message {address}: {messages}')
        self.client.send_message(address, messages)



class MessageReceiver:
    def __init__(self, port):
        print(f'Setting up Receiver with port: {port}')
        self.dispatcher = Dispatcher()
        self.server = BlockingOSCUDPServer(('127.0.0.1', port), self.dispatcher)
        self.dispatcher.set_default_handler(self.handleMessage)
        self.thread = Thread(target=self.run)
        self.thread.start()


    def run(self):
        self.server.serve_forever()
        print('done with receiver thread')


    def handleMessage(self, adress, *args):
        print(f'handler: {adress}: {args}')

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
