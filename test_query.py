import pytest
from antlr4 import InputStream
from src.language.antlr.query import script_is_correct


def valid_script(script_file):
    with open(script_file) as file:
        stream = InputStream(file.read())
        return script_is_correct(stream)


def test_query():
    assert (valid_script('tests/script0_empty.txt'))
    assert (valid_script('tests/script1.txt'))
    assert (valid_script('tests/script2.txt'))
    assert (valid_script('tests/script3.txt'))
    assert (not valid_script('tests/script4_invalid.txt'))
    assert (not valid_script('tests/script5_invalid.txt'))
    assert (valid_script('tests/script6.txt'))


if __name__ == '__main__':
    pytest.main()
