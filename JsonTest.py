# JSON Test

import json



class Scope:
    def __init__(self, parent = None):
        self.variables, self.parent = {}, parent

    def setValueForIdentifier(self, identifier, value):
        self.variables[identifier] = value
        print(f'set id {identifier} to {value}')

    def lookUpVariable(self, identifier):
        if not identifier in self.variables:
            print(f'Error trying to acces undifined variable {identifier}')
            return None

        return self.variables[identifier]

    def assignNewValueToIdentifier(self, identifier, value):
        if not identifier in self.variables:
            print(f'Error can not assign to undeclared identifier {identifier}')
            return

        self.variables[identifier] = value
        print(f'set new value for {identifier}: {value}')


rootScope = Scope()

def traverseRoot(tree):
    if tree['language'] != 'TickTack':
        print('Not a TickTack Parse Tree')

    traverseBlockStatement(tree['root_scope'])

def traverseBlockStatement(blockNode):
    for statement in blockNode:
        if statement == 'variable_declaration':
            traverseVariableDeclaration(blockNode[statement])

        elif statement == 'assignment':
            traverseAssignment(blockNode[statement])


def traverseBinaryOperationPlus(node):
    return traverseExpression(node['left_operant']) + traverseExpression(node['right_operant'])

def traverseBinaryOperationModulo(node):
    return traverseExpression(node['left_operant']) % traverseExpression(node['right_operant'])

def traverseExpression(exprNode):
    if 'binary_operation_plus' in exprNode:
        return traverseBinaryOperationPlus(exprNode['binary_operation_plus'])
    if 'binary_operation_modulo' in exprNode:
        return traverseBinaryOperationModulo(exprNode['binary_operation_modulo'])
    if 'numeric_literal' in exprNode:
        return exprNode['numeric_literal']
    if 'unqualified_name' in exprNode:
        return rootScope.lookUpVariable(exprNode['unqualified_name'])


def traverseVariableDeclaration(declarationNode):
    identifier = declarationNode['identifier']
    value = traverseExpression(declarationNode['expression'])
    rootScope.setValueForIdentifier(identifier, value)

def traverseAssignment(node):
    identifier = node['identifier']
    value = traverseExpression(node['expression'])
    rootScope.assignNewValueToIdentifier(identifier, value)

def traverseFunctionCall(node):
    identifier = node['identifier']
    args = [traverseExpression(a['expression']) for a in node['arguments']]

    rootScope.lookUpFunction(identifier)


#traverseRoot(tree)

root = {"list": []}

def get():
    return { "vardecl": { "id": "foo", "expr": { "num_lit": 6 }}}

for _ in range(10):
    root["list"].append(get())

print(json.dumps(root, indent=5))
