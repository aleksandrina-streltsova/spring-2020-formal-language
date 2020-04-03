from src.grammar_handler import Grammar, Rule
from collections import defaultdict


def grammar_contains_word(grammar_file, word_file):
    grammar = Grammar()
    grammar.parse(grammar_file)
    grammar.to_cnf()
    word = load_word(word_file, grammar.epsilon)
    return cyk(grammar, word)


def load_word(word_file, epsilon):
    with open(word_file) as file:
        word = tuple(filter(lambda symbol: symbol != epsilon, file.readline().split()))
        if len(word) == 0:
            return epsilon,
        return word


def cyk(grammar, word):
    if word == (grammar.epsilon,):
        if Rule(grammar.initial, (grammar.epsilon,)) in grammar.rules:
            return True
        else:
            return False

    right_parts = defaultdict(set)
    for rule in grammar.rules:
        right_parts[rule.right].add(rule.left)
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
