from collections import defaultdict

from src import fsm_handler


def load_word(word_file, epsilon):
    with open(word_file) as file:
        word = tuple(filter(lambda symbol: symbol != epsilon, file.readline().split()))
        if len(word) == 0:
            return epsilon,
        return word


def load_graph(graph_file):
    edges = set()
    vertices = set()
    with open(graph_file) as file:
        for line in file.readlines():
            edge = line.split()
            edges.add((int(edge[0]), int(edge[2]), edge[1]))
            vertices.add(int(edge[0]))
            vertices.add(int(edge[2]))
    return vertices, edges


def right_parts_dict(grammar):
    right_parts = defaultdict(set)
    for rule in grammar.rules:
        right_parts[rule.right].add(rule.left)
    return right_parts


# грамматика с расширенным представлением правой части
def load_grammar(grammar_file):
    grammar = {}
    initial = ''
    with open(grammar_file) as file:
        for line in file.readlines():
            nonterm = line[0]
            if initial == '':
                initial = nonterm
            regex = line[2:].replace('eps', '').replace(' ', '')
            grammar[nonterm] = fsm_handler.regex_to_dfsm(regex)
    return initial, grammar
