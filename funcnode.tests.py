from funcnode import FuncExpNode, TreeTransformation
from search_methods import bfs, dfs, greedy, astar
from heuristics import by_funcnode_length
from utils import normalize_expression

search = dfs.search

def display(initial_node, solution):
    print(f"Solution length: {len(solution.get_sequence())}")
    seq = solution.get_sequence()
    prev_state = initial_node.state
    # print(initial_exp)
    for t in seq:
        next_exp, curr_underline = t.get_styled(prev_state)
        print("=\n" if t is not seq[0] else '', 
              next_exp, 
              "\n", 
              f"{curr_underline} \t\t{t.description}")
        prev_state = t.result
    print("=\n", initial_node.state.expected)

    initial_node = FuncExpNode.from_expressions("c1 (c1 (c1 c1))", "c8")
    solution, _, _ = greedy.search(initial_node, by_funcnode_length)


def test_funcnode():
    initial_node = FuncExpNode.from_expressions("c2 c2", "c6")
    solution, _, _ = search(initial_node)
    assert solution is not None

    initial_node = FuncExpNode.from_expressions("c2 (c1 c1)", "c5 c1")
    solution, _, _ = search(initial_node)
    assert solution is not None

    initial_node = FuncExpNode.from_expressions("c5 c1", "c2 (c1 c1)")
    solution, _, _ = search(initial_node)
    assert solution is not None

    initial_node = FuncExpNode.from_expressions("c1 c2", "c4")
    solution, _, _ = search(initial_node)
    assert solution is not None

    initial_node = FuncExpNode.from_expressions("c4", "c1 c2")
    solution, _, _ = search(initial_node)
    assert solution is not None

    initial_node = FuncExpNode.from_expressions("c5", "c1 c2")
    solution, _, _ = search(initial_node)
    assert solution is None

    initial_node = FuncExpNode.from_expressions("c1 (c1 c1)", "c1 c1 c1 c1")
    solution, _, _ = search(initial_node)
    assert solution is not None

    initial_node = FuncExpNode.from_expressions("c1 (c1 c1)", "c3")
    solution, _, _ = search(initial_node)
    assert solution is None

    initial_node = FuncExpNode.from_expressions("c1 c4", "c2 c3 c1") 
    solution, _, _ = search(initial_node)
    assert solution is not None 

    initial_node = FuncExpNode.from_expressions("c2 c3 c1", "c1 c4") 
    solution, _, _ = search(initial_node)
    assert solution is not None 

    initial_node = FuncExpNode.from_expressions("c2 c3 c1", "c5") 
    solution, _, _ = search(initial_node)
    assert solution is None 

    initial_node = FuncExpNode.from_expressions("c1 c3", "c7") 
    solution, _, _ = search(initial_node)
    assert solution is not None 

    initial_node = FuncExpNode.from_expressions("c1 c3", "c8") 
    solution, _, _ = search(initial_node)
    assert solution is None 

    initial_node = FuncExpNode.from_expressions("c8", "c1 (c1 c1) c1 c1 c1 c1") 
    solution, _, _ = search(initial_node)
    assert solution is not None 

    initial_node = FuncExpNode.from_expressions("c1 (c1 c1) c1 c1 c1 c1", "c1 c1 c1 c1 c1 c1 c1 c1") 
    solution, _, _ = search(initial_node)
    assert solution is not None 

    initial_node = FuncExpNode.from_expressions("c1 (c1 c2 (c4 c3)) (c1 c1) c2", "c1 c2 (c4 c3) (c1 c1 c2)") 
    solution, _, _ = greedy.search(initial_node, by_funcnode_length)
    assert solution is not None 

    initial_node = FuncExpNode.from_expressions("c2 c3", "c8", True)
    solution, _, _ = greedy.search(initial_node, by_funcnode_length)
    assert solution is not None

    initial_node = FuncExpNode.from_expressions("c1 (c1 (c1 c1))", "c9")
    solution, _, _ = greedy.search(initial_node, by_funcnode_length)
    assert solution is not None

    initial_node = FuncExpNode.from_expressions("c9", "c1 (c1 (c1 c1))")
    solution, _, _ = greedy.search(initial_node, by_funcnode_length)
    assert solution is not None
    # display(initial_node, solution)

    initial_node = FuncExpNode.from_expressions("c6", "c10", True)
    solution, _, _ = bfs.search(initial_node)
    assert solution is not None
    display(initial_node, solution)


if __name__ == "__main__":
    test_funcnode()
    print("All tests passed")