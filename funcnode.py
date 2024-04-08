from utils import get_token, get_parameters_subexpressions
from search_methods.node import Node

# c_n c_1 -> c_n+1
def cn_definition(tree: 'FuncExpTree'):
    if tree.root_is_cn() and tree.is_parent() and tree.args[0].f == "c1" and tree.args[0].is_atomic():
        tree_copy = tree.copy()
        tree_copy.args.pop(0)
        tree_copy.f = f"c{int(tree.f[1:]) + 1}"

        transformation = TreeTransformation(tree_copy, tree, f"def {tree_copy.f}")
        return [transformation]
    return [] 

# c_n+1 -> c_n c_1       
def cn_inverse_definition(tree: 'FuncExpTree'):
    if not tree.root_is_cn():
        return []

    number = int(tree.f[1:])
    if number > 1: 
        tree_copy = tree.copy()
        tree_copy.f = f"c{number - 1}"
        tree_copy.args = [FuncExpTree(f="c1", level=tree_copy.level+1)] + tree_copy.args

        transformation = TreeTransformation(tree_copy, tree, f"def {tree.f}")
        return [transformation]
    return []

# a (b c) x -> c1 a b c x
def c1_inverse_apply(tree: 'FuncExpTree'):
    if tree.is_atomic():
        return []

    variants = []
    for i, child in enumerate(tree.args):
        if child.is_parent():
            a = tree.copy()
            b = a.args[i]
            c = b.args.pop()
            x = a.args[i+1:]
            a.args = a.args[:i]
            new_args = [a, b, c] + x


            new_node = FuncExpTree(f="c1", level=a.level, expected=a.expected)
            new_node.args = new_args

            a.level += 1
            c.level -= 1

            transformation = TreeTransformation(new_node, tree, f"def c1 (inv apply)")
            variants.append(transformation) 
    return variants

# c1 a b c x -> a (b c) x
def c1_apply(tree: 'FuncExpTree'):
    if tree.is_atomic():
        return []

    if tree.f == "c1" and len(tree.args) >= 3:
        tree_copy = tree.copy()
        a = tree_copy.args[0]
        b = tree_copy.args[1]
        c = tree_copy.args[2]
        x = tree_copy.args[3:]

        a.args.append(b)
        b.args.append(c)
        a.args.extend(x)

        a.level -= 1
        c.level += 1

        a.expected = tree.expected

        transformation = TreeTransformation(a, tree, f"def c1 (apply)")
        return [transformation]
    return []

def get_last_variable_name(tree: 'FuncExpTree'):
    infix_exp = tree.infix() 
    return max(filter(lambda e: e[0] == 'f', infix_exp.replace('(', '').replace(')', '').split(' ')), key=lambda e: int(e[1:]), default=None)

MAX_ETA = 1

def eta(tree: 'FuncExpTree'):
    if tree.is_atomic():
        return []
    
    options = []
    last_var = get_last_variable_name(tree)

    # Remove eta
    if last_var is not None and tree.args[-1].f == last_var and tree.args[-1].is_atomic(): 
        tree_copy = tree.copy()
        tree_copy.args.pop()

        transformation = TreeTransformation(tree_copy, tree, f"eta (remove)")
        options.append(transformation)
    
    max_eta_app = int(last_var[1:]) if last_var is not None else 0
    if max_eta_app >= MAX_ETA:
        return options
    # Add eta
    next_var = f"f{max_eta_app + 1}" if last_var is not None else "f1"
    tree_copy = tree.copy()
    tree_copy.args.append(FuncExpTree(f=next_var, level=tree.level+1))    

    transformation = TreeTransformation(tree_copy, tree, f"eta (add)")
    options.append(transformation)

    return options

known_actions = [cn_definition, cn_inverse_definition, c1_apply, c1_inverse_apply]

class TreeTransformation(object):
    def __init__(self, result: 'FuncExpTree', original_subtree: 'FuncExpTree', description: str):
        self.original_subtree = original_subtree
        self.result = result
        self.description = description
        self.prefix_value = "" 
        self.underline = ""
        self.symbol = ' '
        self.coloring = False
    
    def get_styled_infix(self, tree: 'FuncExpTree'):
        if tree is self.original_subtree:
            self.coloring = True
            self.symbol = '-'

        if tree.is_atomic():
            self.prefix_value += f"{tree.f}"
            self.underline += self.symbol * len(tree.f)
        else:
            self.prefix_value += f"({tree.f} "
            self.underline += self.symbol * (len(tree.f)+2)

            for arg in tree.args:
                self.get_styled_infix(arg) 
                if arg is not tree.args[-1]:
                    self.prefix_value += " "
                    self.underline += self.symbol

            self.prefix_value = self.prefix_value + ")"
            self.underline += self.symbol

        if tree is self.original_subtree and self.coloring:
            self.coloring = False
            self.symbol = ' '

        return self.prefix_value, self.underline
        




class FuncExpTree(object):
    def __init__(self, f, arg_tokens=[], level=0, expected=None):
        self.f = f
        self.args = [ FuncExpTree.parse(arg, level = level+1, expected=None) for arg in arg_tokens]
        self.level = level
        self.infix_val = None # Infix cache 
        self.expected = expected

    def is_solution(self):
        return self.expected is not None and self.infix() == f"{self.expected}"
    
    def __hash__(self) -> int:
        return hash(self.infix())
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FuncExpTree):
            return False
        return self.infix() == other.infix()
    
    def root_is_cn(self):
        return self.f[0] == 'c'

    def infix(self):
        # if self.infix_val is not None:
        #     return self.infix_val

        self.infix_val = f"({self.f} {' '.join([arg.infix() for arg in self.args])})" if self.is_parent() else f"{self.f}"
        return self.infix_val

    def parse(s: str, expected: str, level: int = 0) -> 'FuncExpTree':
        if s[0] == '(':
            s = s[1:-1]
        token, _, current_idx = get_token(s, 0)
        args = get_parameters_subexpressions(s[current_idx+1:])
        node = FuncExpTree(f = token, arg_tokens= args, level = level, expected = expected) 
        return node
    
    def __str__(self):
        output = self.f
        for arg in self.args:
            output += "\n" + "   "*arg.level + "->" + str(arg)
        return output
    
    def __repr__(self):
        return self.f
    
    def is_parent(self) -> bool:
        return len(self.args) > 0
    
    def is_atomic(self) -> bool:
        return not self.is_parent()
    
    def copy(self):
        tree_copy = FuncExpTree(f = self.f, level = self.level, expected=self.expected)
        tree_copy.args = [arg.copy() for arg in self.args]
        return tree_copy
    
    def copy_replacing_child(self, index, child):
        tree_copy = FuncExpTree(f = self.f, level = self.level, expected=self.expected)
        tree_copy.args = [child if i == index else arg.copy() for i, arg in enumerate(self.args)]
        return tree_copy
    
    def get_next_transformations(self):
        # Actions that can be applied to the current tree
        transformations = [trans for action in known_actions for trans in action(self)] 
        
        # Actions that can be applied to the children of the current tree
        for i, arg in enumerate(self.args):
            for trans in arg.get_next_transformations():
                trans.result = self.copy_replacing_child(i, trans.result)
                transformations.append(trans)

        return transformations 

class FuncExpNode(Node):
    def __init__(self, state: FuncExpTree, parent=None, action=None, cost=0, comparator=None, eta_enabled=False):
        super().__init__(state, parent, action, cost, comparator)
        self.eta_enabled = eta_enabled
        assert state.expected is not None
    
    def from_expressions(original: str, expected: str, eta_enabled = False):
        if (expected[0] != '(' or expected[-1] != ')') and ' ' in expected:
            expected = f"({expected})"  
        return FuncExpNode(FuncExpTree.parse(original, expected, 0), eta_enabled=eta_enabled)

    def __hash__(self) -> int:
        return hash(self.state.infix())

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FuncExpNode):
            return False
        return self.state == other.state
    
    def __repr__(self) -> str:
        return f"{str(self.state)}\n{self.action}" 

    def expand(self):
        if (self.cost > 200):
            return []

        expanded_nodes = [FuncExpNode(trans.result, self, trans, self.cost + 1, self.comparator, self.eta_enabled) for trans in self.state.get_next_transformations()]   

        # eta
        if self.eta_enabled:
            expanded_nodes.extend([FuncExpNode(trans.result, self, trans, self.cost + 1, self.comparator, self.eta_enabled) for trans in eta(self.state)])

        return expanded_nodes 

    def get_sequence(self):
        sequence = []
        current = self
        while current is not None and current.action is not None:
            sequence.insert(0, current.action)
            current = current.parent
        return sequence

if __name__ == "__main__":
    # print('\nestilo 1')
    # t1 = FuncExpTree.parse("c1 c2 (c4 c3) (c1 c1 c2)", "")
    # print(t1)
    # print('\nestilo 2')
    # t2 = FuncExpTree.parse("c1 (c1 c2 (c4 c3)) (c1 c1) c2", "")
    # print(t2)
    node = FuncExpNode.from_expressions("c1 c2 (c4 c3) (c1 c1 c2)", "c1 (c1 c2 (c4 c3)) (c1 c1) c2")
    e = node.expand()   
    print('\n'.join(map(str, e)))


