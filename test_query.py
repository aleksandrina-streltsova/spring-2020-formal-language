import pytest
from antlr4 import InputStream

from src.grammar_handler import Rule
from src.language.antlr.query import script_is_correct, run_script, parse_script
from src.language.antlr.query_visitor import queryVisitorImpl


def valid_script(script_file):
    with open(script_file) as file:
        stream = InputStream(file.read())
        return script_is_correct(stream)


def result_matches_script(script_file, result_file):
    with open(script_file) as sf:
        stream = InputStream(sf.read())
        result = run_script(stream)
        with open(result_file) as rf:
            return result, rf.read()


def grammar_from_script(script_file):
    with open(script_file) as sf:
        tree = parse_script(InputStream(sf.read()))
        visitor = queryVisitorImpl()
        visitor.visit(tree)
        return visitor.grammar


def test_query():
    assert (valid_script('tests/script0_empty.txt'))
    assert (valid_script('tests/script1.txt'))
    assert (valid_script('tests/script2.txt'))
    assert (valid_script('tests/script3.txt'))
    assert (not valid_script('tests/script4_invalid.txt'))
    assert (not valid_script('tests/script5_invalid.txt'))
    assert (valid_script('tests/script6.txt'))


def test_run_script():
    actual1, expected1 = result_matches_script('tests/scripts/script1', 'tests/scripts/result1')
    assert (actual1 == expected1)  # connect, list
    actual2, expected2 = result_matches_script('tests/scripts/script2', 'tests/scripts/result2')
    assert (actual2 == expected2)  # select: exists

def test_query_visitor_grammar():
    grammar1 = grammar_from_script('tests/scripts/grammar1')  # pattern, alt_elem
    grammar2 = grammar_from_script('tests/scripts/grammar2')  # seq_elem
    grammar3 = grammar_from_script('tests/scripts/grammar3')  # prim_pattern
    assert (grammar1.rules == {Rule('S', ('a', 'b')), Rule('S', ('c', 'd')), Rule('S', ('e',)), Rule('S', ('eps',))})
    assert (grammar2.rules == {Rule('B', ('_B',)), Rule('_B', ('b', '_B')), Rule('_B', ('eps',)),
                               Rule('C', ('_C',)), Rule('_C', ('eps',)), Rule('_C', ('c',)),
                               Rule('D', ('_D',)), Rule('_D', ('d', '_D')), Rule('_D', ('d',))})
    assert (grammar3.rules == {Rule('S', ('a',)), Rule('S', ('B',)), Rule('B', ('b',)),
                               Rule('S', ('_B',)), Rule('_B', ('c',)), Rule('_B', ('d',))})


if __name__ == '__main__':
    pytest.main()
