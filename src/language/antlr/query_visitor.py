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
        self.__count = 'count'
        self.__exists = 'exists'
        self.__underscore = '_'

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
            connected_vertices = self.__connected_vertices_restricted_by_pattern(self.graphs[graph_file],
                                                                                 ctx.where_expr().pattern())
            return self.__select(list(connected_vertices), ctx.obj_expr(), ctx.where_expr())
        return 'graph isn\'t loaded\n'

    def visitObj_expr(self, ctx: queryParser.Obj_exprContext):
        vs_info = self.visit(ctx.vs_info())
        if ctx.KW_COUNT():
            return vs_info, self.__count
        if ctx.KW_EXISTS():
            return vs_info, self.__exists
        return (vs_info,)

    def visitVs_info(self, ctx: queryParser.Vs_infoContext):
        if ctx.COMMA() is not None:
            return ctx.getChild(1).getText(), ctx.getChild(3).getText()
        return ctx.getChild(0).getText()

    def visitWhere_expr(self, ctx: queryParser.Where_exprContext):
        return self.visit(ctx.getChild(1)), self.visit(ctx.getChild(6))

    def visitV_expr(self, ctx: queryParser.V_exprContext):
        if ctx.DOT() is not None:
            return ctx.IDENT().getText(), ctx.INT().getText()
        if ctx.UNDERSCORE() is not None:
            return self.__underscore
        return ctx.IDENT().getText()

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

    def __connected_vertices_restricted_by_pattern(self, graph, pattern):
        grammar = Grammar()
        nonterm = self.__generate_nonterm()
        grammar.initial = nonterm
        grammar.rules = self.grammar.rules
        self.__add_rules_from_pattern(grammar, nonterm, pattern)
        grammar.update_alphabets()
        grammar.to_wcnf()
        return hellings(grammar, graph)

    def __select(self, connected_vertices, obj_expr_ctx: queryParser.Obj_exprContext,
                 where_expr_ctx: queryParser.Where_exprContext):
        obj_expr = self.visit(obj_expr_ctx)
        vs_info = obj_expr[0]
        v1, v2 = self.visit(where_expr_ctx)
        if len(v1) == 2 and v1[1].isdigit():
            connected_vertices = list(filter(lambda p: p[0] == int(v1[1]), connected_vertices))
            v1 = v1[0]
        if len(v2) == 2 and v2[1].isdigit():
            connected_vertices = list(filter(lambda p: p[1] == int(v2[1]), connected_vertices))
            v2 = v2[0]
        if len(vs_info) == 2:
            if vs_info[0] == vs_info[1]:
                return 'expected variables with different names\n'
            acceptable_vs = {vs_info[0], vs_info[1], self.__underscore}
            if v1 not in acceptable_vs:
                return 'unexpected variable name: \'' + v1 + '\'\n'
            if v2 not in acceptable_vs:
                return 'unexpected variable name: \'' + v2 + '\'\n'
            if (v1 == vs_info[0] or v1 == self.__underscore) and (
                    v2 == vs_info[1] or v2 == self.__underscore):
                result = connected_vertices
            else:
                result = list(map(lambda p: (p[1], p[0]), connected_vertices))
        else:
            if vs_info[0] == v1 and vs_info[0] == v2:
                result = list(set(map(lambda p: p[0], filter(lambda p: p[0] == p[1], connected_vertices))))
            elif vs_info[0] == v1:
                result = list(set(map(lambda p: p[0], connected_vertices)))
            elif vs_info[0] == v2:
                result = list(set(map(lambda p: p[1], connected_vertices)))
            else:
                return 'expected \'' + str(vs_info[0]) + '\' in where expression\n'
        result.sort()
        if len(obj_expr) == 1:
            return '[' + ', '.join(map(str, result)) + ']\n'
        if obj_expr[1] == self.__exists:
            return str(len(result) > 0) + '\n'
        return str(len(result)) + '\n'
