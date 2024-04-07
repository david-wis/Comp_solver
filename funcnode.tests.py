from funcnode import FuncExpNode
from search_methods import dfs
from search_methods import greedy
from heuristics import by_funcnode_length

search = dfs.search

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

if __name__ == "__main__":
    test_funcnode()
    print("All tests passed")