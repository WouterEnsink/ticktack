from TickTack_Interpreter import Interpreter
from TickTack_Parser import Parser
from OSC_Interact import MessageSender, MessageReceiver
from FileListener import FileChangeListener
import sys, json


class ChangeHandler(FileChangeListener):
    def __init__(self, filePath):
        FileChangeListener.__init__(self, './' + filePath)
        self.changeHandler = None
        self.fileChanged(filePath)
        self.startListening()


    def fileChanged(self, path):
        if self.changeHandler != None:
            self.changeHandler(path)


    def setCallback(self, func):
        self.changeHandler = func



class Runtime(Interpreter, MessageSender, MessageReceiver):
    def __init__(self, filePath, receiverPort, senderPort):
        Interpreter.__init__(self)
        MessageSender.__init__(self, senderPort)
        MessageReceiver.__init__(self, receiverPort)
        self.changeHandler = ChangeHandler(filePath)
        self.changeHandler.setCallback(self.fileChanged)


    def handleMessage(self, address, *args):
        print(f'Runtime OSC Receive: {address}: {args}')
        self.invokeOpenSoundControlCallback(address, args)


    def sendDataToOutlet(self, outlet, data):
        print(f'Runtime OSC Send: {outlet}, {data}')
        self.sendMessage(outlet, data)


    def fileChanged(self, path):
        tree = self.attemptParsing(path)

        if tree != None:
            self.runScript(tree)


    def attemptParsing(self, filePath):
        tree = None

        with open(filePath, 'r') as file:
            data = file.read()

            try:
                p = Parser(data)
                tree = p.parse()
                print(f'TickTack: Succesfully parsed {filePath}')
            except Exception as error:
                print(f'{error}, Parser Result Discarded')

        return tree






if __name__ == '__main__':
    path, receivingPort, sendingPort = sys.argv[1:4]
    print(f'path {path}, r {receivingPort}, s {sendingPort}')
    runtime = Runtime(path, int(receivingPort), int(sendingPort))

    #path = sys.argv[1]
    #print(f'Start ChangeHandler test: {path}')
    #handler = ChangeHandler(path)
    #handler.startListening()
