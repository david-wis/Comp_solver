from search_methods.node import Node
import re
from utils import normalize_expression, binarize_expression, index_of_pointer, get_subexpressions, get_token
from search_methods import bfs, dfs, greedy, astar
from typing import Callable, Tuple
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
        if f != None:
            self.f.parent = self
        self.arg = arg
        if arg != None:
            self.arg.parent = self
        self.parent = parent

    def __str__(self):
        if self.is_atomic():
            return self.content
        else:
            if self.parent == None or self.parent.f is self:
                return f"{str(self.f)} {str(self.arg)}"
            else:
                return f"({str(self.f)} {str(self.arg)})"
        
    def __repr__(self):
        return self.__str__()
    
    def is_atomic(self) -> bool:
        return self.content != None
    
    def is_parameter(self) -> bool:
        return self.is_atomic() and self.content.startswith('$')
    
    def is_eta_parameter(self, level:int = None) -> bool:
        if level == None:
            return self.is_atomic() and re.search("^f[1-9][0-9]*$",self.content) != None
        return self.is_atomic() and self.content == f"f{level}"
    
    def is_simple(self) -> bool:
        if self.is_atomic():
            return True
        return self.arg.is_atomic() and self.f.is_simple()
    
    def depth(self) -> int:
        if self.parent == None:
            return 0
        return 1 + self.parent.depth()

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
    
    def shape_like(self, shape: 'BinExpNode', params: dict[str, 'BinExpNode']) -> bool:
        if not isinstance(shape, BinExpNode):
            raise ValueError("Invalid comparison")
        elif shape.is_parameter():
            if shape.content in params:
                return self == params[shape.content]
            else:
                params[shape.content] = self
            return True
        elif self.is_atomic() or shape.is_atomic():
            return shape == self
        else:
            assert self.f != None and self.arg != None and shape.f != None and shape.arg != None
            return self.f.shape_like(shape.f, params) and self.arg.shape_like(shape.arg, params)
            
    def replace_node(self, replacement: 'BinExpNode') -> None:
        if self.parent == None:
            raise ValueError("Invalid replacement")
        if self is self.parent.f:
            self.parent.f = replacement.copy(parent=self.parent)
        elif self is self.parent.arg:
            self.parent.arg = replacement.copy(parent=self.parent)
        else:
            raise ValueError("Invalid replacement")

    def replace_arguments(self, params: dict[str, 'BinExpNode']) -> None:
        if self.is_parameter():
            if self.content in params:
                self.replace_node(params[self.content])
        else:
            if self.f != None:
                self.f.replace_arguments(params)
            if self.arg != None:
                self.arg.replace_arguments(params)

    def find_first(self, predicate: lambda x: bool, inverted : bool = False) -> 'BinExpNode':
        if predicate(self):
            return self
        first, second = (self.f, self.arg) if not inverted else (self.arg, self.f)
        if first != None:
            result = first.find_first(predicate, inverted)
            if result != None:
                return result
        if second != None:
            result = second.find_first(predicate, inverted)
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
    @classmethod
    def from_string(cls, expression_string:str, expected_string:str, solution_function: Callable[['BinExpTree'],bool]) -> 'BinExpTree':
        root = BinExpNode.from_string(expression_string)
        return BinExpTree(root, BinExpNode.from_string(expected_string), solution_function)

    def __init__(self, root:BinExpNode, expected:BinExpNode, solution_function) -> None:
        self.root = root
        self.subexpressions = self.root.calculate_subexpressions()
        self.expected = expected
        self.eta_level = len(root.find_all(lambda x: x.is_atomic() and re.search("^f[1-9][0-9]*$",x.content)))
        self.leaves = self.root.find_all(lambda x: x.is_atomic())
        self.string = str(self.root)
        self.solution_function = solution_function

    def clone(self, new_root:BinExpNode) -> 'BinExpTree':
        return BinExpTree(new_root, self.expected, self.solution_function)

    def __str__(self):
        return self.string

    def __repr__(self):
        return self.__str__()
    
    def __hash__(self):
        return self.root.__hash__()
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BinExpTree):
            raise ValueError("Invalid comparison")
        return self.root == other.root and self.expected == other.expected
    
    def replace(self, old: BinExpNode, replacement: BinExpNode) -> 'BinExpTree':
        target_index = index_of_pointer(self.subexpressions, old)
        if target_index == -1: raise ValueError("Old expression not found")
        elif target_index == 0:
            return self.clone(replacement.copy())
        else:
            new_exp_root = self.root.copy()
            target = new_exp_root.calculate_subexpressions()[target_index]

            replacement_copy = replacement.copy(parent=target.parent)
            if old is old.parent.f:
                target.parent.f = replacement_copy
            elif old is old.parent.arg:
                target.parent.arg = replacement_copy
            return self.clone(new_exp_root)

    def is_solution(self):
        return self.solution_function(self)

    def is_solution_equivalence(node: 'BinExpTree') -> bool:
        return node.root == node.expected
    
    def is_solution_point_free(node: 'BinExpTree') -> bool:
        return node.eta_level == 0
    
    def is_solution_simple(node: 'BinExpTree') -> bool:
        return node.root.is_simple()
    
    def is_solution_lambda(node: 'BinExpTree') -> bool:
        return len(node.leaves) == node.eta_level


def print_transformation(node: 'BinExpNode', marked_nodes: list['BinExpNode']) -> str:
        if any([node is mn for mn in marked_nodes]):
            return '-' * len(str(node))
        else:
            if node.is_atomic():
                return ' ' * len(node.content)
            else:
                if node.parent == None or node.parent.f is node:
                    return f"{print_transformation(node.f, marked_nodes)} {print_transformation(node.arg, marked_nodes)}"
                else:
                    return f" {print_transformation(node.f, marked_nodes)} {print_transformation(node.arg, marked_nodes)} "

class BinSearchNode(Node):
    def __init__(self, state: BinExpTree, actions: list[tuple[Callable, str]], filters: list[Callable], parent:'BinSearchNode'=None, action:str=None, cost=0, comparator=None, marked_nodes: list[BinExpNode] = []):
        super().__init__(state, parent, action, cost, comparator)
        assert state.expected is not None
        self.actions = actions
        self.filters = filters
        self.marked_nodes = marked_nodes
    
    def from_strings(original: str, expected: str, actions: list[tuple[Callable, str]], filters: list[tuple[Callable]], solution_function : Callable[[BinExpTree],bool]) -> 'BinSearchNode':
        return BinSearchNode(BinExpTree.from_string(original, expected, solution_function), actions, filters)
    
    def __str__(self) -> str:
        return str(self.state)

    def __repr__(self) -> str:
        return self.__str__()

    def expand(self):
        if (self.cost > 200):
            return []
        expanded_nodes = [BinSearchNode(result, self.actions, self.filters, self, action_name, self.cost+1, self.comparator, marked_nodes) for action, action_name in self.actions for result, marked_nodes in action(self.state)]
        return [n for n in expanded_nodes if all([filter(n) for filter in self.filters])]

    def get_path(self):
        path = []
        current = self
        while current is not None:
            path.insert(0, current)
            current = current.parent
        return path

    def __hash__(self) -> int:
        return self.state.__hash__()
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BinSearchNode):
            raise ValueError("Invalid comparison")
        return self.state == other.state
    
    def print_step(self, step:int, justify:int = 0):
        if self.parent is not None:
            transformation = print_transformation(self.parent.state.root, self.marked_nodes)
            print(f"  {transformation.ljust(max(justify, len(transformation)), ' ')}\t[{step}] {self.action}")
            print("=")
            print(f"  {str(self.state)}")
        else:
            print(f"  {str(self.state)}")


    def print_trace(node: 'BinSearchNode'):
        path = node.get_path()
        justify = max(len(str(n.state)) for n in path)
        for i, node in enumerate(path):
            node.print_step(i,justify)
        print(len(path) - 1)

def end_with_eta(node : BinSearchNode):
    leafs = node.state.root.find_all(lambda x: x.is_atomic())
    return all([not x.is_eta_parameter() or y.is_eta_parameter() for x,y in zip(leafs, leafs[1:])])

class Heuristics:
    def point_free(node: BinSearchNode) -> float:
        if node.state.eta_level == 0:
            return 0
        else:
            last_eta_parameter = node.state.root.find_first(lambda x: x.is_eta_parameter(node.state.eta_level), inverted=True)
            eta_depth = last_eta_parameter.depth() - 1
            return node.state.eta_level + (eta_depth / (eta_depth + 1))


    def point_free2(node: BinSearchNode) -> float:
        if node.state.eta_level == 0:
            return 0
        else:
            last_eta_parameter = node.state.root.find_first(lambda x: x.is_eta_parameter(node.state.eta_level), inverted=True)
            last2_eta_parameter = node.state.root.find_first(lambda x: x.is_eta_parameter(node.state.eta_level-1), inverted=True)
            eta_depth = last_eta_parameter.depth() - 1
            eta2_depth = last2_eta_parameter.depth() - 1 if last2_eta_parameter != None else 0
            return node.state.eta_level + (eta_depth / (eta_depth + 1)) * 0.5 + (eta2_depth / (eta2_depth + 1)) * 0.5
            

    def complexity(node: BinSearchNode) -> float:
        return str(node.state).count('(')

    def equivalence_count(node: BinSearchNode) -> float:
        return abs(len(node.state.root.find_all(lambda x: True)) - len(node.state.expected.find_all(lambda x: True)))

    def expanded_lambda(node: BinSearchNode) -> float:
        return len(node.state.leaves) - node.state.eta_level


class Actions:
    def equivalent_replace(exp1: BinExpNode, exp2: BinExpNode):
        def replace(tree: BinExpTree) -> list[(BinExpTree, list[BinExpNode])]:
            occurrences = tree.root.find_all(lambda x: x == exp1)
            return [(tree.replace(o, exp2), [o]) for o in occurrences]
        return replace, f"{exp1} -> {exp2}"

    def parametrized_replace(exp1: BinExpNode, exp2: BinExpNode):
        def replace(tree: BinExpTree) -> list[(BinExpTree, list[BinExpNode])]:
            occurrences = tree.root.find_all(lambda x: x.shape_like(exp1, {}))
            result = []
            for o in occurrences:
                params = {}
                if not o.shape_like(exp1, params):
                    raise ValueError("Invalid replacement")
                replacement = exp2.copy()
                replacement.replace_arguments(params)
                result.append((tree.replace(o, replacement), [v for v in params.values()]))
            return result
        return replace, f"{exp1} -> {exp2}"
 
    def eta_add_replace(tree: BinExpTree) -> list[(BinExpTree, list[BinExpNode])]:
        eta_level = tree.eta_level
        if eta_level < 30:
            new_arg = BinExpNode(content=f"f{eta_level+1}")
            new_root = BinExpNode(f=tree.root.copy(), arg=new_arg)
            return [(tree.clone(new_root), [tree.root])]
        return []
    ETA_ADD = (eta_add_replace, "eta add")
    

    def eta_remove_replace(tree: BinExpTree) -> list[(BinExpTree, list[BinExpNode])]:
        eta_level = tree.eta_level
        if eta_level >= 1 and tree.root.arg.is_eta_parameter():
            return [(tree.clone(tree.root.f.copy()), [tree.root.arg])]
        return []
    ETA_REMOVE = (eta_remove_replace, "eta remove")

    def simetric_rule(rule_generator, exp1: BinExpNode, exp2: BinExpNode):
        return [rule_generator(exp1, exp2), rule_generator(exp2, exp1)]
    
    def cn_replace(n: int):
        return Actions.simetric_rule(Actions.equivalent_replace, BinExpNode.from_string(f"c{n}"), BinExpNode.from_string(f"c1 {'c1' * (n-1)}"))
    
    def hn_replace(n: int):
        assert n >= 1
        return Actions.simetric_rule(Actions.parametrized_replace, BinExpNode.from_string(f"h{n} $1 $2 " + " ".join([f"f{i+3}" for i in range(n)])), BinExpNode.from_string(f"$1 ($2 " + " ".join([f"${i+3}" for i in range(n)]) +")"))
    
    def vn_replace(n: int):
        assert n >= 1
        expression = f"${n+1} ${n+2}"
        for i in range(n, 0, -1):
            expression = f"${i} ({expression})"
        return Actions.simetric_rule(Actions.parametrized_replace, BinExpNode.from_string(f"v{n} $1 $2 " + " ".join([f"f{i+3}" for i in range(n)])), BinExpNode.from_string(expression))
        
    C1_EVAL = simetric_rule(parametrized_replace, BinExpNode.from_string(f"c1 $1 $2 $3"), BinExpNode.from_string(f"$1 ($2 $3)"))



def EquivalenceSearchNode(expression_string:str, expected_string:str) -> BinSearchNode:
    actions = []
    actions += [r for i in range(2,10) for r in Actions.cn_replace(i)]
    actions += [Actions.ETA_ADD, Actions.ETA_REMOVE]
    actions += Actions.C1_EVAL
    # actions += simetric_rule(parametrized_replace,BinExpNode.from_string("c1 c1 $1 $2 $3 $4"), BinExpNode.from_string("$1 $2 ($3 $4)"))[1:2]
    # actions += simetric_rule(parametrized_replace,BinExpNode.from_string("c1 c1 c1 $1 $2 $3 $4"), BinExpNode.from_string("$1 ($2 $3 $4)"))[1:2]
    return BinSearchNode.from_strings(expression_string, expected_string, actions, [], BinExpTree.is_solution_equivalence)
    

def PointFreeSearchNode(expression_string:str) -> BinSearchNode:
    actions = [] 
    actions += [Actions.ETA_REMOVE]
    actions += Actions.C1_EVAL[1:2]
    return BinSearchNode.from_strings(expression_string, expression_string, actions, [], BinExpTree.is_solution_point_free)

def LambdaSearchNode(expression_string:str) -> BinSearchNode:
    actions = [] 
    actions += [Actions.ETA_ADD]
    actions += Actions.C1_EVAL[:1]
    return BinSearchNode.from_strings(expression_string, expression_string, actions, [], BinExpTree.is_solution_lambda)

Actions.vn_replace(1)