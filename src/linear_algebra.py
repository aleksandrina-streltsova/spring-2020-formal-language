from src.grammar_handler import Grammar
from src.utils import load_graph, right_parts_dict
from scipy.sparse import lil_matrix


def grammar_connected_vertices_matrix(grammar_file, graph_file):
    grammar = Grammar()
    grammar.parse(grammar_file)
    grammar.to_wcnf()
    graph = load_graph(graph_file)
    return cfpq_matrix(grammar, graph)


def cfpq_matrix(grammar, graph):
    vertices, edges = graph
    right_parts = right_parts_dict(grammar)
    matrices = {}
    n = len(vertices)

    # создаем матрицы
    for nonterm in grammar.nonterm_alphabet:
        matrices[nonterm] = lil_matrix((n, n))

    # инициализируем матрицы
    for (u, v, t) in edges:
        for A in right_parts[(t,)]:
            matrices[A][u, v] = 1
    for A in right_parts[(grammar.epsilon,)]:
        matrices[A].setdiag(1)

    # алгоритм
    is_changing = True
    while is_changing:
        is_changing = False
        for rule in grammar.rules:
            if len(rule.right) == 2:
                A = rule.left
                (B, C) = rule.right
                before = matrices[A].count_nonzero()
                product = matrices[B] * matrices[C]
                matrices[A] = matrices[A] + product
                after = matrices[A].count_nonzero()
                if before < after:
                    is_changing = True
    rows, columns = matrices[grammar.initial].nonzero()
    return set(zip(rows, columns))

