from TickTack_Interpreter import Interpreter
from TickTack_Parser import Parser
from OSC_Interact import MessageSender, MessageReceiver
from FileListener import FileChangeListener
import sys, json


class ChangeHandler(FileChangeListener):
    def __init__(self, filePath):
        FileChangeListener.__init__(self, './' + filePath)
        self.currentTree = self.attemptParsing(filePath)



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


    def fileChanged(self, path):
        print(f'File Changed: {path}')
        tree = self.attemptParsing(path)



class Runtime(Interpreter, MessageSender, MessageReceiver):
    def __init__(self, receiverPort, senderPort):
        super(MessageSender, self).__init__(senderPort)
        super(MessageReceiver, self).__init__(receiverPort)
        self.syntaxTree = None


    def handleMessage(self, address, *args):
        print(f'Runtime OSC Receive: {address}: {args}')




if __name__ == '__main__':
    path = sys.argv[1]
    print(f'start ChangeHandler test: {path}')
    handler = ChangeHandler(path)
    handler.startListening()
