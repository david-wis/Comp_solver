from search_methods import bfs, dfs, greedy, astar
from binexptree import BinExpTree, BinSearchNode
from datetime import datetime
def asoc(expression_string : str) -> str:
    result = ""
    count = 1
    for i,c in enumerate(expression_string):
        if c == '.':
            result += f"{' ' if len(result) > 1 and result[-1] == ')' else ''}f{str(count)}{' ' if i < len(expression_string) - 1 else ''}"
            count += 1
        elif c == '(':
            result += "("
        elif c == ')':
            if result[-1] == " ":
                result = result[:-1] + ")"
            else:
                result += ")"
    return result

def vc(n):
    expression = ".."
    for i in range(n):
        expression = f".({expression})"
    return asoc(expression)

def hc(n):
    return asoc(f".(.{'.'*n})")

def end_with_eta(node : BinSearchNode):
    leafs = node.state.root.find_all(lambda x: x.is_atomic())
    return all([not x.is_eta_parameter() or y.is_eta_parameter() for x,y in zip(leafs, leafs[1:])])

def search_path(expression, search_method, heuristic, print_trace=False):
    t = datetime.now()
    initial_node = BinSearchNode(BinExpTree.from_string(expression, "c8", BinExpTree.is_solution_eta_level))
    # print(initial_node)
    solution, _, _ = search_method(initial_node, h=heuristic, predicate=end_with_eta, print_current=print_trace)
    # BinSearchNode.print_trace(solution)
    print(datetime.now() - t)
    return solution

def generate_lambda(expression, search_method, heuristic, print_trace=False):
    t = datetime.now()
    initial_node = BinSearchNode(BinExpTree.from_string(expression, "c8", BinExpTree.is_solution_reverse_eta))
    # print(initial_node)
    solution, _, _ = search_method(initial_node, h=heuristic, predicate=end_with_eta, print_current=print_trace)
    # BinSearchNode.print_trace(solution)
    print(datetime.now() - t)
    return solution
    
if __name__ == '__main__':
    pass