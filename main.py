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

methods = {
    "dfs": dfs.search,
    "bfs": bfs.search,
    "greedy": greedy.search,
    "A*": astar.search
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

def verify_correctness(seq):
    print(f"\nTest the types in ghci:")
    for (_, exp) in seq:
        print(f":t {exp}")

    
    



def single():
    initial_state = CompositionState("c12", "c8")

    initial_node = CompositionNode(initial_state, None, None, 0)

    begin_time = datetime.now()
    (solution, visited, border) = search(initial_node)
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
    verify_correctness(seq)



if __name__ == "__main__":
    single()
