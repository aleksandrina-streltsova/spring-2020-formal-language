from src.language.language_handler import parse_language, load_program, valid_program


def test_language_contains_word():
    language = parse_language()
    empty_program = load_program('tests/program0_empty.txt')
    program1 = load_program('tests/program1.txt')
    program2 = load_program('tests/program2.txt')
    program3 = load_program('tests/program3.txt')
    assert (valid_program(language, empty_program))
    assert (valid_program(language, program1))
    assert (valid_program(language, program2))
    assert (valid_program(language, program3))
