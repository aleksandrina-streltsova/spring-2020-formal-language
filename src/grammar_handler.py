from collections import deque
import networkx as nx


def convert_grammar_from_file_into_cnf(fin, fout):
    grammar = Grammar()
    grammar.parse(fin)
    grammar.to_cnf()
    grammar.write_grammar(fout)


class Rule:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __eq__(self, other):
        return self.left == other.left and self.right == other.right

    def __hash__(self):
        return hash((self.left, self.right))


class Grammar:
    def __init__(self):
        self.rules = set()
        self.nonterm_alphabet = set()
        self.term_alphabet = set()
        self.initial = 'S'
        self.epsilon = 'eps'
        self.capitalized_normally = True

    def __str__(self):
        result = ''
        for rule in self.rules:
            result += rule.left + ' -> ' + ' '.join(rule.right) + '\n'
        return result

    def parse(self, filename):
        with open(filename) as file:
            self.set_initial(file)
            for line in file.readlines():
                self.add_rule(line)

    def to_cnf(self):
        self.remove_initial_from_right()
        self.eliminate_long_rules()
        self.eliminate_eps_rules()
        self.eliminate_unit_rules()
        self.eliminate_nongenereting_nonterms()
        self.eliminate_nonaccessible_nonterms()
        self.replace_terms_with_nonterms()
        self.update_alphabets()

    def to_wcnf(self):
        self.eliminate_long_rules()
        self.eliminate_unit_rules()
        self.eliminate_nongenereting_nonterms()
        self.eliminate_nonaccessible_nonterms()
        self.replace_terms_with_nonterms()
        self.update_alphabets()

    def eliminate_long_rules(self):
        (symbol, index) = self.__generate_nonterm()
        new_rules = set()
        rules_to_be_deleted = set()
        for rule in self.rules:
            if len(rule.right) > 2:
                current_nonterm = rule.left
                for i in range(len(rule.right) - 2):
                    index += 1
                    next_nonterm = symbol + str(index)
                    self.nonterm_alphabet.add(next_nonterm)
                    new_rules.add(Rule(current_nonterm, (rule.right[i], next_nonterm)))
                    current_nonterm = next_nonterm
                new_rules.add(Rule(current_nonterm, (rule.right[-2], rule.right[-1])))
                rules_to_be_deleted.add(rule)
        self.rules = new_rules.union(self.rules).difference(rules_to_be_deleted)

    def eliminate_eps_rules(self):
        concerned_rules = {}
        eps_nonterms = set()
        new_rules = set()
        q = deque()
        for nonterm in self.nonterm_alphabet:
            concerned_rules[nonterm] = set()
        counter = {}
        for rule in self.rules:
            if len(rule.right) == 1 and rule.right[0] == self.epsilon:
                counter[rule] = 0
                if rule.left not in eps_nonterms:
                    q.append(rule.left)
                    eps_nonterms.add(rule.left)
            else:
                counter[rule] = len(set(rule.right))
            for term in rule.right:
                if term in self.nonterm_alphabet:
                    concerned_rules[term].add(rule)

        while len(q) > 0:
            nonterm = q.pop()
            for rule in concerned_rules[nonterm]:
                counter[rule] -= 1
                if counter[rule] == 0 and rule.left not in eps_nonterms:
                    q.appendleft(rule.left)
                    eps_nonterms.add(rule.left)
        for rule in self.rules:
            new_rules = new_rules.union(self.instead_eps_rules(eps_nonterms, rule.left, [], list(rule.right)))

        self.rules = set(filter(lambda rule: rule.right != (self.epsilon,) and len(rule.right) > 0,
                                self.rules.union(new_rules)))

        if self.initial in eps_nonterms:
            self.rules.add(Rule(self.initial, (self.epsilon,)))

    def eliminate_unit_rules(self):
        unit_rules = list(filter(lambda rule: len(rule.right) == 1 and
                                              rule.right[0] in self.nonterm_alphabet, self.rules))
        graph = nx.DiGraph()
        graph.add_nodes_from(self.nonterm_alphabet)
        graph.add_edges_from(map(lambda rule: (rule.left, rule.right[0]), unit_rules))
        new_rules = set()
        for rule in self.rules:
            right = rule.left
            for left in self.nonterm_alphabet:
                if nx.has_path(graph, left, right):
                    if not (len(rule.right) == 1 and rule.right[0] in self.nonterm_alphabet):
                        new_rules.add(Rule(left, rule.right))
        self.rules = self.rules.union(new_rules).difference(unit_rules)

    def eliminate_nongenereting_nonterms(self):
        concerned_rules = {}
        generating_nonterms = set()
        new_rules = set()
        q = deque()
        for nonterm in self.nonterm_alphabet:
            concerned_rules[nonterm] = set()
        counter = {}
        for rule in self.rules:
            counter[rule] = len(set(filter(lambda term: term in
                                                        self.nonterm_alphabet, rule.right)))
            if counter[rule] == 0:
                if rule.left not in generating_nonterms:
                    q.append(rule.left)
                    generating_nonterms.add(rule.left)
            for term in rule.right:
                if term in self.nonterm_alphabet:
                    concerned_rules[term].add(rule)

        while len(q) > 0:
            nonterm = q.pop()
            for rule in concerned_rules[nonterm]:
                counter[rule] -= 1
                if counter[rule] == 0 and rule.left not in generating_nonterms:
                    q.appendleft(rule.left)
                    generating_nonterms.add(rule.left)

        for rule in self.rules:
            if counter[rule] == 0:
                new_rules.add(rule)
        self.rules = new_rules

    def eliminate_nonaccessible_nonterms(self):
        nonaccess_nonterms = set()
        rules_to_be_deleted = set()
        edges = set()

        for rule in self.rules:
            for right in rule.right:
                edges.add((rule.left, right))

        graph = nx.DiGraph()
        graph.add_nodes_from(self.nonterm_alphabet)
        graph.add_edges_from(edges)
        for nonterm in self.nonterm_alphabet:
            if not nx.has_path(graph, self.initial, nonterm):
                nonaccess_nonterms.add(nonterm)

        for rule in self.rules:
            if rule.left in nonaccess_nonterms:
                rules_to_be_deleted.add(rule)
                continue
            for term in rule.right:
                if term in nonaccess_nonterms:
                    rules_to_be_deleted.add(rule)
                    break

        self.rules = self.rules.difference(rules_to_be_deleted)

    def replace_terms_with_nonterms(self):
        rules_to_be_deleted = set()
        new_rules = set()
        term_to_nonterm = {}
        (symbol, index) = self.__generate_nonterm()

        for rule in self.rules:
            if len(rule.right) > 1:
                new_right = []
                for term in rule.right:
                    new_term = term
                    if term in self.term_alphabet:
                        if term not in term_to_nonterm:
                            index += 1
                            new_nonterm = symbol + str(index)
                            self.nonterm_alphabet.add(new_nonterm)
                            term_to_nonterm[term] = new_nonterm
                            new_rules.add(Rule(new_nonterm, (term,)))
                        new_term = term_to_nonterm[term]
                    new_right.append(new_term)
                new_right = tuple(new_right)
                if new_right != rule.right:
                    rules_to_be_deleted.add(rule)
                    new_rules.add(Rule(rule.left, new_right))
        self.rules = self.rules.union(new_rules).difference(rules_to_be_deleted)

    def __generate_nonterm(self):
        alphabet = map(lambda term: ''.join([c for c in term if not c.isdigit()]), list(self.nonterm_alphabet))
        a = 'A' if self.capitalized_normally else 'a'
        z = 'Z' if self.capitalized_normally else 'z'
        symbol = a
        if len(self.nonterm_alphabet) != 0:
            max_symbol = max(alphabet)
            if max_symbol[-1] == z:
                symbol = max_symbol + a
            else:
                symbol = max_symbol[:-1] + chr(ord(max_symbol[-1]) + 1)
        return symbol, 0

    def set_initial(self, file):
        first_line = file.readline().split()
        if len(first_line) > 0:
            self.initial = first_line[0]
        file.seek(0)

    def add_rule(self, rule):
        self.add_symbols_from_iterable(rule.split())
        left, *right = rule.split()
        if not (len(right) == 1 and right[0] == self.epsilon):
            right = filter(lambda symbol: symbol != self.epsilon, right)
        self.rules.add(Rule(left, tuple(right)))

    def add_symbols_from_iterable(self, iterable):
        for symbol in iterable:
            if self.capitalized_normally:
                if symbol != self.epsilon:
                    if symbol.lower() == symbol:
                        self.term_alphabet.add(symbol)
                    else:
                        self.nonterm_alphabet.add(symbol)
            else:
                if symbol != self.epsilon:
                    if symbol.lower() == symbol:
                        self.nonterm_alphabet.add(symbol)
                    else:
                        self.term_alphabet.add(symbol)

    def instead_eps_rules(self, eps_nonterms, left, list_left, list_right):
        eps_term_index = -1
        for i in range(len(list_right)):
            if list_right[i] in eps_nonterms:
                eps_term_index = i
                break
        if eps_term_index == -1:
            eps_term_index = len(list_right)
        list_left = list_left + list_right[0: eps_term_index]
        list_right = list_right[eps_term_index:]
        if len(list_right) == 0 and len(list_left) == 0:
            return set()
        if len(list_right) == 0:
            return {Rule(left, tuple(list_left))}
        eps_term = list_right[0]
        list_right = list_right[1:]
        return self.instead_eps_rules(eps_nonterms, left, list_left, list_right).union(
            self.instead_eps_rules(eps_nonterms, left, list_left + [eps_term], list_right)
        )

    def remove_initial_from_right(self):
        (symbol, index) = self.__generate_nonterm()
        new_nonterm = symbol + str(index + 1)
        self.nonterm_alphabet.add(new_nonterm)
        new_rules = set()
        for rule in self.rules:
            new_rule = rule
            if self.initial == rule.left or self.initial in rule.right:
                replace = lambda symbol: symbol if self.initial != symbol else new_nonterm
                new_rule = Rule(replace(rule.left), tuple(map(replace, rule.right)))
            new_rules.add(new_rule)
        self.rules = new_rules
        self.rules.add(Rule(self.initial, (new_nonterm,)))
        self.nonterm_alphabet.add(new_nonterm)

    def write_grammar(self, filename):
        with open(filename, 'w') as file:
            for rule in self.rules:
                file.write(rule.left + ' ' + ' '.join(rule.right) + '\n')

    def update_alphabets(self):
        self.nonterm_alphabet = set()
        self.term_alphabet = set()
        for rule in self.rules:
            self.nonterm_alphabet.add(rule.left)
            self.add_symbols_from_iterable(rule.right)
