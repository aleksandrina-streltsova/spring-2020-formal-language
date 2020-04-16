import itertools
import networkx as nx
from scipy.sparse import lil_matrix, kron
from src.grammar_handler import Grammar
from src.utils import load_graph, load_grammar, right_parts_dict
from collections import defaultdict


def grammar_connected_vertices_matrix(grammar_file, graph_file):
    grammar = Grammar()
    grammar.parse(grammar_file)
    grammar.to_wcnf()
    graph = load_graph(graph_file)
    return cfpq_matrix(grammar, graph)


def grammar_connected_vertices_tensor_product(grammar_file, graph_file):
    initial, grammar = load_grammar(grammar_file)
    graph = load_graph(graph_file)
    return cfpq_tensor_product(initial, grammar, graph)


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
    rules = set()  # отберем правила длины 2
    for rule in grammar.rules:
        if len(rule.right) == 2:
            rules.add(rule)

    is_changing = True
    while is_changing:
        is_changing = False
        for rule in rules:
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


def cfpq_tensor_product(initial, grammar, graph):
    # инициализируем матрицу грамматики
    S = defaultdict(set)
    F = defaultdict(set)
    N = set()  # множество нетерминалов порождающих пустую строку
    grammar_edges = set()
    n = 0
    for nonterm, fsm in grammar.items():
        S[fsm.initial + n].add(nonterm)
        for final in fsm.finals:
            F[final + n].add(nonterm)
        if fsm.initial in fsm.finals:
            N.add(nonterm)
        for u, d in fsm.map.items():
            for l, v in d.items():
                grammar_edges.add((u + n, v + n, l))
        n += len(fsm.states)
    constant_factory_n = lambda: next(itertools.repeat(lil_matrix((n, n))))
    grammar_matrices = defaultdict(constant_factory_n)
    for (u, v, l) in grammar_edges:
        grammar_matrices[l][u, v] = 1

    # инициализируем матрицу графа
    vertices, graph_edges = graph
    m = len(vertices)
    constant_factory_m = lambda: next(itertools.repeat(lil_matrix((m, m))))
    graph_matrices = defaultdict(constant_factory_m)
    for (u, v, l) in graph_edges:
        graph_matrices[l][u, v] = 1
    for nonterm in N:
        graph_matrices[nonterm].setdiag(1)

    # алгоритм
    k = n * m
    is_changing = True
    while is_changing:
        is_changing = False
        matrix = lil_matrix((k, k))
        labels = set(graph_matrices.keys()).intersection(grammar_matrices.keys())
        for l in labels:
            matrix = matrix + kron(grammar_matrices[l], graph_matrices[l])
        matrix = transitive_closure2(matrix, k)
        rows, columns = matrix.nonzero()
        for pair in zip(rows, columns):
            ni, nj, mi, mj = get_coordinates(pair, m)
            for nonterm in S[ni].intersection(F[nj]):
                if graph_matrices[nonterm][mi, mj] == 0:
                    is_changing = True
                graph_matrices[nonterm][mi, mj] = 1
    rows, columns = graph_matrices[initial].nonzero()
    return set(zip(rows, columns))


def constant_factory(n):
    return next(itertools.repeat(lil_matrix(n, n)))


def transitive_closure1(matrix, k):
    G = nx.DiGraph(matrix)
    paths = nx.all_pairs_shortest_path_length(G)
    matrix = lil_matrix((k, k))
    for u, d in dict(paths).items():
        for v, length in d.items():
            if length > 0:
                matrix[u, v] = 1
    return matrix


def transitive_closure2(matrix, k):
    pow = 1
    while pow < k:
        before = matrix.count_nonzero()
        matrix = matrix + matrix ** 2
        after = matrix.count_nonzero()
        if before == after:
            break
        pow *= 2
    return matrix


def get_coordinates(pair, m):
    i, j = pair
    ni = i // m
    mi = i % m
    nj = j // m
    mj = j % m
    return ni, nj, mi, mj
