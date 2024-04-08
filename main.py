import numpy as np
import sys
import json
from comp import (
    CompositionNode, CompositionState 
)
from search_methods import bfs, dfs, greedy, astar
from functools import partial
from datetime import datetime
import os
import heuristics as h
from funcnode import FuncExpNode
from utils import normalize_expression

methods = {
    "dfs": dfs.search,
    "bfs": bfs.search,
    "greedy": greedy.search,
    "A*": astar.search
}
heuristics = {
    "by_length": h.by_length,
    "by_constant_weight": h.by_constant_weight,
    "by_funcnode_length": h.by_funcnode_length
}

# heuristics = {
#     "euclidean": partial(d_heuristic, distance_function=euclidean_distance),
#     "euclidean+p": euclidean_heuristic, 
#     "manhattan": partial(d_heuristic, distance_function=manhattan_distance),
#     "manhattan+p": manhattan_heuristic,
#     "mod_manhattan+p": partial(mdp_heuristic, distance_function=manhattan_distance),
#     "max_manhattan+p": max_heuristic(manhattan_heuristic, partial(mdp_heuristic, distance_function=manhattan_distance))
# }

search = methods["bfs"]
heuristic = heuristics["by_funcnode_length"]

def verify_correctness(seq):
    print(f"\nTest the types in ghci:")
    for t in seq:
        print(f":t {t.result.infix()}")

    
    


def single_funcnode():
    initial_node = FuncExpNode.from_expressions("c6", "c10", True)

    begin_time = datetime.now()
    (solution, visited, border) = search(initial_node, heuristic)
    finish_time = datetime.now()

    print(f"visited nodes = {len(visited)}")

    print(f"border = {len(border)}")
    print("Time = ", finish_time - begin_time)
    if solution is None:
        print("No solution found")
        return
    print(f"cost = {solution.cost} ")
    print(f"solution length = {len(solution.get_sequence())}")
    seq = solution.get_sequence()
    # print(f"Solution:\n", "\n".join(map(lambda x: f"=\t\t\t\t{x[0]}\n{normalize_expression(x[1])}", seq)))
    print("length: ", len(seq))
    verify_correctness(seq)

def single():
    initial_state = CompositionState("c8", "c2 c3")

    initial_node = CompositionNode(initial_state, None, None, 0)

    begin_time = datetime.now()
    (solution, visited, border) = search(initial_node, heuristic)
    finish_time = datetime.now()


    print(f"visited nodes = {len(visited)}")
    print(f"border = {len(border)}")
    print("Time = ", finish_time - begin_time)
    if solution is None:
        print("No solution found")
        return
    print(f"cost = {solution.cost} ")
    print(f"solution length = {len(solution.get_sequence())}")
    seq = solution.get_sequence()
    print(f"Solution:\n{initial_state.exp}\n", "\n".join(map(lambda x: f"=\t\t\t\t{x[0]}\n({x[1]})", seq)))
    print("lenght: ", len(seq))
    verify_correctness(seq)


if __name__ == "__main__":
    single_funcnode()
