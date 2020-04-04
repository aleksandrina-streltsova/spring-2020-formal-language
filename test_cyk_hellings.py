import pytest

from src.cyk_hellings import grammar_contains_word, grammar_connected_vertices


def test_cyk():
    assert (grammar_contains_word('tests/grammar1.txt', 'tests/word1.txt'))
    assert (not grammar_contains_word('tests/grammar1.txt', 'tests/word2.txt'))


def test_hellings():
    assert (grammar_connected_vertices('tests/grammar7.txt', 'tests/graph1.txt') == {(1, 3), (0, 2), (2, 3), (1, 2),
                                                                                     (0, 3), (2, 2)})


if __name__ == '__main__':
    pytest.main()
