import pytest

from src.grammar_handler import Grammar, Rule


def test_parse_grammar():
    grammar = Grammar()
    grammar.parse('tests/grammar1.txt')

    assert (len(grammar.nonterm_alphabet) == 2)
    assert (grammar.term_alphabet == {'a', 'b'})
    assert (len(grammar.rules) == 3)


def test_eliminate_long_rules():
    grammar = Grammar()
    grammar.parse('tests/grammar6.txt')
    grammar.eliminate_long_rules()

    assert (len(grammar.rules) == 8)


def test_eliminate_eps_rules():
    grammar = Grammar()
    grammar.parse('tests/grammar2.txt')
    grammar.eliminate_eps_rules()

    assert (set(filter(lambda rule: rule.right == (grammar.epsilon,), grammar.rules))
            == {Rule(grammar.initial, (grammar.epsilon,))})
    assert (len(grammar.rules) == 15)


def test_eliminate_unit_rules():
    grammar = Grammar()
    grammar.parse('tests/grammar3.txt')
    grammar.eliminate_unit_rules()

    assert (Rule('S', ('a', 'b')) in grammar.rules)
    assert (Rule('A', ('a', 'b')) in grammar.rules)
    assert (len(grammar.rules) == 4)


def test_eliminate_nongenerating_nonterms():
    grammar = Grammar()
    grammar.parse('tests/grammar4.txt')
    grammar.eliminate_nongenereting_nonterms()

    assert (len(grammar.rules) == 1)
    assert (grammar.rules == {Rule('S', ('b', 'c'))})


def test_eliminate_nonaccessible_nonterms():
    grammar = Grammar()
    grammar.parse('tests/grammar1.txt')
    grammar.eliminate_nonaccessible_nonterms()

    assert (len(grammar.rules) == 2)
    assert (grammar.rules == {Rule(grammar.initial, (grammar.epsilon,)), Rule('S', ('a', 'S', 'b', 'S'))})


def test_replace_terms_with_nonterms():
    grammar = Grammar()
    grammar.parse('tests/grammar4.txt')
    grammar.replace_terms_with_nonterms()

    assert (len(grammar.rules) == 6)
    for rule in grammar.rules:
        contains_term = len(set(filter(lambda term: term in grammar.term_alphabet, rule.right))) > 0
        assert(not contains_term or (contains_term and len(rule.right) == 1))


def test_to_cnf1():
    grammar1 = Grammar()
    grammar1.parse('tests/grammar5.txt')
    grammar1.to_cnf()

    grammar2 = Grammar()
    grammar2.parse('tests/grammar5.txt')

    assert (len(grammar1.rules) == len(grammar2.rules))
    assert (grammar1.rules == grammar2.rules)


def test_to_cnf2():
    grammar = Grammar()
    grammar.parse('tests/grammar1.txt')
    grammar.to_cnf()

    assert (Rule(grammar.initial, (grammar.epsilon,)) in grammar.rules)
    for rule in grammar.rules:
        is_first_type = rule == Rule(grammar.initial, (grammar.epsilon,))
        is_second_type = len(rule.right) == 1 and rule.right[0] in grammar.term_alphabet
        is_third_type = len(rule.right) == 2 and rule.right[0] in grammar.nonterm_alphabet and\
            rule.right[1] in grammar.nonterm_alphabet
        assert (is_first_type or is_second_type or is_third_type)
    assert(len(grammar.rules) == 10)


if __name__ == '__main__':
    pytest.main()
