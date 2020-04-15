import pytest
from src.linear_algebra import grammar_connected_vertices_matrix, grammar_connected_vertices_tensor_product


def test_matrix1():  # a^n b^n
    connected_vertices = {(0, 2), (0, 3), (1, 2), (1, 3), (2, 2), (2, 3)}
    assert (grammar_connected_vertices_matrix('tests/grammar7.txt', 'tests/graph1.txt') == connected_vertices)


def test_matrix2():  # однозначная грамматика (ПСП)
    connected_vertices = {(0, 0), (1, 1), (2, 2), (3, 3), (0, 2), (0, 3), (1, 2), (1, 3), (2, 2), (2, 3)}
    assert (grammar_connected_vertices_matrix('tests/grammar1_cbs.txt', 'tests/graph1.txt') == connected_vertices)


def test_matrix3():  # неоднозначная грамматика (ПСП)
    connected_vertices = {(0, 0), (1, 1), (2, 2), (3, 3), (0, 2), (0, 3), (1, 2), (1, 3), (2, 2), (2, 3)}
    assert (grammar_connected_vertices_matrix('tests/grammar9_cbs.txt', 'tests/graph1.txt') == connected_vertices)


def test_matrix4():  # пустой граф
    assert (grammar_connected_vertices_matrix('tests/grammar7.txt', 'tests/graph2_empty.txt') == set())


def test_matrix5():  # мультиграф
    connected_vertices = {(0, 1), (0, 2), (0, 0), (1, 1), (2, 2)}
    assert (grammar_connected_vertices_matrix('tests/grammar8_cbs.txt', 'tests/graph3.txt') == connected_vertices)


def test_matrix6():  # существенно неоднозначный язык
    connected_vertices = {(0, 3), (0, 4), (0, 5), (0, 6), (0, 7),
                          (1, 3), (1, 4), (1, 5), (1, 6), (1, 7),
                          (2, 3), (2, 4), (2, 5), (2, 6), (2, 7)}
    assert (grammar_connected_vertices_matrix('tests/grammar10.txt', 'tests/graph4.txt') == connected_vertices)


def test_tensor_product1():
    connected_vertices = {(0, 2), (0, 3), (1, 2), (1, 3), (2, 2), (2, 3)}
    assert (grammar_connected_vertices_tensor_product('tests/grammar12_fsm.txt',
                                                      'tests/graph1.txt') == connected_vertices)


def test_tensor_product2():
    connected_vertices = {(0, 2), (0, 4), (0, 6), (2, 4), (2, 6), (4, 6),
                          (0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6)}
    assert (grammar_connected_vertices_tensor_product('tests/grammar11_fsm.txt',
                                                      'tests/graph5.txt') == connected_vertices)


def test_tensor_product3():
    connected_vertices = {(0, 2), (0, 4), (0, 6), (2, 4), (2, 6), (4, 6),
                          (0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6)}
    assert (grammar_connected_vertices_tensor_product('tests/grammar13_fsm.txt',
                                                      'tests/graph5.txt') == connected_vertices)


if __name__ == '__main__':
    pytest.main()
