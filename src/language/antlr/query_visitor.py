from src.cyk_hellings import hellings
from src.grammar_handler import Grammar, Rule
from src.language.antlr.queryParser import queryParser
from src.language.antlr.queryVisitor import queryVisitor
from src.utils import load_graph


class queryVisitorImpl(queryVisitor):
    def __init__(self):
        self.graphs = {}
        self.grammar = Grammar()
        self.last_generated_nonterm = '_A'

    def visitScript(self, ctx: queryParser.ScriptContext):
        result = ''
        for child in ctx.children:
            child_result = self.visit(child)
            if child_result is not None:
                result += child_result
        return result

    def visitStmt(self, ctx: queryParser.StmtContext):
        result = ''
        if ctx.KW_LIST() is not None:
            for graph in self.graphs:
                result += graph + '\n'
            return result
        if ctx.KW_CONNECT() is not None:
            graph_file = ctx.STRING().getText()[1:-1]
            self.graphs[graph_file] = load_graph(graph_file)
            return None
        if ctx.OP_EQ() is not None:
            left = ctx.NT_NAME().getText()
            if len(self.grammar.rules) == 0:
                self.grammar.initial = left
            self.__add_rules_from_pattern(self.grammar, left, ctx.pattern())
            return None
        return self.visit(ctx.select_stmt())

    def visitPattern(self, ctx: queryParser.PatternContext):
        result = self.visit(ctx.alt_elem())
        if ctx.OP_OR() is not None:
            result += self.visit(ctx.pattern())
        return result

    def visitAlt_elem(self, ctx: queryParser.Alt_elemContext):
        if ctx.KW_EPS() is not None:
            return [(self.grammar.epsilon,)]
        return [self.visit(ctx.seq())]

    def visitSeq(self, ctx: queryParser.SeqContext):
        result = []
        for child in ctx.children:
            result.append(self.visit(child))
        return tuple(result)

    def visitSeq_elem(self, ctx: queryParser.Seq_elemContext):
        prim_pattern = self.visit(ctx.prim_pattern())
        if len(ctx.children) == 1:
            return prim_pattern
        nonterm = self.__generate_nonterm()
        if ctx.OP_PLUS() is not None:
            self.grammar.rules.add(Rule(nonterm, (prim_pattern, nonterm)))
            self.grammar.rules.add(Rule(nonterm, (prim_pattern,)))
        if ctx.OP_STAR() is not None:
            self.grammar.rules.add(Rule(nonterm, (prim_pattern, nonterm)))
            self.grammar.rules.add(Rule(nonterm, (self.grammar.epsilon,)))
        if ctx.OP_QUEST() is not None:
            self.grammar.rules.add(Rule(nonterm, (prim_pattern,)))
            self.grammar.rules.add(Rule(nonterm, (self.grammar.epsilon,)))
        return nonterm

    def visitPrim_pattern(self, ctx: queryParser.Prim_patternContext):
        if ctx.pattern() is not None:
            left = self.__generate_nonterm()
            self.__add_rules_from_pattern(self.grammar, left, ctx.pattern())
            return left
        return ctx.getChild(0).getText()

    def visitSelect_stmt(self, ctx: queryParser.Select_stmtContext):
        graph_file = ctx.STRING().getText()[1:-1]
        if graph_file in self.graphs:
            graph = self.graphs[graph_file]
            pattern = self.visit(ctx.where_expr())
            grammar = Grammar()
            nonterm = self.__generate_nonterm()
            grammar.initial = nonterm
            grammar.rules = self.grammar.rules
            self.__add_rules_from_pattern(grammar, nonterm, pattern)
            grammar.update_alphabets()
            grammar.to_wcnf()
            connected_vertices = hellings(grammar, graph)
            return str(len(connected_vertices) > 0) + '\n'
        return 'graph isn\'t loaded\n'

    def visitWhere_expr(self, ctx: queryParser.Where_exprContext):
        return ctx.pattern()

    def __generate_nonterm(self):
        nonterm = self.last_generated_nonterm
        if nonterm[-1] == 'Z':
            nonterm += 'A'
        else:
            nonterm = nonterm[:-1] + chr(ord(nonterm[-1]) + 1)
        self.last_generated_nonterm = nonterm
        return nonterm

    def __add_rules_from_pattern(self, grammar, left, pattern):
        right_parts = self.visit(pattern)
        for right in right_parts:
            grammar.rules.add(Rule(left, right))
