from search_methods.node import Node
import re
from utils import normalize_expression, binarize_expression, index_of_pointer, get_subexpressions, get_token

class BinExpNode:
    def from_string(expression_string) -> 'ExpNode':
        expression_string = binarize_expression(normalize_expression(expression_string))
        return BinExpNode._from_string(expression_string)

    def _from_string(expression_string, parent = None) -> 'ExpNode':
        exp_node = BinExpNode(parent=parent)
        if expression_string[0] != '(':
            exp_node.content = expression_string
        else:
            f_token, _, end_f = get_token(expression_string, 1)
            arg_token, _, end_arg = get_token(expression_string, end_f+1)
            assert not f_token.startswith(' ') and not arg_token.startswith(' ') and expression_string[end_f] == ' '
            assert expression_string[end_arg] == ')'  
            exp_node.f = BinExpNode._from_string(f_token, exp_node)
            exp_node.arg = BinExpNode._from_string(arg_token, exp_node)
        return exp_node
        
    def __init__(self, content = None, f = None, arg = None, parent = None):
        self.content = content
        self.f = f
        self.arg = arg
        self.parent = parent

    def __str__(self):
        if self.is_atomic():
            return self.content
        else:
            return f"({str(self.f)} {str(self.arg)})"
        
    def __repr__(self):
        return self.__str__()
    
    def is_atomic(self) -> bool:
        return self.content != None

    def copy(self, parent:'BinExpNode' = None) -> 'BinExpNode':
        exp_node = BinExpNode(content=self.content, parent=parent)
        if self.f != None:
            exp_node.f = self.f.copy(parent=exp_node)
        if self.arg != None:
            exp_node.arg = self.arg.copy(parent=exp_node)
        return exp_node
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BinExpNode):
            raise ValueError("Invalid comparison")
        if self.is_atomic() or other.is_atomic():
            return self.content == other.content
        return self.f == other.f and self.arg == other.arg
    
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
