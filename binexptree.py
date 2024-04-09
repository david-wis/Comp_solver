from search_methods.node import Node
import re
from utils import normalize_expression, binarize_expression, index_of_pointer, get_subexpressions, get_token
from search_methods.bfs import search

class BinExpNode:
    def from_string(expression_string) -> 'BinExpNode':
        expression_string = binarize_expression(normalize_expression(expression_string))
        return BinExpNode._from_string(expression_string)

    def _from_string(expression_string, parent = None) -> 'BinExpNode':
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
        
    def __init__(self, content:str = None, f:'BinExpNode' = None, arg:'BinExpNode' = None, parent:'BinExpNode' = None):
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
            if other == None: return False
            raise ValueError("Invalid comparison")
        if self.is_atomic() or other.is_atomic():
            return self.content == other.content
        return self.f == other.f and self.arg == other.arg
    
    def __hash__(self) -> int:
        return hash((self.content, self.f, self.arg))
    
    def shape_like(self, shape: 'BinExpNode') -> bool:
        if not isinstance(shape, BinExpNode):
            raise ValueError("Invalid comparison")
        elif shape.is_atomic():
            return True
        elif self.is_atomic():
            return shape.is_atomic()
        else:
            assert self.f != None and self.arg != None and shape.f != None and shape.arg != None
            return self.f.shape_like(shape.f) and self.arg.shape_like(shape.arg)

    def find_first(self, predicate: lambda x: bool) -> 'BinExpNode':
        if predicate(self):
            return self
        if self.f != None:
            result = self.f.find_first(predicate)
            if result != None:
                return result
        if self.arg != None:
            result = self.arg.find_first(predicate)
            if result != None:
                return result
        return None
            
    
    def find_all(self, predicate: lambda x: bool) -> list['BinExpNode']:
        results = []
        if predicate(self):
            results.append(self)
        if self.f != None:
            results += self.f.find_all(predicate)
        if self.arg != None:
            results += self.arg.find_all(predicate)
        return results
    
    def calculate_subexpressions(self) -> list['BinExpNode']:
        return self.find_all(lambda x: True)

class BinExpTree:
    def from_string(expression_string:str, expected_string:str) -> 'BinExpTree':
        return BinExpTree(BinExpNode.from_string(expression_string), BinExpNode.from_string(expected_string))

    def __init__(self, root:BinExpNode, expected:BinExpNode) -> None:
        self.root = root
        self.subexpressions = self.root.calculate_subexpressions()
        self.expected = expected

    def __str__(self):
        return str(self.root)

    def __repr__(self):
        return self.__str__()
    
    def __hash__(self):
        return self.root.__hash__()
    
    def replace(self, old: BinExpNode, replacement: BinExpNode) -> 'BinExpTree':
        target_index = index_of_pointer(self.subexpressions, old)
        if target_index == -1: raise ValueError("Old expression not found")
        elif target_index == 0:
            return BinExpTree(replacement.copy(), self.expected)
        else:
            new_exp_root = self.root.copy()
            target = new_exp_root.calculate_subexpressions()[target_index]

            replacement_copy = replacement.copy(parent=target.parent)
            if old is old.parent.f:
                target.parent.f = replacement_copy
            elif old is old.parent.arg:
                target.parent.arg = replacement_copy
            return BinExpTree(new_exp_root, self.expected)

    def is_solution(self):
        return self.root == self.expected    


def equivalent_replace(exp1: BinExpNode, exp2: BinExpNode):
    def replace(tree: BinExpTree) -> list[BinExpTree]:
        occurrences = tree.root.find_all(lambda x: x == exp1)
        return [tree.replace(o, exp2) for o in occurrences]
    return replace

actions = [
    equivalent_replace(BinExpNode.from_string("c1 c1"), BinExpNode.from_string("c2"))
]

class BinSearchNode(Node):
    def __init__(self, state: BinExpTree, parent:'BinSearchNode'=None, action=None, cost=0, comparator=None):
        super().__init__(state, parent, action, cost, comparator)
        assert state.expected is not None
    
    def from_strings(original: str, expected: str, eta_enabled = False):
        return BinSearchNode(BinExpTree.from_string(original, expected))
    
    def __repr__(self) -> str:
        return f"{str(self.state)}\n{self.action}"

    def expand(self):
        if (self.cost > 200):
            return []
        expanded_nodes = [BinSearchNode(result, self, action, self.cost+1, self.comparator) for action in actions for result in action(self.state)]
        return expanded_nodes 

    def get_sequence(self):
        sequence = []
        current = self
        while current is not None and current.action is not None:
            sequence.insert(0, current.action)
            current = current.parent
        return sequence

    def get_path(self):
        path = []
        current = self
        while current is not None and current.action is not None:
            path.insert(0, current.state)
            current = current.parent
        return path
            
    def __hash__(self) -> int:
        return self.state.__hash__()
    
if __name__ == '__main__':
    initial_node = BinSearchNode(BinExpTree.from_string("c1 c1 c1 (c1 c1)", "c2 c1 c2"))
    solution, _, _ = search(initial_node)
    current_state = initial_node.state
    for n in solution.get_path():
        print(n)