# TickTack Interpreter

from JSON_Parser import Parser
import json, sys

class Interpreter:
    def __init__(self):
        self.tree = None
        self.globalScope = None

    def openSyntaxTree(self, path):
        with open(path, 'r') as file:
            self.tree = json.load(file)

    def traverseScript(self):
        print(json.dumps(self.tree, indent = 2))
        self.traverseBlockStatement(self.tree['root']['block_statement'])

    def traverseBlockStatement(self, block):
        blockScope = None
        for s in block:
            self.traverseStatement(s, blockScope)

    def traverseStatement(self, statement):
        if 'variable_declaration' in statement:
            return self.traverseVariableDeclaration(statement['variable_declaration'])
        if 'block_statement' in statement:
            return self.traverseBlockStatement(statement['block_statement'])
        if 'function_definition' in statement:
            return self.traverseFunctionDefinition(statement['function_definition'])
        if 'expression_statement' in statement:
            return self.traverseExpression(statement['expression_statement'])

    def traverseExpression(self, expression):
        if 'assignment' in expression:
            return self.traverseAssignment(expression['assignment'])
        if 'binary_operation' in expression:
            return self.traverseBinaryOperation(expression['binary_operation'])


if __name__ == '__main__':
    path = sys.argv[1]
    print(f'TickScript loading "{path}"')

    i = Interpreter()
    i.openSyntaxTree(path)
    i.traverseScript()
