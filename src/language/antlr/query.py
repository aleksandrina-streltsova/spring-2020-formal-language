from antlr4 import *
from antlr4.error.ErrorListener import ErrorListener
from src.language.antlr.queryLexer import queryLexer
from src.language.antlr.queryParser import queryParser


class QueryTreeWalker:
    def __init__(self, node):
        self.nodes = []
        self.edges = []
        self.size = 0
        self.walk(node)

    def walk(self, node):
        current_index = self.size
        self.size += 1
        if isinstance(node, TerminalNode):
            label = node.getText()
        else:
            child_indices = []
            for child in node.getChildren():
                child_index = self.walk(child)
                child_indices.append(child_index)
            self.edges.append((current_index, child_indices))
            label = queryParser.ruleNames[node.getRuleIndex()]
        self.nodes.append((current_index, label))
        return current_index


class QueryParseError(Exception):
    pass


class QueryErrorListener(ErrorListener):
    def __init__(self):
        super(QueryErrorListener, self).__init__()

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        raise QueryParseError()

    def reportAmbiguity(self, recognizer, dfa, startIndex, stopIndex, exact, ambigAlts, configs):
        raise QueryParseError()

    def reportAttemptingFullContext(self, recognizer, dfa, startIndex, stopIndex, conflictingAlts, configs):
        raise QueryParseError()

    def reportContextSensitivity(self, recognizer, dfa, startIndex, stopIndex, prediction, configs):
        raise QueryParseError()


def parse_script(stream):
    lexer = queryLexer(stream)
    token_stream = CommonTokenStream(lexer)
    parser = queryParser(token_stream)
    parser.addErrorListener(QueryErrorListener())
    try:
        return parser.script()
    except QueryParseError:
        return None


def script_is_correct(stream):
    tree = parse_script(stream)
    return tree is not None


def print_script_tree(stream, outputfile):
    tree = parse_script(stream)
    if tree is None:
        print("couldn't parse the script")
        return
    outputfile.write('digraph {\n')
    walker = QueryTreeWalker(tree)
    for index, label in walker.nodes:
        outputfile.write('\t' + str(index) + ' [label=' + label + '];\n')
    for index, child_indices in walker.edges:
        for child_index in child_indices:
            outputfile.write('\t' + str(index) + ' -> ' + str(child_index) + ';\n')
    outputfile.write('}')
