import pytest
from src import fsm_handler
from greenery import fsm


def test_regex_to_dfsm():
    case0 = fsm_handler.regex_to_dfsm("")
    assert (len(case0.states) == 1)
    assert (case0.accepts(""))
    assert (not case0.accepts("a"))

    case1 = fsm_handler.regex_to_dfsm("(ab|aab|aba)*")
    assert (len(case1.states) == 5)
    assert (case1.accepts(""))
    assert (case1.accepts("ababaaabab"))
    assert (not case1.accepts("ababbaabab"))

    case2 = fsm_handler.regex_to_dfsm("(a*b)*|(ba*)*")
    assert (len(case2.states) == 4)
    assert (case2.accepts(""))
    assert (case2.accepts("aabbb"))
    assert (not case2.accepts("aabaa"))

    case3 = fsm_handler.regex_to_dfsm("a+")
    assert (len(case3.states) == 2)
    assert (not case3.accepts(""))
    assert (case3.accepts("aaaa"))


def test_nfsm():
    case0_nfsm = fsm_handler.nfsm(
        alphabet={},
        states={0},
        initial=0,
        finals={0},
        map={}
    )
    assert (case0_nfsm.accepts(""))
    assert (not case0_nfsm.accepts("a"))

    case1_nfsm = fsm_handler.nfsm(
        alphabet={"a", "b", "c"},
        states={1, 2, 3, 4, 5, fsm.anything_else},
        initial=1,
        finals={3, 5},
        map={
            1: {"a": {2, 4}},
            2: {"b": {3}},
            4: {"c": {5}}
        }
    )
    case1_fsm = fsm.fsm(
        alphabet={"a", "b", "c"},
        states={1, 2, 3},
        initial=1,
        finals={3},
        map={
            1: {"a": 2},
            2: {"b": 3, "c": 3}
        }
    )
    assert (case1_nfsm.accepts("ab"))
    assert (not case1_nfsm.accepts("bc"))
    assert (case1_nfsm.to_fsm().equivalent(case1_fsm))

    case2_nfsm = fsm_handler.nfsm(
        alphabet={"a", "b"},
        states={1, 2},
        initial=1,
        finals={2},
        map={
            1: {"a": {1, 2}, "b": {1}},
            2: {"b": {1, 2}}
        }
    )
    case2_fsm = fsm_handler.nfsm(
        alphabet={"a", "b"},
        states={1, 2},
        initial=1,
        finals={2},
        map={
            1: {"a": 2, "b": 1},
            2: {"a": 2, "b": 2}
        }
    )
    assert (case2_nfsm.accepts("abbab"))
    assert (not case2_nfsm.accepts("bbbbb"))
    assert (case2_nfsm.to_fsm().equivalent(case2_fsm))


def test_nfsm_intersection():
    case0_nfsm = fsm_handler.nfsm(
        alphabet={},
        states={0},
        initial=0,
        finals={0},
        map={}
    )
    intersection0 = case0_nfsm.intersection(fsm_handler.regex_to_dfsm(""))
    assert (intersection0.accepts(""))
    assert (not intersection0.accepts("a"))

    case1_nfsm = fsm_handler.nfsm(
        alphabet={"a", "b", "c", "d"},
        states={1, 2, 3, 4},
        initial=1,
        finals={4},
        map={
            1: {"a": {2}, "d": {1, 3}},
            2: {"b": {4}},
            3: {"b": {2, 4}},
            4: {"c": {4}}
        }
    )
    case1_fsm = fsm.fsm(
        alphabet={"a", "b", "c"},
        states={1, 2, 3},
        initial=1,
        finals={3},
        map={
            1: {"a": 2, "c": 2},
            2: {"b": 3},
            3: {"c": 3}
        }
    )
    intersection1 = case1_nfsm.intersection(case1_fsm)
    assert (intersection1.accepts("abccc"))
    assert (not intersection1.accepts("dabc"))
    case2_nfsm = fsm_handler.nfsm(
        alphabet={"a", "b"},
        states={1, 2, 3},
        initial=1,
        finals={3},
        map={
            1: {"a": {1, 2}},
            2: {"b": {2, 3}}
        }
    )
    case2_fsm = fsm.fsm(
        alphabet={"a", "b"},
        states={1, 2},
        initial=1,
        finals={2},
        map={
            1: {"a": 2},
            2: {"b": 2}
        }
    )
    intersection2 = case2_nfsm.intersection(case2_fsm)
    assert (intersection2.accepts("abbb"))
    assert (not intersection2.accepts("aabb"))


if __name__ == '__main__':
    pytest.main()
