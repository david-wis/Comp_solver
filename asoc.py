from search_methods import bfs, dfs, greedy, astar
from binexptree import BinExpTree, BinSearchNode

def asoc(expression_string : str) -> str:
    result = ""
    count = 1
    for c in expression_string:
        if c == '.':
            result += f"f{str(count)} "
            count += 1
        elif c == '(':
            result += "("
        elif c == ')':
            if result[-1] == " ":
                result = result[:-1] + ")"
            else:
                result += ")"
    return result


if __name__ == '__main__':
    initial_node = BinSearchNode(BinExpTree.from_string(asoc(".(..)"), "c8", BinExpTree.is_solution_eta_level))
    heuristic = lambda x: x.state.eta_level + (not (x.state.root.arg != None and x.state.root.arg.is_eta_parameter()))
    solution, _, _ = greedy.search(initial_node, h=heuristic)
    current_state = initial_node.state
    BinSearchNode.print_trace(solution)
