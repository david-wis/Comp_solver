import numpy as np
from search_methods.node import Node
import re
from utils import normalize_expression, get_token
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
    
    def __attempt_replace(expression, old_exp, new_exp):
        index = expression.find(old_exp)
        old_atomic = old_exp.find(' ') == -1
        new_atomic = new_exp.find(' ') == -1

        if index == -1 or (index+len(old_exp)+1 < len(expression) and expression[index + len(old_exp)] not in [' ', ')']):
            return []

        # If the expression is at the beginning of the string, the precedence makes the braces unnecessary
        if index == 0 or (old_atomic and new_atomic):
            return [expression.replace(old_exp, new_exp, 1)]

        # If the expression is an atomic expansion (and it's not at the beginning), braces are needed 
        if old_atomic:
            return [expression.replace(old_exp, f"({new_exp})", 1)]
        
        # old is not atomic
        if expression[index-1] == '(':
            if expression[index + len(old_exp)] == ')' and new_atomic:
                return [expression.replace(f"({old_exp})", new_exp, 1)]
            return [expression.replace(old_exp, new_exp, 1)]

        return []


    def expression_replace(self, expression):
        children = EquivalentExpressions.__attempt_replace(expression, self.short, self.long)
        if len(children) > 0:
            return [normalize_expression(c) for c in children]

        children = EquivalentExpressions.__attempt_replace(expression, self.long, self.short)
        if len(children) > 0:
            return [normalize_expression(c) for c in children]
        return [] 
    
    def __str__(self):
        return f"e/c {self.short}" if self.custom_name is None else self.custom_name

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
            return [normalize_expression(expression)]
        
        # cx (cy cz) -> c1 cx cy cz
        # TODO: Braces case
        result = re.search(r"^c[0-9]+ \(c[0-9]+ c[0-9]+\)", expression)
        if result:
            expression = re.sub(r"c[0-9]+ \(c[0-9]+ c[0-9]+\)", f"c1 {result.group().replace('(', '', 1).replace(')', '', 1)}", expression)
            return [normalize_expression(expression)]

        return []

    def __str__(self):
        return "def (.)"

    def __repr__(self):
        return str(self)
    
def expression_ended(expression, index):
    return index >= len(expression) or expression[index] == ')'

class CEvaluationDefinition:
    PLACEHOLDER = ';'

    def __init__(self, composer, transformation):
        self.composer = composer
        self.transformation = re.sub("[0-9]", CEvaluationDefinition.PLACEHOLDER, transformation)
        self.arg_count = transformation.replace('(', '').replace(')','').count(' ') + 1
    

    def expression_replace(self, expression):
        children = []
        expression = f"({expression})"
        start_index = 0
        while (index := expression.find(f"({self.composer} ", start_index)) != -1:
            substitution = self.transformation
            target, start, end = get_token(expression, index)
            index += len(self.composer) + 2 #len(f"({self.composer} ")
            start_index = index
            args = []
            while len(args) < self.arg_count and index < end - 1: #end -1 = ')'
                arg, _, index = get_token(expression, index)
                index += 1
                args.append(arg)
            if len(args) == self.arg_count:
                index -= 1
                if expression[index] == ' ':
                    start += 1
                    end = index
                for arg in args:    
                    substitution = substitution.replace(CEvaluationDefinition.PLACEHOLDER, arg, 1)
                result = expression[:start] + substitution + expression[end:]
                children.append(normalize_expression(result))
        return children
                

    def __str__(self):
        return f"def {self.composer}"
    
    def __repr__(self):
        return str(self)


class SimpleEta:
    def __init__(self):
        pass

    def expression_replace(self, expression):
        if expression.endswith(' f'):
            return [expression[:-2]]
        elif expression.find(' f ') == -1:
            return [expression + ' f']
        return []
    
    def __str__(self):
        return f"eta"
    
    def __repr__(self):
        return str(self)


known_actions = [ EquivalentExpressions(f"c{i+1}", f"c{i} c1") for i in range(1, 32)] + [
    #EquivalentExpressions("c8", "c2 c3", "lemma 3"),
    CompositionDefinition(),
    CEvaluationDefinition("c1", "(1 (2 3))"),
    CEvaluationDefinition("c2", "(1 2 (3 4))"),
    CEvaluationDefinition("c3", "(1 (2 3 4))"),
    SimpleEta()
]


class CompositionNode(Node):
    def __init__(self, state, parent=None, action=None, cost=0, comparator=None):
        super().__init__(state, parent, action, cost, comparator)

    def expand(self):
        if self.cost > 10000:
            return []
        print(self.state)
        for action in known_actions:
            new_states = action.expression_replace(self.state.exp)
            for s in new_states:
                yield CompositionNode(CompositionState(s, self.state.expec_exp), self, action, self.cost + 1, self.comparator)
            

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
    
if __name__ == "__main__":

    c2 = EquivalentExpressions("c2", "c1 c1")
    assert (c2.expression_replace("c1 (c1 c1) c1 c1 c1 c1")[0] == ("c1 c2 c1 c1 c1 c1")), f"Got: {c2.expression_replace('c1 (c1 c1) c1 c1 c1 c1')}"
    #ceval
    ceval = CEvaluationDefinition("c1", "(1 (2 3))")
    assert (len(ceval.expression_replace("c1 x y")) == 0), f"Got: {ceval.expression_replace('c1 x y')}"
    assert (len(ceval.expression_replace("c1 x (y z)")) == 0), f"Got: {ceval.expression_replace('c1 x (y z)')}"
    assert (ceval.expression_replace("c1 x y z")[0] == "x (y z)"), f"Got: {ceval.expression_replace('c1 x y z')}"
    assert (ceval.expression_replace("c1 (f x) (g y) (h z)")[0] == "f x (g y (h z))"), f"Got: {ceval.expression_replace('c1 (f x) (g y) (h z)')}"
    assert (ceval.expression_replace("c1 f (g (x y)) z")[0] == "f (g (x y) z)"), f"Got: {ceval.expression_replace('c1 f (g (x y)) z')}"
    assert (ceval.expression_replace("c1 f g x y")[0] == "f (g x) y"), f"Got: {ceval.expression_replace('c1 f g x y')}"
    assert (ceval.expression_replace("c2 (c1 f g x y)")[0] == "c2 (f (g x) y)"), f"Got: {ceval.expression_replace('c2 (c1 f g x y)')}"
    assert (len(ceval.expression_replace("c2 (c1 f g) c1")) == 0), f"Got: {ceval.expression_replace('c2 (c1 f g) c1')}"

    beval = CEvaluationDefinition("c2", "(1 2 (3 4))")
    assert (len(beval.expression_replace("c2 f g x")) == 0), f"Got: {beval.expression_replace('c2 f g x')}"
    assert (len(beval.expression_replace("c2 f x (g y)")) == 0), f"Got: {beval.expression_replace('c2 f x (g y)')}"
    assert (beval.expression_replace("c2 f x g y")[0] == "f x (g y)"), f"Got: {beval.expression_replace('c2 f x g y')}"
    assert (beval.expression_replace("c2 f x g y z")[0] == "f x (g y) z"), f"Got: {beval.expression_replace('c2 f x g y z')}"
