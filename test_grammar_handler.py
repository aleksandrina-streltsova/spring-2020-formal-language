import pytest

from grammar_handler import Grammar, Rule


def test_parse_grammar():
    grammar = Grammar()
    grammar.parse('tests/grammar1.txt')

    assert (len(grammar.nonterm_alphabet) == 0)
    assert (grammar.term_alphabet == {'a', 'b'})
    assert (len(grammar.rules) == 2)


def test_eliminate_long_rules():
    grammar = Grammar()
    grammar.add_rule('S a b c d e f')
    grammar.eliminate_long_rules()

    assert (len(grammar.rules) == 5)

    grammar.add_rule('S A h')
    grammar.add_rule('A b c d')
    grammar.eliminate_long_rules()

    assert (len(grammar.rules) == 8)


def test_eliminate_eps_rules():
    grammar = Grammar()
    grammar.parse('tests/grammar2.txt')
    grammar.eliminate_eps_rules()

    assert (set(filter(lambda rule: rule.right == (grammar.epsilon,), grammar.rules))
            == {Rule(grammar.initial, (grammar.epsilon,))})


def test_eliminate_unit_rules():
    grammar = Grammar()
    grammar.parse('tests/grammar3.txt')
    grammar.eliminate_unit_rules()

    assert (Rule('S', ('a', 'b')) in grammar.rules)
    assert (Rule('A', ('a', 'b')) in grammar.rules)


def test_eliminate_nongenerating_nonterms():
    grammar = Grammar()
    grammar.parse('tests/grammar4.txt')
    grammar.eliminate_nongenereting_nonterms()

    assert (len(grammar.rules) == 1)
    assert (grammar.rules == {Rule('S', ('b', 'c'))})


def test_eliminate_nonaccessible_nonterms():
    grammar = Grammar()
    grammar.add_rule('S a b')
    grammar.add_rule('A c d')
    grammar.eliminate_nonaccessible_nonterms()

    assert (len(grammar.rules) == 1)
    assert (grammar.rules == {Rule('S', ('a', 'b'))})


def test_replace_terms_with_nonterms():
    grammar = Grammar()
    grammar.add_rule('S a b')
    grammar.replace_terms_with_nonterms()

    assert (len(grammar.rules) == 3)


def test_to_cnf():
    grammar1 = Grammar()
    grammar1.parse('tests/grammar5.txt')
    grammar1.to_cnf()

    grammar2 = Grammar()
    grammar2.parse('tests/grammar5.txt')

    assert (grammar1.rules == grammar2.rules)


if __name__ == '__main__':
    pytest.main()
