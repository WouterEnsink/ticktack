# TickScript Interpreter

from OSC_Interact import MessageReceiver, MessageSender
from enum import Enum

class Tokens:
    comma               = ','
    dot                 = '.'
    quote               = '\''
    equals              = '=='
    logicalAnd          = '&&'
    logicalOr           = '||'
    notEquals           = '!='
    logicalNot          = '!'
    greaterThanEquals   = '>='
    lessThanEquals      = '<='
    greaterThan         = '>'
    lessThan            = '<'
    assign              = '='
    colon               = ':'
    doubleArrow         = '<->'
    arrowLeft           = '<-'
    arrowRight          = '->'
    greaterThan         = '>'
    lessThan            = '<'
    openBracket         = '['
    closeBracket        = ']'
    stripe              = '|'
    arrowLeft           = '<-'
    arrowRight          = '->'
    endOfFile           = 'EOF'
    newLine             = '\n'
    openParentheses     = '('
    closeParentheses    = ')'
    openBraces          = '{'
    closeBraces         = '}'
    plusEquals          = '+='
    minusEquals         = '-='
    timesEquals         = '*='
    devideEquals        = '/='
    moduloEquals        = '%='
    times               = '*'
    devide              = '/'
    modulo              = '%'
    plus                = '+'
    minus               = '-'

    operators = [comma, dot, equals, notEquals, logicalNot, logicalAnd, logicalOr, greaterThanEquals, lessThanEquals, greaterThan, lessThan,
                 assign, colon, doubleArrow, arrowLeft, arrowRight, greaterThan, lessThan, openBracket,
                 closeBracket, stripe, arrowLeft, arrowRight, endOfFile, newLine, openParentheses,
                 closeParentheses, openBraces, closeBraces, plusEquals, minusEquals, timesEquals, devideEquals,
                 moduloEquals, times, devide, modulo, plus, minus]

    wheelKeyword        = 'wheel'
    returnKeyword       = 'return'
    funcKeyword         = 'func'
    printKeyword        = 'print'
    outletKeyword       = 'outlet'
    varKeyword          = 'var'
    letKeyword          = 'let'
    trueKeyword         = 'true'
    falseKeyword        = 'false'
    ifKeyword           = 'if'
    elseKeyword         = 'else'

    keywords = [wheelKeyword, returnKeyword, funcKeyword, printKeyword,
                outletKeyword, varKeyword, letKeyword, trueKeyword, falseKeyword,
                ifKeyword, elseKeyword]

    keywordType         = 'keyword'
    identifierType      = 'identifier'
    numericLiteralType  = 'numeric'
    operatorType        = 'operator'
    stringLiteralType   = 'string'

    def isKeyword(word):
        for value in Tokens.keywords:
            if value == word:
                return True
        return False

    def isIdentifierBody(charToCheck):
        return charToCheck.isnumeric() or charToCheck.isalpha() or charToCheck == '_'

# -----------------------------------------------------------------------------------------

class CodeLocation:
    def __init__(self, code):
        self.code, self.index = code, 0

    def getLineNumber(self):
        num, i = 1, 0
        while i < self.index:
            if self.code[i] == '\n':
                num += 1
            i += 1

        return num

    def copyCurrentLocation(self):
         l = CodeLocation(self.code)
         l.index = self.index
         return l

    def throwLocationError(self, errorMessage):
        #print(f'TickScript Error on line {self.getLineNumber()}: {errorMessage}')
        raise Exception(f'TickScript Error on line {self.getLineNumber()}: {errorMessage}')

# -----------------------------------------------------------------------------------------

class TokenIterator(CodeLocation):
    def __init__(self, code):
        super(TokenIterator, self).__init__(code)
        self.currentTokenValue, self.currentTokenType = '', ''

    def advance(self):
        self.skipWhiteSpaceAndComments()

        if (self.index >= len(self.code)):
            self.currentTokenValue = Tokens.endOfFile
            return self.currentTokenValue

        return self.matchNextToken()

    def advanceIfTokenValueIsExpected(self, expectedValue):
        if expectedValue != self.currentTokenValue:
            return False
        self.advance()
        return True

    def advanceIfTokenTypeIsExpected(self, expectedType):
        if expectedType != self.currentTokenType:
            return False
        self.advance()
        return True

    def matchAnyOfTokenValues(self, expectedTokenValues):
        for t in expectedTokenValues:
            if t == self.currentTokenValue:
                return True
        return False

    def skipWhiteSpaceAndComments(self):
        while self.index < len(self.code) and (self.code[self.index] == ' ' or self.code[self.index] == '\t'):
            self.index += 1

        if self.code[self.index : self.index + 2] == '//':
            while self.code[self.index] != Tokens.newLine:
                self.index += 1
                if self.index == len(self.code):
                    return

        if self.code[self.index : self.index + 2] == '/*':
            while self.code[self.index : self.index + 2] != '*/':
                self.index += 1
                if self.index >= len(self.code):
                    self.throwLocationError("Unterminated multi-line comment")
                    break
            self.index += 2

        while self.index < len(self.code) and (self.code[self.index] == ' ' or self.code[self.index] == '\t'):
            self.index += 1

    def matchNextToken(self):
        if self.attemptOperator() or self.attemptIdentifierOrKeyword():
            return self.currentTokenValue

        if self.attemptNumericLiteral() or self.attemptStringLiteral():
            return self.currentTokenValue

        self.throwLocationError(f"Unknown token: {self.code[self.index]}")
        self.index += 1


    def attemptIdentifierOrKeyword(self):
        if not self.code[self.index].isalpha():
            return False

        identifier = ''
        i = self.index
        while i < len(self.code) and Tokens.isIdentifierBody(self.code[i]):
            identifier += self.code[i]
            i += 1

        self.currentTokenType = Tokens.keywordType if Tokens.isKeyword(identifier) else Tokens.identifierType
        self.currentTokenValue = identifier
        self.index += len(identifier)
        return True

    def attemptOperator(self):
        for value in Tokens.operators:
            if self.code[self.index : self.index + len(value)] == value:
                self.currentTokenType, self.currentTokenValue = Tokens.operatorType, value
                self.index += len(value)
                return True
        return False

    def attemptNumericLiteral(self):
        if not self.code[self.index].isnumeric():
            return False

        number, i, numDots = '', self.index, 0

        while i < len(self.code) and (self.code[i].isnumeric() or self.code[i] == '.'):
            if self.code[i] == '.' and numDots == 1:
                break
            number += self.code[i]
            i += 1

        self.currentTokenType, self.currentTokenValue, self.index = Tokens.numericLiteralType, number, i
        return True

    def attemptStringLiteral(self):
        if self.code[self.index] != '\'':
            return False

        i, string = self.index + 1, ''

        while self.code[i] != Tokens.quote:
            string, i = string + self.code[i], i + 1

        self.currentTokenType, self.currentTokenValue, self.index = Tokens.stringLiteralType, string, i + 1
        return True



# -----------------------------------------------------------------------------------------

def testTokenIterator(code):
    iterator, tokens = TokenIterator(code), []
    while True:
        iterator.advance()
        tokens.append([iterator.currentTokenType, iterator.currentTokenValue])
        if iterator.currentTokenValue == Tokens.endOfFile:
            break

    for type, value in tokens:
        print(f"type {type}, value {value if value != Tokens.newLine else 'newLine'}")


# -----------------------------------------------------------------------------------------

class ResultCodes(Enum):
    ok, returnWasHit = 0, 1

class Statement:
    def perform(self, scope):
        print('error: using Statement base class')
        return ResultCodes.ok

class Expression(Statement):
    def evaluate(self, scope):
        print('error: using Expression base class')

class BinaryOperation(Expression):
    def __init__(self, left, token, right):
        self.lhs, self.token, self.rhs = left, token, right

    def evaluate(self, scope):
        left, right = self.lhs.evaluate(scope), self.rhs.evaluate(scope)

        if self.token == Tokens.plus:
            return left + right
        if self.token == Tokens.minus:
            return left - right
        if self.token == Tokens.times:
            return left * right
        if self.token == Tokens.devide:
            return left / right
        print(f'Error unsupported token for BinaryOperation: {self.token}')

class UnaryOperation(Expression):
    def __init__(self, token, right):
        self.token, self.rightOperant = token, right

    def evaluate(self, scope):
        if self.token == Tokens.minus:
            return self.rightOperant.evaluate() * -1
        return self.rightOperant.evaluate()

class NumericLiteral(Expression):
    def __init__(self, value):
        self.value = value

    def evaluate(self, scope):
        return float(self.value)

class UnqualifiedName(Expression):
    def __init__(self, identifier):
        self.identifier = identifier

    def evaluate(self, scope):
        return float(scope.lookUpVariable(self.identifier))

    def assignValue(self, scope, newValue):
        scope.setValueForIdentifier(self.identifier, newValue)

class Scope:
    def __init__(self, parent=None):
        self.parent, self.variables, self.functionDefinitions, self.oscCallbacks = parent, {}, {}, {}
        self.returnValue = '[undifined]'

    def setValueForIdentifier(self, identifier, value):
        self.variables[identifier] = value

    def addFunctionDefinition(self, identifier, functionDefinition):
        self.functionDefinitions[identifier] = functionDefinition

    def addOpenSoundControlCallback(self, adress, callback):
        print(f'adding osc callback {adress}')
        self.oscCallbacks[adress] = callback

    def invokeOpenSoundControlCallback(self, adress, args):
        print('invoking osc callback')
        callback = self.oscCallbacks[adress]
        argIds = callback.args

        functionScope = Scope(parent=self)

        for index, identifier in enumerate(argIds):
            print(f'setting {identifier} {args}')
            functionScope.setValueForIdentifier(identifier, args)

        callback.body.perform(functionScope)

    def lookUpFunction(self, identifier):
        for i, f in self.functionDefinitions.items():
            if i == identifier:
                return f
        if self.parent != None:
            return self.parent.lookUpFunction(identifier)

        print(f'did not find function {identifier}, there were a total of {len(self.functionDefinitions)}')
        return None

    def lookUpVariable(self, identifier):
        for i, v in self.variables.items():
            if i == identifier:
                return v
        if self.parent != None:
            return self.parent.lookUpVariable(identifier)
        print(f'error: variable with name {identifier} does not exist')
        return None

    def setReturnValue(self, newValue):
        self.returnValue = newValue


class BlockStatement(Statement):
    def __init__(self):
        self.statements = []

    def addStatement(self, statement):
        self.statements.append(statement)

    def perform(self, scope):
        for statement in self.statements:
            code = statement.perform(scope)
            if code != ResultCodes.ok:
                return code
        return ResultCodes.ok


class FunctionDefinition(Statement):
    def __init__(self, identifier, argumentList, body):
        self.identifier, self.argumentIdentifiers, self.body = identifier, argumentList, body

    def perform(self, scope):
        scope.addFunctionDefinition(self.identifier, self)
        return ResultCodes.ok

class FunctionCall(Expression):
    def __init__(self, identifier, arguments):
        self.identifier, self.arguments = identifier, arguments

    def perform(self, scope):
        self.evaluate(scope)
        return ResultCodes.ok

    def evaluate(self, scope):
        function, functionScope = scope.lookUpFunction(self.identifier), Scope(parent=scope)

        for identifier, value in zip(function.argumentIdentifiers, self.arguments):
            functionScope.setValueForIdentifier(identifier, float(value.evaluate(scope)))

        function.body.perform(functionScope)
        return functionScope.returnValue

class Assignment(Expression):
    def __init__(self, unqualifiedName, expression):
        self.unqualifiedName, self.expression = unqualifiedName, expression

    def perform(self, scope):
        self.evaluate(scope)
        return ResultCodes.ok

    def evaluate(self, scope):
        result = self.expression.evaluate(scope)
        self.unqualifiedName.assignValue(scope, float(result))
        return result

class PrintStatement(Statement):
    def __init__(self, arguments):
        self.arguments = arguments

    def perform(self, scope):
        args = [arg.evaluate(scope) for arg in self.arguments]
        print(f'TickScript: {args}')
        return ResultCodes.ok

class EmptyStatement(Statement):
    def __init__(self):
        pass

    def perform(self, scope):
        return ResultCodes.ok

class OpenSoundControlCallbackDefinition(Statement):
    def __init__(self, adress, args, body):
        print(f'new osc def {adress}')
        self.adress, self.args, self.body = adress, args, body

    def perform(self, scope):
        scope.addOpenSoundControlCallback(self.adress, self)
        return ResultCodes.ok

class ReturnStatement(Statement):
    def __init__(self, expression):
        self.expression = expression

    def perform(self, scope):
        scope.setReturnValue(self.expression.evaluate(scope))
        return ResultCodes.returnWasHit


# -----------------------------------------------------------------------------------------


class Parser(TokenIterator):
    def __init__(self, code):
        super(Parser, self).__init__(code)


    def parse(self):
        self.advance()
        return self.parseStatementList()


    def parseReturnStatement(self):
        return ReturnStatement(self.parseExpression())


    def parsePrintStatement(self):
        self.advanceIfTokenValueIsExpected(Tokens.openParentheses)
        args = [self.parseExpression()]
        while self.currentTokenValue != Tokens.closeParentheses:
            self.advanceIfTokenValueIsExpected(Tokens.comma)
            args.append(self.parseExpression())

        self.advance()
        return PrintStatement(args)


    def parseStatement(self):
        while self.currentTokenValue == Tokens.newLine:
            self.advance()

        if self.currentTokenType == Tokens.stringLiteralType:
            return self.parseOpenSoundControlCallback()

        if self.currentTokenValue == Tokens.openBraces:
            return self.parseBlockStatement()

        if self.advanceIfTokenValueIsExpected(Tokens.controllerKeyword):
            return self.parseController()

        if self.advanceIfTokenValueIsExpected(Tokens.returnKeyword):
            return self.parseReturnStatement()

        if self.advanceIfTokenValueIsExpected(Tokens.funcKeyword):
            return self.parseFunctionDefinition()

        if self.advanceIfTokenValueIsExpected(Tokens.printKeyword):
            return self.parsePrintStatement()

        if self.currentTokenType == Tokens.identifierType or self.currentTokenType == Tokens.numericLiteralType:
            return self.parseExpression()

        if self.currentTokenType == Tokens.openParentheses:
            return self.parseFactor()

        return EmptyStatement()


    def parseBlockStatement(self):
        while self.currentTokenValue != Tokens.openBraces and self.currentTokenValue != Tokens.endOfFile:
            self.advance()

        self.advanceIfTokenValueIsExpected(Tokens.openBraces)
        block = self.parseStatementList()
        self.advanceIfTokenValueIsExpected(Tokens.closeBraces)
        return block


    def parseStatementList(self):
        blockStatement = BlockStatement()

        if self.currentTokenValue != Tokens.closeBraces:
            blockStatement.addStatement(self.parseStatement())

        while self.currentTokenValue != Tokens.closeBraces and self.currentTokenValue != Tokens.endOfFile:
            if not self.advanceIfTokenValueIsExpected(Tokens.newLine):
                self.throwLocationError(f'Expected newline before statement, current token: {self.currentTokenValue}')

            while self.currentTokenValue == Tokens.newLine:
                self.advance()

            if self.currentTokenValue != Tokens.endOfFile and self.currentTokenValue != Tokens.closeBraces:
                blockStatement.addStatement(self.parseStatement())
            self.throwLocationError(f'current iteration of block paring: {self.currentTokenValue}')

        return blockStatement


    def parseFunctionDefinition(self):
        identifier = self.currentTokenValue
        self.advanceIfTokenTypeIsExpected(Tokens.identifierType)
        self.advanceIfTokenValueIsExpected(Tokens.openParentheses)

        arguments = []
        while self.currentTokenValue != Tokens.closeParentheses:
            arguments.append(self.currentTokenValue)
            self.advanceIfTokenTypeIsExpected(Tokens.identifierType)
            self.advanceIfTokenValueIsExpected(Tokens.comma)

        self.advance()
        block = self.parseBlockStatement()

        return FunctionDefinition(identifier, arguments, block)


    def parseOpenSoundControlCallback(self):
        adress = self.currentTokenValue
        self.advance()
        self.advanceIfTokenValueIsExpected(Tokens.arrowRight)
        self.advanceIfTokenValueIsExpected(Tokens.openParentheses)
        argIds = []

        while self.currentTokenValue != Tokens.closeParentheses:
            argIds.append(self.currentTokenValue)
            self.advanceIfTokenTypeIsExpected(Tokens.identifierType)
            self.advanceIfTokenTypeIsExpected(Tokens.comma)

        self.advance()
        self.throwLocationError(f'parsing {adress} callback')
        block = self.parseBlockStatement()
        return OpenSoundControlCallbackDefinition(adress, argIds, block)


    def parseController(self):
        pass


    def parseControllerMemberFunctionCall(self, identifier):
        pass


    def parseFunctionCall(self, identifier):
        args = [self.parseExpression()]
        while self.currentTokenValue != Tokens.closeParentheses:
             self.advanceIfTokenValueIsExpected(Tokens.comma)
             args.append(self.parseExpression())

        self.advance()
        return FunctionCall(identifier, args)


    def parseSuffix(self, expression):
        if self.advanceIfTokenValueIsExpected(Tokens.openParentheses):
            return self.parseFunctionCall(expression.identifier)

        if self.advanceIfTokenValueIsExpected(Tokens.dot):
            return self.parseControllerFunctionCall(expression.identifier)

        return expression


    def parseFactor(self):
        token = self.currentTokenValue

        if self.advanceIfTokenTypeIsExpected(Tokens.identifierType):
            return self.parseSuffix(UnqualifiedName(token))

        if self.advanceIfTokenTypeIsExpected(Tokens.numericLiteralType):
            return NumericLiteral(token)

        if self.advanceIfTokenValueIsExpected(Tokens.openParentheses):
            exp = self.parseExpression()
            self.advanceIfTokenValueIsExpected(Tokens.closeParentheses)
            return exp


    def parseUnary(self):
        if self.advanceIfTokenValueIsExpected(Tokens.minus):
            return UnaryOperation(Tokens.minus, self.parseUnary())
        if self.advanceIfTokenValueIsExpected(Tokens.plus):
            return self.parseUnary()

        return self.parseFactor()


    def parseMultiplyDevide(self):
        lhs, token = self.parseUnary(), self.currentTokenValue

        if token == Tokens.times or token == Tokens.devide:
            self.advance()
            return BinaryOperation(lhs, token, self.parseUnary())

        return lhs


    def parseAdditionSubtraction(self):
        lhs, token = self.parseMultiplyDevide(), self.currentTokenValue

        if token == Tokens.plus or token == Tokens.minus:
            self.advance()
            return BinaryOperation(lhs, token, self.parseMultiplyDevide())

        return lhs


    def parseExpression(self):
        lhs = self.parseAdditionSubtraction()

        if self.advanceIfTokenValueIsExpected(Tokens.assign):
            return Assignment(lhs, self.parseExpression())

        return lhs


# -----------------------------------------------------------------------------------------



class Interpreter:
    def __init__(self, code):
        self.parser = Parser(code)
        self.tree = self.parser.parse()
        self.rootScope = Scope()
        self.oscReceiver = MessageReceiver(5000)
        self.oscReceiver.addHandler('/*', self.handleOSC_Message)


    def run(self):
        print('Starting TickScript Interpreter')
        self.tree.perform(self.rootScope)

    def handleOSC_Message(self, adress, message):
        print(f'handle osc, adress: {adress}, message: {message}')
        self.rootScope.invokeOpenSoundControlCallback(adress, message)

    def refreshCode(self, newCode):
        newParser = Parser(newCode)



def interpreterTest(code):
    #code = 'x = 3 + 4\n func add(a, b) { a = 3 }\n add(3,4)\n//some comments\n print(3,4,5)'

    print('lexer output:')
    testTokenIterator(code)
    print('--------------------------------------')
    i = Interpreter(code)
    i.run()
