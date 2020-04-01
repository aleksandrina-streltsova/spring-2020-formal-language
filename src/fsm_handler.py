from greenery import lego, fsm
from collections import deque


def regex_to_dfsm(regex):
    # parse разбирает строку и возвращает lego piece, to_fsm() строит минимальный ДКА
    return lego.parse(regex).to_fsm()


# недетерминированный конечный автомат без eps-переходов
class nfsm:
    # поля класса соответствуют полям fsm, но в map каждому символу
    # соответствует не одно состояние, а множество состояний
    def __init__(self, alphabet, states, initial, finals, map):
        self.__dict__["alphabet"] = set(alphabet)
        self.__dict__["states"] = set(states)
        self.__dict__["initial"] = initial
        self.__dict__["finals"] = set(finals)
        self.__dict__["map"] = map

    def accepts(self, input):
        states = {self.initial}
        for symbol in input:
            if fsm.anything_else in self.alphabet and not symbol in self.alphabet:
                symbol = fsm.anything_else
            next_states = set()
            for state in states:
                if state in self.map and symbol in self.map[state]:
                    next_states = next_states.union(self.map[state][symbol])
            states = next_states
        return len(states.intersection(self.finals)) != 0

    # возвращает минимальный ДКА, принимающий те же строчки, что и данный НКА
    def to_fsm(self):
        q = deque()
        # sst - множество состояний
        initial_sst = frozenset({self.initial})
        q.append(initial_sst)

        sst_map = {}  # переходы из множеств состояний в множества состояний
        used_ssts = {initial_sst}
        final_ssts = set()

        # пока очередь не пуста, по множеству состояний строим новое,
        # в которое можно перейти по данному символу
        while len(q) != 0:
            sst = q.pop()
            transitions = {}  # переходы из данного множества в другие
            for symbol in self.alphabet:
                # строим множество, в которое можно перейти по данному символу
                new_sst = set()
                for state in sst:
                    if state in self.map and symbol in self.map[state]:
                        new_sst = new_sst.union(self.map[state][symbol])
                new_sst = frozenset(new_sst)

                # добавляем переход в полученное множество
                if len(new_sst):
                    transitions[symbol] = new_sst

                # добавляем множество в финальные, если в нём встречается финальная вершина
                if len(new_sst.intersection(self.finals)):
                    final_ssts.add(new_sst)

                # добавляем в очередь новое состояние
                if len(new_sst) and new_sst not in used_ssts:
                    q.append(new_sst)
                    used_ssts.add(new_sst)
            # добавляем получившиеся переходы из исходного множества
            if len(transitions):
                sst_map[sst] = transitions

        # присваиваем каждому множеству состояний свой номер
        sst_dict = {}
        for sst in used_ssts:
            sst_dict[sst] = len(sst_dict)

        new_map = {}
        for sst, sst_transitions in sst_map.items():
            new_transitions = {}
            for symbol, other_sst in sst_transitions.items():
                new_transitions[symbol] = sst_dict[other_sst]
            new_map[sst_dict[sst]] = new_transitions

        new_finals = set(map(lambda sst: sst_dict[sst], list(final_ssts)))

        return fsm.fsm(
            alphabet=self.alphabet,
            states=set(range(len(sst_dict))),
            initial=sst_dict[initial_sst],
            finals=new_finals,
            map=new_map
        ).reduce()

    # строит пересечение с ДКА
    def intersection(self, other):
        alphabet = self.alphabet.intersection(other.alphabet)
        # pstate - пара состояний
        pstates = {(self.initial, other.initial)}  # пары состояний, перебираемые на текущей итерации

        used_pstates = set()
        pstates_map = {}  # переходы из пар состояний в пары состояний
        final_pstates = set()
        while len(pstates):
            next_pstates = set()
            for state_nfsm, state_fsm in pstates:
                current = (state_nfsm, state_fsm)
                # переходы из current в другие пары состояний
                transitions = {}
                for symbol in alphabet:
                    if state_nfsm in self.map and symbol in self.map[state_nfsm] \
                            and state_fsm in other.map and symbol in other.map[state_fsm]:
                        # пары состояний, в которые можно перейти из current по текущему символу
                        next_by_symbol = set()
                        for pstate in self.map[state_nfsm][symbol]:
                            next_by_symbol.add((pstate, other.map[state_fsm][symbol]))
                        transitions[symbol] = next_by_symbol
                        next_pstates = next_pstates.union(next_by_symbol)

                if len(transitions):
                    pstates_map[current] = transitions
                if state_nfsm in self.finals and state_fsm in other.finals:
                    final_pstates.add(current)

            used_pstates = used_pstates.union(pstates)
            pstates = next_pstates.difference(used_pstates)

        # присваиваем каждой паре состояний свой номер
        pstate_dict = {}
        for pstate in used_pstates:
            pstate_dict[pstate] = len(pstate_dict)

        new_map = {}
        for pstate, pstate_transitions in pstates_map.items():
            new_transitions = {}
            for symbol in pstate_transitions.keys():
                new_transitions[symbol] = set()
                for next_pstate in pstate_transitions[symbol]:
                    new_transitions[symbol].add(pstate_dict[next_pstate])
            new_map[pstate_dict[pstate]] = new_transitions

        new_finals = set(map(lambda pstate: pstate_dict[pstate], list(final_pstates)))

        return nfsm(
            alphabet=alphabet,
            states=set(range(len(pstate_dict))),
            initial=pstate_dict[(self.initial, other.initial)],
            finals=new_finals,
            map=new_map
        )
