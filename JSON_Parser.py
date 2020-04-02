# TickTack to JSON Parser


from TickScript import Tokens, TokenIterator
import json

class Parser(TokenIterator):
    def __init__(self, code):
        super(Parser, self).__init__(code)


    def consumeType(self, type, errorMessage):
        if self.currentTokenType != type:
            self.throwLocationError(errorMessage)
        self.advance()


    def consumeValue(self, value, errorMessage):
        if self.currentTokenValue != value:
            self.throwLocationError(errorMessage)
        self.advance()


    def parse(self):
        tree = { 'language': 'TickTack', 'version': '0.1b' }
        self.advance()
        tree['root'] = self.parseStatementList()
        return tree


    def parseBlockStatement(self):
        while self.currentTokenValue != Tokens.openBraces and self.currentTokenValue != Tokens.endOfFile:
            self.advance()

        self.consumeValue(Tokens.openBraces, 'Expected "{" to start block statement')
        block = self.parseStatementList()
        self.consumeValue(Tokens.closeBraces, 'Expected "}" to close off block statement')
        return block


    def parseStatementList(self):
        block = { "block_statement": [] }

        if self.currentTokenValue != Tokens.closeBraces:
            block["block_statement"].append(self.parseStatement())

        while self.currentTokenValue != Tokens.closeBraces and self.currentTokenValue != Tokens.endOfFile:
            #self.consumeValue(Tokens.newLine, f'Expected newline before statement, current token: {self.currentTokenValue}')

            while self.currentTokenValue == Tokens.newLine:
                self.advance()

            if self.currentTokenValue != Tokens.endOfFile and self.currentTokenValue != Tokens.closeBraces:
                block["block_statement"].append(self.parseStatement())

        return block


    def parseStatement(self):
        while self.currentTokenValue == Tokens.newLine:
            self.advance()

        if self.advanceIfTokenValueIsExpected(Tokens.outletKeyword):
            return self.parseOutletDeclaration()

        if self.currentTokenType == Tokens.identifierType or self.currentTokenType == Tokens.numericLiteralType:
            return { 'expression_statement': self.parseExpression() }

        if self.advanceIfTokenValueIsExpected(Tokens.varKeyword):
            return { 'variable_declaration': self.parseVariableDeclaration(constant=False) }

        if self.advanceIfTokenValueIsExpected(Tokens.letKeyword):
            return { 'variable_declaration': self.parseVariableDeclaration(constant=True) }

        if self.advanceIfTokenValueIsExpected(Tokens.returnKeyword):
            return { 'return_statement': { 'expression': self.parseExpression() }}

        if self.advanceIfTokenValueIsExpected(Tokens.funcKeyword):
            return { 'function_definition': self.parseFunctionDefinition() }

        if self.advanceIfTokenValueIsExpected(Tokens.ifKeyword):
            return { 'if_statement': self.parseIfStatement() }

        if self.currentTokenValue == Tokens.openBraces:
            return self.parseBlockStatement()

        if self.advanceIfTokenValueIsExpected(Tokens.printKeyword):
            return self.parsePrintStatement()

        if self.currentTokenType == Tokens.stringLiteralType:
            return { 'osc_callback_definition': self.parseCallbackDefinition() }

        if self.advanceIfTokenValueIsExpected(Tokens.openBracket):
            return self.parseTickStatement()

        return { 'empty_statement': None }


    def parsePrintStatement(self):
        self.consumeValue(Tokens.openParentheses, 'Expected "(" after "print"')
        expr = self.parseExpression()
        self.consumeValue(Tokens.closeParentheses, 'Expected ")" to close off print statement')
        return {'print_statement': expr}


    def parseCallbackDefinition(self):
        address = self.currentTokenValue
        self.advance()
        self.consumeValue(Tokens.arrowRight, 'Expected "->" after address in OSC callback')
        self.consumeValue(Tokens.openParentheses, 'Expected "(" after "->" in OSC callback')
        argumentList = []

        if self.currentTokenValue != Tokens.closeParentheses:
            argumentList.append(self.currentTokenValue)
            self.consumeType(Tokens.identifierType, 'Expected identifier in argument list')

        while self.currentTokenValue != Tokens.closeParentheses and self.currentTokenValue != Tokens.endOfFile:
            self.consumeValue(Tokens.comma, 'Expected "," in argument list')
            argumentList.append(self.currentTokenValue)
            self.consumeType(Tokens.identifierType, 'Expected identifier in argument list')

        block = self.parseBlockStatement()
        return { 'address': address, 'argumentList': argumentList, 'body': block }


    def parseTickStatement(self):
        data = []
        while self.currentTokenValue == Tokens.stripe or self.currentTokenValue == Tokens.dot:
            data.append(1 if self.currentTokenValue == Tokens.stripe else 0)
            self.advance()

        self.consumeValue(Tokens.closeBracket, 'Expected "]" to close tick statement')

        stmt = self.parseStatement()
        conds = []
        num = len(data)
        modOp = {'binary_operation': {'type': '%',
                                      'left_operant':  {'unqualified_name': '__tick__'},
                                      'right_operant': {'numeric_literal': num}}}

        for i, d in enumerate(data):
            if d == 1:
                c = { 'equality_operation': {
                         'type': '==', 'left_operant': modOp, 'right_operant': {'numeric_literal': i }}}
                conds.append(c)

        condition = conds[0]

        for i in range(len(conds) - 1):
            condition = {'logical_operation': {'type': '||', 'left_operant': condition, 'right_operant': conds[i+1]}}

        return { 'if_statement': { 'condition': condition, 'if_block': stmt, 'else_block': None }}


    def parseOutletDeclaration(self):
        identifier = self.currentTokenValue
        self.consumeType(Tokens.identifierType, 'Expected identifier after "outlet"')
        self.consumeValue(Tokens.arrowRight, 'Expected "->" after identifier in outlet declaration')
        address = self.currentTokenValue
        self.consumeType(Tokens.stringLiteralType, 'Expected address after "->" in outlet declaration')
        return { 'outlet_declaration': { 'identifier': identifier, 'address': address }}


    def parseIfStatement(self):
        self.consumeValue(Tokens.openParentheses, 'Expected "(" after "if"')
        condition = self.parseExpression()
        self.consumeValue(Tokens.closeParentheses, 'Expected ")" after expression in if statement')
        ifBlock = self.parseStatement()

        while self.currentTokenValue == Tokens.newLine:
            self.advance()

        elseBlock = None
        if self.advanceIfTokenValueIsExpected(Tokens.elseKeyword):
            elseBlock = self.parseStatement()

        return { 'condition': condition, 'if_block': ifBlock, 'else_block': elseBlock }


    def parseFunctionDefinition(self):
        identifier = self.currentTokenValue
        self.consumeType(Tokens.identifierType, 'Expected identifier after "func"')
        self.consumeValue(Tokens.openParentheses, 'Expected "(" after identifier in function declaration')

        if self.currentTokenType == Tokens.identifierType:
            arguments = [self.currentTokenValue]
            self.advance()
        else:
            arguments = []

        while self.currentTokenValue != Tokens.closeParentheses and self.currentTokenValue != Tokens.endOfFile:
            self.consumeValue(Tokens.comma, 'Expected "," between function arguments')
            arguments.append(self.currentTokenValue)
            self.consumeType(Tokens.identifierType, 'Expected identifier in function arguments')

        self.consumeValue(Tokens.closeParentheses, 'Expected ")" to close off function arguments')
        block = self.parseBlockStatement()

        return { 'identifier': identifier, 'arguments': arguments, 'body': block }


    def parseFunctionCall(self, identifier):
        args = [self.parseExpression()] if self.currentTokenValue != Tokens.closeParentheses else []

        while self.currentTokenValue != Tokens.closeParentheses:
             self.consumeValue(Tokens.comma, 'Expected "," between function arguments')
             args.append(self.parseExpression())

        self.advance()
        return { 'function_call': { 'identifier': identifier, 'arguments': args }}


    def parseVariableDeclaration(self, constant):
        if self.currentTokenType != Tokens.identifierType:
            self.throwLocationError('Expected identifier for variable declaration')

        identifier = self.currentTokenValue
        self.consumeType(Tokens.identifierType,
            f'Expected identifier after "{Tokens.letKeyword if constant else Tokens.varKeyword}"')
        self.consumeValue(Tokens.assign, 'Expected "=" for variable declaration')

        expr = self.parseExpression()

        if expr == None:
            self.throwLocationError('Expected expression after "=" in variable declaration')

        return { 'identifier': identifier, 'constant': constant, 'expression': expr }


    def parseSuffix(self, identifier):
        if self.advanceIfTokenValueIsExpected(Tokens.openParentheses):
            return self.parseFunctionCall(identifier)

        if self.advanceIfTokenValueIsExpected(Tokens.dot):
            return self.parseControllerFunctionCall(identifier)

        return { 'unqualified_name': identifier }


    def parseFactor(self):
        token = self.currentTokenValue

        if self.advanceIfTokenTypeIsExpected(Tokens.identifierType):
            return self.parseSuffix(token)

        if self.advanceIfTokenTypeIsExpected(Tokens.numericLiteralType):
            return { 'numeric_literal': float(token) }

        if token == Tokens.trueKeyword or token == Tokens.falseKeyword:
            self.advance()
            return { 'boolean_literal': (token == Tokens.trueKeyword) }

        if self.advanceIfTokenValueIsExpected(Tokens.openParentheses):
            exp = self.parseExpression()
            self.advanceIfTokenValueIsExpected(Tokens.closeParentheses)
            return exp


    def parseUnary(self):
        if self.advanceIfTokenValueIsExpected(Tokens.minus):
            return { 'unary_operation': { 'type': Tokens.minus, 'right_operant': self.parseUnary() }}

        if self.advanceIfTokenValueIsExpected(Tokens.plus):
            return self.parseUnary()

        return self.parseFactor()


    def parseMultiplyDevide(self):
        lhs = self.parseUnary()

        while True:
            t = self.currentTokenValue
            if t == Tokens.times or t == Tokens.devide or t == Tokens.modulo:
                self.advance()
                rhs = self.parseUnary()
                lhs = { 'binary_operation': { 'type': t, 'left_operant': lhs, 'right_operant': rhs }}
            else:
                break

        return lhs


    def parseAdditionSubtraction(self):
        lhs = self.parseMultiplyDevide()

        while True:
            t = self.currentTokenValue
            if t == Tokens.plus or t == Tokens.minus:
                rhs = self.parseMultiplyDevide()
                lhs = { 'binary_operation': { 'type': t, 'left_operant': lhs, 'right_operant': rhs }}
            else:
                break

        return lhs


    def parseComparisonOperation(self):
        lhs = self.parseAdditionSubtraction()

        while True:
            t = self.currentTokenValue
            if self.matchAnyOfTokenValues([Tokens.greaterThan, Tokens.lessThan,
                                           Tokens.greaterThanEquals, Tokens.lessThanEquals]):
                self.advance()
                rhs = self.parseAdditionSubtraction()
                lhs = { 'comparison_operation': { 'type': t, 'left_operant': lhs, 'right_operant': rhs }}
            else:
                break

        return lhs


    def parseEqualityOperation(self):
        lhs = self.parseComparisonOperation()

        while True:
            t = self.currentTokenValue
            if t == Tokens.equals or t == Tokens.notEquals:
                self.advance()
                rhs = self.parseComparisonOperation()
                lhs = { 'equality_operation': { 'type': t, 'left_operant': lhs, 'right_operant': rhs }}
            else:
                break

        return lhs


    def parseLogicalOperation(self):
        lhs = self.parseEqualityOperation()

        while True:
            t = self.currentTokenValue
            if t == Tokens.logicalAnd or t == Tokens.logicalOr:
                self.advance()
                rhs = self.parseEqualityOperation()
                lhs = { 'logical_operation': { 'type': t, 'left_operant': lhs, 'right_operant': rhs }}
            else:
                break

        return lhs


    def parseExpression(self):
        lhs = self.parseLogicalOperation()

        if self.advanceIfTokenValueIsExpected(Tokens.assign):
            return {'assignment': {'left_operant': lhs, 'right_operant': self.parseExpression()}}

        if self.matchAnyOfTokenValues([Tokens.plusEquals, Tokens.minusEquals,
            Tokens.timesEquals, Tokens.devideEquals, Tokens.moduloEquals]):
            type = self.currentTokenValue
            self.advance()
            return {'self_assignment': {'type': type, 'left_operant': lhs, 'right_operant': self.parseExpression()}}

        return lhs



#==================================================================================


def parserTest():
    code = '''  if (x == 3) x = 4 else if (x == 4) x = 3 \n
                outlet kick -> \'kick\' \n
                let x = 3 \n
                func foo (x, y) { return x + y }\n
                x += 1 \n
                [..|.|] if (x == 3) kick(x)

                '/left'->(dt) {
                    [..|] kick()
                }
           '''

    p = Parser(code)

    try:
        tree = p.parse()

        with open('tick_tack_syntax.tack', 'w') as file:
            file.write(json.dumps(tree, indent=2))

    except Exception as error:
        print(error)
        print('Parsing Failed')

parserTest()
