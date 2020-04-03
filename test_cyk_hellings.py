import pytest

from src.cyk_hellings import grammar_contains_word


def test_cyk():
    assert (grammar_contains_word('tests/grammar1.txt', 'tests/word1.txt'))
    assert (not grammar_contains_word('tests/grammar1.txt', 'tests/word2.txt'))


def main():
    grammar_contains_word('tests/grammar1.txt', 'tests/word1.txt')


if __name__ == '__main__':
    pytest.main()