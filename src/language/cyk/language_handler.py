from src.cyk_hellings import cyk
from src.grammar_handler import Grammar

epsilon = 'EPS'


def parse_language():
    language = Grammar()
    language.capitalized_normally = False
    language.epsilon = epsilon
    language.parse('src/language/cyk/grammar.txt')
    language.to_cnf()
    return language


def load_program(program_file):
    with open(program_file) as file:
        tokens = []
        for line in file.readlines():
            tokens += line.split()
        program = tuple(filter(lambda symbol: symbol != epsilon, tokens))
        if len(program) == 0:
            return epsilon,
        return program


def valid_program(language, program):
    return cyk(language, program)
