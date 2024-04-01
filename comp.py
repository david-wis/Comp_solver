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

def get_token(expression, start_index):
    current_index = start_index
    if expression[current_index] == ' ': raise ValueError("Invalid expression")
    if expression[current_index] == '(':
        scope_count = 1
        while scope_count > 0 and current_index < len(expression):
            current_index += 1
            scope_count += (expression[current_index] == '(') - (expression[current_index] == ')')
        if scope_count != 0:
            raise ValueError("Invalid parenthesis")
        current_index += 1        
    else:
        while current_index < len(expression) and expression[current_index] != ')' and expression[current_index] != ' ':
            current_index += 1
    return expression[start_index:current_index], start_index, current_index

def get_all_subexpressions(expression):
    subexpressions = []
    index = 0
    while index < len(expression):
        if index == 0 or expression[index] == '(' or expression[index - 1] == ' ' or expression[index - 1] == '(':
            token, start, end = get_token(expression, index)
            subexpressions.append(token)
        index += 1
        
    return subexpressions

    
def normalize_expression(expression):
    while expression.startswith("("):
        _, _, end = get_token(expression, 0)
        expression = expression[1:end - 1] + expression[end:]
    index = expression.find("((")
    while (index := expression.find("((", index)) != -1:
        _, _, end = get_token(expression, index + 1)
        expression = expression[:index] + expression[index+1:end-1]+ expression[end:]
    return expression

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
            return expression, False

        # If the expression is at the beginning of the string, the precedence makes the braces unnecessary
        if index == 0 or (old_atomic and new_atomic):
            return expression.replace(old_exp, new_exp, 1), True

        # If the expression is an atomic expansion (and it's not at the beginning), braces are needed 
        if old_atomic:
            return expression.replace(old_exp, f"({new_exp})", 1), True
        
        # old is not atomic
        if expression[index-1] == '(':
            if expression[index + len(old_exp)] == ')' and new_atomic:
                return expression.replace(f"({old_exp})", new_exp, 1), True
            return expression.replace(old_exp, new_exp, 1), True

        return expression, False


    def expression_replace(self, expression):
        exp, found = EquivalentExpressions.__attempt_replace(expression, self.short, self.long)
        if found:
            return normalize_expression(exp), True

        exp, found = EquivalentExpressions.__attempt_replace(expression, self.long, self.short)
        if found:
            return normalize_expression(exp), True

        return expression, False 
    
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
    
def expression_ended(expression, index):
    return index >= len(expression) or expression[index] == ')'

class CEvaluationDefinition:
    PLACEHOLDER = ';'

    def __init__(self, composer, transformation):
        self.composer = composer
        self.transformation = re.sub("[0-9]", CEvaluationDefinition.PLACEHOLDER, transformation)
        self.arg_count = transformation.replace('(', '').replace(')','').count(' ') + 1
    

    def expression_replace(self, expression):
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
                return normalize_expression(result), True
        return expression[1:-1], False
                

    def __str__(self):
        return f"def {self.composer}"
    
    def __repr__(self):
        return str(self)


known_actions = [ EquivalentExpressions(f"c{i+1}", f"c{i} c1") for i in range(1, 32)] + [
    EquivalentExpressions("c8", "c2 c3", "lemma 3"),
    CompositionDefinition(),
    CEvaluationDefinition("c1", "(1 (2 3))"),
    CEvaluationDefinition("c2", "(1 2 (3 4))"),
    CEvaluationDefinition("c3", "(1 (2 3 4))"),
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
    
if __name__ == "__main__":

    c2 = EquivalentExpressions("c2", "c1 c1")
    assert (c2.expression_replace("c1 (c1 c1) c1 c1 c1 c1") == ("c1 c2 c1 c1 c1 c1", True)), f"Got: {c2.expression_replace('c1 (c1 c1) c1 c1 c1 c1')}"
    #normalize expression
    assert (normalize_expression("a b") == "a b"), f"Got: {normalize_expression('a b')}"
    assert (normalize_expression("(a b)") == "a b"), f"Got: {normalize_expression('(a b)')}"
    assert (normalize_expression("((a b) c)") == "a b c"), f"Got: {normalize_expression('((a b) c)')}"
    assert (normalize_expression("((a b) (c d))") == "a b (c d)"), f"Got: {normalize_expression('((a b) (c d))')}"
    assert (normalize_expression("a (b c)") == "a (b c)"), f"Got: {normalize_expression('a (b c)')}"
    assert (normalize_expression("(((((a b) c) d) e) f) h") == "a b c d e f h"), f"Got: {normalize_expression('(((((a b) c) d) e) f) h')}"
    assert (normalize_expression("a (b (c (d (e f))))") == "a (b (c (d (e f))))"), f"Got: {normalize_expression('a (b (c (d (e f))))')}"
    assert (normalize_expression("a (b c) (d e) (e f)") == "a (b c) (d e) (e f)"), f"Got: {normalize_expression('a (b c) (d e) (e f)')}"
    assert (normalize_expression("a ((b c) d) ((e f) g) (h (i j))") == "a (b c d) (e f g) (h (i j))"), f"Got: {normalize_expression('a ((b c) d) ((e f) g) (h (i j))')}"
    assert (normalize_expression("a b (c ((d e) f) ((g h) (i j)))") == "a b (c (d e f) (g h (i j)))"), f"Got: {normalize_expression('a b (c ((d e) f) ((g h) (i j)))')}"
    #ceval
    ceval = CEvaluationDefinition("c1", "(1 (2 3))")
    assert (ceval.expression_replace("c1 x y") == ("c1 x y", False)), f"Got: {ceval.expression_replace('c1 x y')}"
    assert (ceval.expression_replace("c1 x (y z)") == ("c1 x (y z)", False)), f"Got: {ceval.expression_replace('c1 x (y z)')}"
    assert (ceval.expression_replace("c1 x y z") == ("x (y z)", True)), f"Got: {ceval.expression_replace('c1 x y z')}"
    assert (ceval.expression_replace("c1 (f x) (g y) (h z)") == ("f x (g y (h z))", True)), f"Got: {ceval.expression_replace('c1 (f x) (g y) (h z)')}"
    assert (ceval.expression_replace("c1 f (g (x y)) z") == ("f (g (x y) z)", True)), f"Got: {ceval.expression_replace('c1 f (g (x y)) z')}"
    assert (ceval.expression_replace("c1 f g x y") == ("f (g x) y", True)), f"Got: {ceval.expression_replace('c1 f g x y')}"
    assert (ceval.expression_replace("c2 (c1 f g x y)") == ("c2 (f (g x) y)", True)), f"Got: {ceval.expression_replace('c2 (c1 f g x y)')}"
    assert (ceval.expression_replace("c2 (c1 f g) c1") == ("c2 (c1 f g) c1", False)), f"Got: {ceval.expression_replace('c2 (c1 f g) c1')}"

    beval = CEvaluationDefinition("c2", "(1 2 (3 4))")
    assert (beval.expression_replace("c2 f g x") == ("c2 f g x", False)), f"Got: {beval.expression_replace('c2 f g x')}"
    assert (beval.expression_replace("c2 f x (g y)") == ("c2 f x (g y)", False)), f"Got: {beval.expression_replace('c2 f x (g y)')}"
    assert (beval.expression_replace("c2 f x g y") == ("f x (g y)", True)), f"Got: {beval.expression_replace('c2 f x g y')}"
    assert (beval.expression_replace("c2 f x g y z") == ("f x (g y) z", True)), f"Got: {beval.expression_replace('c2 f x g y z')}"