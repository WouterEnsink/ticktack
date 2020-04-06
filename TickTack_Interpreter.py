# TickTack Interpreter

from TickTack_Parser import Parser
import json, sys



class Scope:

    def __init__(self, parent=None):
        self.parent, self.variables, self.functionDefinitions, self.oscCallbacks = parent, {}, {}, {}
        self.returnValue = '[undifined]'
        self.outlets = {}
        self.constants = {}


    def setValueForIdentifier(self, identifier, value):
        if identifier in self.variables:
            self.variables[identifier] = value
            return

        if identifier in self.constants:
            print(f'Error: trying to assign value to constant "{identifier}"')
            return

        if self.parent != None:
            return self.parent.setValueForIdentifier(identifier, value)

        print(f'didn\'t find variable "{identifier}"')


    def addVariable(self, identifier, value):
        self.variables[identifier] = value


    def addConstant(self, identifier, value):
        self.constants[identifier] = value


    def addFunctionDefinition(self, identifier, functionDefinition):
        self.functionDefinitions[identifier] = functionDefinition


    def addOutlet(self, identifier, address):
        self.outlet[identifier] = address


    def addOpenSoundControlCallback(self, adress, callback):
        self.oscCallbacks[adress] = callback


    def lookUpOutlet(self, identifier):
        if identifier in self.outlets:
            return self.outlets[identifier]

        if self.parent != None:
            return self.parent.lookUpOutlet(identifier)

        return None


    def lookUpCallback(self, address):
        if address in self.oscCallbacks:
            return self.oscCallbacks[address]

        print(f'Error: did not find OSC callback "{address}"')
        return None


    def lookUpFunction(self, identifier):
        if identifier in self.functionDefinitions:
            return self.functionDefinitions[identifier]

        if self.parent != None:
            return self.parent.lookUpFunction(identifier)

        print(f'did not find function "{identifier}", there were a total of {len(self.functionDefinitions)}')
        return None


    def lookUpVariable(self, identifier):
        if identifier in self.variables:
            return self.variables[identifier]

        if identifier in self.constants:
            return self.constants[identifier]

        if self.parent != None:
            return self.parent.lookUpVariable(identifier)

        print(f'Error: variable "{identifier}" does not exist')
        return None


    def setReturnValue(self, newValue):
        self.returnValue = newValue




class Result:
    ok, returnWasHit = 0, 1


class Interpreter:
    def __init__(self):
        self.tree = None
        self.globalScope = Scope()


    def openSyntaxTree(self, path):
        with open(path, 'r') as file:
            self.tree = json.load(file)


    def invokeOpenSoundControlCallback(self, address, arguments):
        callback = self.globalScope.lookUpCallback(address)
        if callback == None:
            return

        fnScope = Scope(parent=self.globalScope)
        if len(arguments) > 0:
            fnScope.addConstant('__tick__', arguments[0])

        self.traverseBlockStatement(callback['body']['block_statement'], fnScope)


    def traverseScript(self):
        self.traverseBlockStatement(self.tree['root']['block_statement'], self.globalScope)


    def traverseBlockStatement(self, block, scope):
        for s in block:
            if self.traverseStatement(s, scope) == Result.returnWasHit:
                return Result.returnWasHit

        return Result.ok


    def traverseStatement(self, statement, scope):
        if 'variable_declaration' in statement:
            return self.traverseVariableDeclaration(statement['variable_declaration'], scope)
        if 'block_statement' in statement:
            return self.traverseBlockStatement(statement['block_statement'], scope)
        if 'function_definition' in statement:
            return self.traverseFunctionDefinition(statement['function_definition'], scope)
        if 'expression_statement' in statement:
            self.traverseExpression(statement['expression_statement'], scope)
            return Result.ok
        if 'print_statement' in statement:
            return self.traversePrintStatement(statement['print_statement'], scope)
        if 'return_statement' in statement:
            return self.traverseReturnStatement( statement['return_statement'], scope)
        if 'if_statement' in statement:
            return self.traverseIfStatement(statement['if_statement'], scope)
        if 'osc_callback_definition' in statement:
            return self.traverseOSC_CallbackDefinition(statement['osc_callback_definition'], scope)
        if 'outlet_declaration' in statement:
            return self.traverseOutletDeclaration(statement['outlet_declaration'], scope)

        print(f'Interpreter Error: Unknown Statement Type')


    def traverseOutletDeclaration(self, node, scope):
        scope.outlets[node['identifier']] = node['address']
        return Result.ok


    def traverseOSC_CallbackDefinition(self, node, scope):
        scope.addOpenSoundControlCallback(node['address'], node)
        return Result.ok


    def traverseFunctionDefinition(self, node, scope):
        scope.addFunctionDefinition(node['identifier'], node)
        return Result.ok


    def traverseReturnStatement(self, node, scope):
        scope.returnValue = self.traverseExpression(node['expression'], scope)
        return Result.returnWasHit


    def traversePrintStatement(self, node, scope):
        exprs = ', '.join([str(self.traverseExpression(i, scope)) for i in node])
        print(f'TickTack: {exprs}')
        return Result.ok


    def traverseIfStatement(self, node, parentScope):
        cond = self.traverseExpression(node['condition'], parentScope) != 0

        if cond == True:
            ifScope = Scope(parent=parentScope)
            if self.traverseStatement(node['if_block'], ifScope) == Result.returnWasHit:
                parentScope.returnValue = ifScope.returnValue
                return Result.returnWasHit

        elif node['else_block'] != None:
            elseScope = Scope(parent=parentScope)
            if self.traverseStatement(node['else_block'], elseScope) == Result.returnWasHit:
                parentScope.returnValue = elseScope.returnValue
                return Result.returnWasHit

        return Result.ok


    def traverseVariableDeclaration(self, node, scope):
        identifier, constant = node['identifier'], node['constant']
        expression = self.traverseExpression(node['expression'], scope)

        if constant:
            scope.addConstant(identifier, expression)
        else:
            scope.addVariable(identifier, expression)

        return Result.ok


    def traverseExpression(self, expression, scope):
        if '=' in expression:
            return self.traverseAssignment(expression['='], scope)

        for o in ['+=', '-=', '*=', '/=', '%=']:
            if o in expression:
                return self.traverseSelfAssignment(o, expression[o], scope)

        for o in ['+', '-', '*', '/', '%', '==', '&&', '||', '!=', '>', '<', '>=', '<=']:
            if o in expression:
                return self.traverseBinary(o, expression[o], scope)

        if 'function_call' in expression:
            return self.traverseFunctionCall(expression['function_call'], scope)

        if 'unqualified_name' in expression:
            return scope.lookUpVariable(expression['unqualified_name'])

        if 'numeric_literal' in expression:
            return expression['numeric_literal']


    def traverseBinary(self, type, node, scope):
        lhs, rhs = self.traverseExpression(node[0], scope), self.traverseExpression(node[1], scope)
        if type == '+':  return lhs +   rhs
        if type == '-':  return lhs -   rhs
        if type == '*':  return lhs *   rhs
        if type == '/':  return lhs /   rhs
        if type == '%':  return lhs %   rhs
        if type == '==': return lhs ==  rhs
        if type == '!=': return lhs !=  rhs
        if type == '&&': return lhs and rhs
        if type == '||': return lhs or  rhs
        if type == '>=': return lhs >=  rhs
        if type == '>':  return lhs >   rhs
        if type == '<=': return lhs <=  rhs
        if type == '<':  return lhs <   rhs


    def traverseSelfAssignment(self, type, node, scope):
        val = self.traverseExpression(node[1], scope)
        varId = node[0]['unqualified_name']
        varVal = scope.lookUpVariable(varId)

        if type == '+=': varVal += val
        if type == '-=': varVal -= val
        if type == '*=': varVal *= val
        if type == '/=': varVal /= val
        if type == '%=': varVal %= val

        scope.setValueForIdentifier(varId, varVal)
        return varVal


    def traverseFunctionCall(self, node, parentScope):

        args = [self.traverseExpression(arg, parentScope) for arg in node['arguments']]
        identifier = node['identifier']
        outlet = parentScope.lookUpOutlet(identifier)
        if outlet != None:
            self.sendDataToOutlet(outlet, args)
            return

        function = parentScope.lookUpFunction(identifier)
        fnScope = Scope(parent=parentScope)
        for argID, val in zip(function['arguments'], args):
            fnScope.addVariable(argID, val)

        self.traverseBlockStatement(function['body']['block_statement'], fnScope)
        return fnScope.returnValue


    def traverseAssignment(self, node, scope):
        varID = node[0]['unqualified_name']
        value = self.traverseExpression(node[1], scope)
        scope.setValueForIdentifier(varID, value)
        return value


    # meant to be overridden by subclass
    def sendDataToOutlet(self, outlet, data):
        print(f'TickTack: Sending data to "{outlet}": {data}')


#---------------------------------------------------------------------------------------

if __name__ == '__main__':
    path = sys.argv[1]
    print(f'TickTack: loading "{path}"')

    i = Interpreter()
    try:
        i.openSyntaxTree(path)
        i.traverseScript()
        for x in range(100):
            i.invokeOpenSoundControlCallback('/tick', [x])
    except Exception as error:
        print(f'TickTack Interpreter Error: {error}')
