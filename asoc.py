from search_methods import bfs, dfs, greedy, astar
from binexptree import BinExpTree, Heuristics, PointFreeSearchNode, LambdaSearchNode, EquivalenceSearchNode
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

def point_free(expression, search_method, heuristic, print_trace=False):
    t = datetime.now()
    initial_node = PointFreeSearchNode(expression)
    solution, _, _ = search_method(initial_node, h=heuristic, print_current=print_trace)
    # BinSearchNode.print_trace(solution)
    print(datetime.now() - t)
    return solution

def generate_lambda(expression, search_method, heuristic, print_trace=False):
    t = datetime.now()
    initial_node = LambdaSearchNode(expression)
    solution, _, _ = search_method(initial_node, h=heuristic, print_current=print_trace)
    # BinSearchNode.print_trace(solution)
    print(datetime.now() - t)
    return solution
    
if __name__ == '__main__':
    pass