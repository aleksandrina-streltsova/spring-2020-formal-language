import pytest

from src.cyk_hellings import grammar_contains_word, grammar_connected_vertices


def test_cyk1():  # однозначная грамматика (ПСП)
    assert (grammar_contains_word('tests/grammar1_cbs.txt', 'tests/empty_word.txt'))
    assert (grammar_contains_word('tests/grammar1_cbs.txt', 'tests/word1.txt'))
    assert (not grammar_contains_word('tests/grammar1_cbs.txt', 'tests/word2.txt'))


def test_cyk2():  # неоднозначная грамматика (ПСП)
    assert (grammar_contains_word('tests/grammar9_cbs.txt', 'tests/empty_word.txt'))
    assert (grammar_contains_word('tests/grammar9_cbs.txt', 'tests/word1.txt'))
    assert (not grammar_contains_word('tests/grammar9_cbs.txt', 'tests/word2.txt'))


def test_cyk3():  # ПСП с несколькими типами скобочных последовательностей
    assert (grammar_contains_word('tests/grammar8_cbs.txt', 'tests/empty_word.txt'))
    assert (grammar_contains_word('tests/grammar8_cbs.txt', 'tests/word1.txt'))
    assert (not grammar_contains_word('tests/grammar8_cbs.txt', 'tests/word2.txt'))
    assert (grammar_contains_word('tests/grammar8_cbs.txt', 'tests/word3.txt'))
    assert (not grammar_contains_word('tests/grammar8_cbs.txt', 'tests/word4.txt'))


def test_hellings1():  # a^n b^n
    connected_vertices = {(0, 2), (0, 3), (1, 2), (1, 3), (2, 2), (2, 3)}
    assert (grammar_connected_vertices('tests/grammar7.txt', 'tests/graph1.txt') == connected_vertices)


def test_hellings2():  # однозначная грамматика (ПСП)
    connected_vertices = {(0, 0), (1, 1), (2, 2), (3, 3), (0, 2), (0, 3), (1, 2), (1, 3), (2, 2), (2, 3)}
    assert (grammar_connected_vertices('tests/grammar1_cbs.txt', 'tests/graph1.txt') == connected_vertices)


def test_hellings3():  # неоднозначная грамматика (ПСП)
    connected_vertices = {(0, 0), (1, 1), (2, 2), (3, 3), (0, 2), (0, 3), (1, 2), (1, 3), (2, 2), (2, 3)}
    assert (grammar_connected_vertices('tests/grammar9_cbs.txt', 'tests/graph1.txt') == connected_vertices)


if __name__ == '__main__':
    pytest.main()
