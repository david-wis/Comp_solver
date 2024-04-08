from search_methods.node import Node
import re
from utils import normalize_expression, index_of_pointer, get_subexpressions

class ExpNode:
    def from_string(expression_string) -> 'ExpNode':
        expression_string = normalize_expression(expression_string)
        if expression_string.count(' ') == 0:
            return ExpNode._from_string(expression_string)
        else:
            return ExpNode._from_string(f"({expression_string})")

    def _from_string(expression_string, parent = None) -> 'ExpNode':
        exp_node = ExpNode(parent=parent)
        if expression_string[0] != '(':
            exp_node.content = expression_string
        exp_node.children = [ ExpNode._from_string(se, parent=exp_node) for se in get_subexpressions(expression_string)]
        assert (len(exp_node.children) == 0 or exp_node.content is None) and (len(exp_node.children) > 0 or exp_node.content is not None)
        return exp_node
        
    def __init__(self, children = None, content = None, parent = None):
        self.children = children
        self.content = content
        self.parent = parent
    
    def __str__(self):
        if len(self.children) == 0:
            return self.content
        elif self.parent is None:
            return f"{' '.join([str(child) for child in self.children])}"
        else:
            return f"({' '.join([str(child) for child in self.children])})"
        
    def __repr__(self):
        return self.__str__()
    
    def is_atomic(self) -> bool:
        return len(self.children) == 0
    
    def copy(self, parent:'ExpNode' = None, extra_children: list['ExpNode'] = []) -> 'ExpNode':
        exp_node = ExpNode(content=self.content, parent=parent)
        exp_node.children = [child.copy(parent=exp_node) for child in (self.children + extra_children)]
        return exp_node
    

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ExpNode):
            raise ValueError("Invalid comparison")
        if self.is_atomic():
            return self.content == other.content
        if len(self.children) != len(other.children):
            return False
        for i in range(len(self.children)):
            if self.children[i] != other.children[i]:
                return False
        return True
    
    def starts_with(self, other: 'ExpNode') -> bool:
        if not isinstance(other, ExpNode):
            raise ValueError("Invalid comparison")
        if self.is_atomic():
            return self == other
        if len(self.children) < len(other.children):
            return False
        for i in range(len(other.children)):
            if self.children[i] != other.children[i]:
                return False
        return True

    def shape_like(self, shape: 'ExpNode') -> bool:
        if not isinstance(shape, ExpNode):
            raise ValueError("Invalid comparison")
        if shape.is_atomic():
            return True
        if len(self.children) < len(shape.children) or (shape.parent is not None and len(self.children) != len(shape.children)):
            return False
        for i in range(len(shape.children)):
            if not self.children[i].shape_like(shape.children[i]):
                return False
        return True

    def find_first(self, predicate: lambda x: bool) -> 'ExpNode':
        if predicate(self):
            return self
        for child in self.children:
            result = child.find_first(predicate)
            if result != None:
                return result
        return None
    
    def find_all(self, predicate: lambda x: bool) -> list['ExpNode']:
        results = []
        if predicate(self):
            results.append(self)
        for child in self.children:
            results += child.find_all(predicate)
        return results
    
    def calculate_subexpressions(self) -> list['ExpNode']:
        return self.find_all(lambda x: True)
    


class ExpressionState:
    def from_string(expression_string: str, expected_expression_string: str) -> 'ExpressionState':
        return ExpressionState(ExpNode.from_string(expression_string), ExpNode.from_string(expected_expression_string))

    def __init__(self, expression: ExpNode, expected_expression: ExpNode):
        self.expected_expression = expected_expression
        self.root = expression
        self.subexpressions = self.root.calculate_subexpressions()
        
    def __str__(self):
        return str(self.root)
    
    def __repr__(self):
        return self.__str__()
    
    def __eq__(self, value: object) -> bool:
        if value is None:
            return False
        return self.root == value.root

    def replace(self, old: ExpNode, replacement: ExpNode, extra_children=[]) -> 'ExpressionState':
        target_index = index_of_pointer(self.subexpressions, old)
        if target_index == -1: raise ValueError("Old expression not found")
        elif target_index == 0:
            return ExpressionState(replacement.copy(extra_children=extra_children), self.expected_expression)
        else:
            new_exp_root = self.root.copy()
            target = new_exp_root.calculate_subexpressions()[target_index]

            if (child_index := index_of_pointer(target.parent.children, target)) == -1: raise ValueError("target expression not found")
            replacement_copy = replacement.copy(parent=target.parent, extra_children=extra_children)
            target.parent.children[child_index] = replacement_copy

            return ExpressionState(new_exp_root, self.expected_expression)
    

def test_shape_like():
    comp_shape = ExpNode.from_string("a b c")
    assert ExpNode.from_string("c1 c1 c1").shape_like(comp_shape)
    assert ExpNode.from_string("c1 c1 c1 c1").shape_like(comp_shape)
    assert ExpNode.from_string("c1 c1 c1 c1 c1").shape_like(comp_shape)
    assert not ExpNode.from_string("c1 c1").shape_like(comp_shape)
    assert not ExpNode.from_string("c1 (c1 c1 c1)").shape_like(comp_shape)
    assert ExpNode.from_string("(c1 c1) c1 c1").shape_like(comp_shape)
    assert ExpNode.from_string("c1 (c1 c1) c1").shape_like(comp_shape)
    assert ExpNode.from_string("c1 c1 (c1 c1)").shape_like(comp_shape)
    assert ExpNode.from_string("(c1 c1) (c1 c1) (c1 c1)").shape_like(comp_shape)
    assert ExpNode.from_string("(c1 c1) (c1 c1) (c1 c1) c1").shape_like(comp_shape)
    assert ExpNode.from_string("c1 (c1 c1) (c1 (c1 1))").shape_like(comp_shape)

    comp_shape = ExpNode.from_string("a (b c)")
    assert ExpNode.from_string("c1 (c1 c1)").shape_like(comp_shape)
    assert ExpNode.from_string("c1 (c1 c1) c1").shape_like(comp_shape)
    assert ExpNode.from_string("c1 (c1 c1) (c1 c1)").shape_like(comp_shape)
    assert ExpNode.from_string("c1 (c1 (f c1))").shape_like(comp_shape)
    assert not ExpNode.from_string("c1 c1").shape_like(comp_shape)
    assert not ExpNode.from_string("c1 c1 c1").shape_like(comp_shape)
    #assert ExpNode.from_string("c1 (c1 c1 c1)").shape_like(comp_shape)

    

def test_calculate_subexpressions():
    exp_str_list = ["a b c", "a (b c)", "(a b) (c d) (e f)", "a (b (c d) e) f", "a (b c) d e f", "x (a (b (c (d (e f)))))"]
    for exp_str in exp_str_list:
        exp = ExpressionState.from_string(exp_str, "c1")
        subexpressions = exp.root.calculate_subexpressions()
        assert all(se == subexpressions[i] for i, se in enumerate(exp.subexpressions))
        pass
    
def test_replacement():
    old_pattern = ExpNode.from_string("a b c")
    new_pattern = ExpNode.from_string("a (b c)")
    exp = ExpressionState.from_string("a b c (a b c) (a b c d) (a b c d e)", "c1")
    occurrences = exp.root.find_all(lambda x: x.starts_with(old_pattern))
    for occ in occurrences:
        new_exp = exp.replace(occ, new_pattern, extra_children=occ.children[len(old_pattern.children):])
        print(exp, '>', new_exp)

if __name__ == "__main__":
    test_shape_like()
    test_calculate_subexpressions()
    test_replacement()
