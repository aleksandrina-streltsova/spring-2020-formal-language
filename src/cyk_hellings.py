from src.grammar_handler import Grammar, Rule
from collections import defaultdict, deque
from src.utils import load_word, load_graph, right_parts_dict


def grammar_contains_word(grammar_file, word_file):
    grammar = Grammar()
    grammar.parse(grammar_file)
    grammar.to_cnf()
    word = load_word(word_file, grammar.epsilon)
    return cyk(grammar, word)


def grammar_connected_vertices_hellings(grammar_file, graph_file):
    grammar = Grammar()
    grammar.parse(grammar_file)
    grammar.to_wcnf()
    graph = load_graph(graph_file)
    return hellings(grammar, graph)


def cyk(grammar, word):
    if word == (grammar.epsilon,):
        if Rule(grammar.initial, (grammar.epsilon,)) in grammar.rules:
            return True
        else:
            return False

    right_parts = right_parts_dict(grammar)
    n = len(word)
    m = [[set() for _ in range(n)] for _ in range(n)]

    # инициализируем матрицу
    for i in range(n):
        m[i][i] = right_parts[(word[i],)]

    # динамика
    for l in range(1, n):  # (длина текущей подстроки) - 1
        for i in range(n - l):
            j = i + l
            for k in range(i, j):
                for B in m[i][k]:
                    for C in m[k + 1][j]:
                        m[i][j] = m[i][j].union(right_parts[(B, C)])

    if grammar.initial in m[0][n - 1]:
        return True
    return False


def hellings(grammar, graph):
    vertices, edges = graph
    right_parts = right_parts_dict(grammar)
    r_left = defaultdict(set)  # строки матрицы
    r_right = defaultdict(set)  # столбцы матрицы
    r = set()  # содержимое матрицы в виде множества троек
    m = deque()

    # инициализируем матрицу
    for v in vertices:
        for A in right_parts[(grammar.epsilon,)]:
            r_left[v].add((v, A))
            r_right[v].add((v, A))
            t = (v, v, A)
            r.add(t)
            m.append(t)
    for (v, u, t) in edges:
        for A in right_parts[(t,)]:
            r_left[v].add((u, A))
            r_right[u].add((v, A))
            t = (v, u, A)
            if t not in r:
                r.add(t)
                m.append(t)

    # алгоритм
    while len(m) > 0:
        new_triples = set()
        v, u, C = m.pop()
        for (w, B) in r_right[v]:
            for A in right_parts[(B, C)]:
                t = (w, u, A)
                if t not in r:
                    new_triples.add(t)

        for (w, B) in r_left[u]:
            for A in right_parts[(C, B)]:
                t = (v, w, A)
                if t not in r:
                    new_triples.add(t)
        for t in new_triples:
            r.add(t)
            m.append(t)
            r_left[t[0]].add((t[1], t[2]))
            r_right[t[1]].add((t[0], t[2]))
    return set(map(lambda t: (t[0], t[1]), filter(lambda t: t[2] == grammar.initial, r)))

