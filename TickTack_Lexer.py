# TickTack Lexer

from OSC_Interact import MessageReceiver, MessageSender


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
    openParenthesis     = '('
    closeParenthesis    = ')'
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
                 closeBracket, stripe, arrowLeft, arrowRight, endOfFile, newLine, openParenthesis,
                 closeParenthesis, openBraces, closeBraces, plusEquals, minusEquals, timesEquals, devideEquals,
                 moduloEquals, times, devide, modulo, plus, minus]

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

    keywords = [returnKeyword, funcKeyword, printKeyword,
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
