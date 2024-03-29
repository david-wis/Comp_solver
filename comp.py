import numpy as np
from search_methods.node import Node
import re

class CompositionState(object):
    def __init__(self, exp, expec_exp) -> None:
        self.exp = exp
        self.expec_exp = expec_exp

    def __eq__(self, other):
        return self.exp == other.exp
    
    def __hash__(self) -> int:
        return hash(self.exp)

    def __str__(self):
        return self.exp


    def is_solution(self):
        return self.exp == self.expec_exp 


class EquivalentExpressions:
    def __init__(self, short, long, custom_name=None):
        self.short = short
        self.long = long
        self.custom_name = custom_name 
    
    def __attempt_replace(expression, exp_to_replace, exp_to_replace_with, replace_short=False):
        index = expression.find(exp_to_replace)
        if index == -1:
            return expression, False

        # If the expression is at the beginning of the string, the precedence makes the braces unnecessary
        if index == 0:
            return expression.replace(exp_to_replace, exp_to_replace_with, 1), True

        # If the expression is an atomic expansion (and it's not at the beginning), braces are needed 
        if replace_short:
            return expression.replace(exp_to_replace, f"({exp_to_replace_with})", 1), True

        if expression[index - 1] == "(":
            if expression[index + len(exp_to_replace)] == ")" and not replace_short:
                return expression.replace(f"({exp_to_replace})", exp_to_replace_with, 1), True
            return expression.replace(exp_to_replace, exp_to_replace_with, 1), True

        return expression, False


    def expression_replace(self, expression):
        exp, found = EquivalentExpressions.__attempt_replace(expression, self.short, self.long, replace_short=True)
        if found:
            return exp, True

        exp, found = EquivalentExpressions.__attempt_replace(expression, self.long, self.short, replace_short=False)
        if found:
            return exp, True

        return expression, False 
    
    def __str__(self):
        return f"def {self.short}" if self.custom_name is None else self.custom_name

    def __repr__(self):
        return str(self)

class CompositionDefinition:
    def __init__(self):
        pass

    def expression_replace(self, expression):
        # c1 cx cy cz -> cx (cy cz)
        result = re.search(r"(^c1 c[0-9]+ c[0-9]+ c[0-9]+)|(\(c1 c[0-9]+ c[0-9]+ c[0-9]+)", expression)
        if result:
            expression = re.sub(r"(^c1 c[0-9]+ c[0-9]+ c[0-9]+)|(\(c1 c[0-9]+ c[0-9]+ c[0-9]+)", 
                f"{result.group().replace('c1 ', '', 1).replace(' ', ' (', 1)})", expression)
            return expression, True
        
        # cx (cy cz) -> c1 cx cy cz
        # TODO: Braces case
        result = re.search(r"^c[0-9]+ \(c[0-9]+ c[0-9]+\)", expression)
        if result:
            expression = re.sub(r"c[0-9]+ \(c[0-9]+ c[0-9]+\)", f"c1 {result.group().replace('(', '', 1).replace(')', '', 1)}", expression)
            return expression, True

        return expression, False

    def __str__(self):
        return "def (.)"

    def __repr__(self):
        return str(self)



known_actions = [
    # TODO: List comprehension?
    EquivalentExpressions("c2", "c1 c1"),
    EquivalentExpressions("c3", "c2 c1"),
    EquivalentExpressions("c4", "c3 c1"),
    EquivalentExpressions("c5", "c4 c1"),
    EquivalentExpressions("c6", "c5 c1"),
    EquivalentExpressions("c7", "c6 c1"),
    EquivalentExpressions("c8", "c7 c1"),
    EquivalentExpressions("c9", "c8 c1"),
    EquivalentExpressions("c10", "c9 c1"),
    EquivalentExpressions("c11", "c10 c1"),
    EquivalentExpressions("c12", "c11 c1"),
    EquivalentExpressions("c13", "c12 c1"),
    EquivalentExpressions("c14", "c13 c1"),
    EquivalentExpressions("c15", "c14 c1"), 
    EquivalentExpressions("c16", "c15 c1"),
    EquivalentExpressions("c8", "c2 c3", "lemma 3"),
    CompositionDefinition()
]


class CompositionNode(Node):
    def __init__(self, state, parent=None, action=None, cost=0, comparator=None):
        super().__init__(state, parent, action, cost, comparator)

    def expand(self):
        if self.cost > 10000:
            return []

        for action in known_actions:
            new_state, found = action.expression_replace(self.state.exp)
            if found:
                yield CompositionNode(CompositionState(new_state, self.state.expec_exp), self, action, self.cost + 1, self.comparator)
            

    def __str__(self):
        return f"Action: {self.action}, Cost: {self.cost}" 
    
    def __hash__(self) -> int:
        return hash(self.state) 

    def get_sequence(self):
        sequence = []
        current = self
        while current is not None and current.action is not None:
            sequence.insert(0, (str(current.action), current.state.exp))
            current = current.parent
        return sequence