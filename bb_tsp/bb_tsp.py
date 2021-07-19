import time
from matplotlib import pyplot as plt
import cycle_detector
from PNode import PNode
import copy
import numpy as np
from scipy.spatial.distance import pdist, squareform

proper_subsets_of_V = []
node_x = 1
nodes_generated = 0
inf = float('inf')


def power_set(s):
    power_set = [[]]
    for elem in s:
        for sub_set in power_set:
            power_set = power_set + [list(sub_set) + [elem]]
    return power_set


def branch(P, cycle):
    global nodes_generated
    subproblems = []
    for i, edge in enumerate(cycle):
        E_0, E_1 = [cycle[i]], cycle[:i]
        nodes_generated += 1
        P_i = PNode(copy.deepcopy(P.V), copy.deepcopy(P.E),
                    E_0=copy.deepcopy(P.E_0), E_1=copy.deepcopy(P.E_1),
                    name='P'+str(nodes_generated))
        P_i.update_E_set(E_0, E_1)
        P_i.build_LP_problem(proper_subsets_of_V)
        P_i.solve()
        if P_i.LB is not None:
            subproblems.append(P_i)
    return subproblems


def find_cycle(solution):
    one_tree_graph = cycle_detector.convert_to_edge_list(solution)
    cycle = cycle_detector.get_cycles(one_tree_graph)
    return cycle


def index_best_node(PNodes):
    index = 0
    best_LB = float('inf')
    for i in range(len(PNodes)):
        if PNodes[i].LB < best_LB:
            index, best_LB = i, PNodes[i].LB
    return index


def closed_open_node(PNodes, z):
    i = 0
    while i < len(PNodes):
        if PNodes[i].LB >= z:
            del PNodes[i]
        else:
            i += 1


def branch_and_bound_tsp(P):
    PNodes, h_cycle, z = [P], [], float('inf')
    P.solve()

    if P.is_hamilton_cycle():
        h_cycle = P.solution, z = P.LB

    while len(PNodes) > 0:
        P_i = PNodes.pop(index_best_node(PNodes))
        branch_nodes = branch(P_i, find_cycle(P_i.solution))
        for p_node in branch_nodes:
            if p_node.is_hamilton_cycle():
                if p_node.LB < z:
                    z, h_cycle = p_node.LB, p_node.solution
                    closed_open_node(PNodes, z)
            elif p_node.LB < z:
                PNodes.append(p_node)
    return z, h_cycle


def generate_tsp_problem(N, range):
    np.random.seed(1)
    V = list(np.arange(1,N+1))
    positions = np.random.randint(range, size=(N,2))
    E = squareform(pdist(positions, 'sqeuclidean')).astype(int)
    return V, E, positions


def plot_result(solution, positions):
    print('Hamiltonian cycle : {}'.format(solution))
    fig, ax = plt.subplots(2, sharex=True, sharey=True)
    ax[0].set_title('Full graph')
    ax[1].set_title('Optimal tour')

    ax[0].scatter(positions[:, 0], positions[:, 1])
    ax[1].scatter(positions[:, 0], positions[:, 1])

    for i in range(1, N+1):
        for j in range(1, N+1):
            if i < j:
                start_pos = positions[i-1]
                end_pos = positions[j-1]
                ax[0].annotate("",
                               xy=start_pos, xycoords='data',
                               xytext=end_pos, textcoords='data',
                               arrowprops=dict(arrowstyle="-",
                                               connectionstyle="arc3"))
    start_node = 1
    distance = 0.

    for i in range(1, N+1):
        start_pos = positions[start_node-1]
        next_node = get_next_node(solution, start_node)
        end_pos = positions[next_node-1]
        distance += np.linalg.norm(end_pos - start_pos)
        ax[1].annotate("",
                       xy=start_pos, xycoords='data',
                       xytext=end_pos, textcoords='data',
                       arrowprops=dict(arrowstyle="-",
                                       connectionstyle="arc3"))
        start_node = next_node

    textstr = "Nodes : %d\nc(z) : %.2f" % (N, distance)
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    ax[1].text(0.05, 0.95, textstr, transform=ax[1].transAxes, fontsize=8, # Textbox
               verticalalignment='top', bbox=props)

    plt.tight_layout()
    plt.show()


def get_next_node(solution, start_node):
    next_node = None
    for i, c in enumerate(solution):
        if c[0] == start_node:
            next_node = c[1]
            del solution[i]
            break
        if c[1] == start_node:
            next_node = c[0]
            del solution[i]
            break
    return next_node


if __name__ == '__main__':
    N = 9
    range_position = 15

    V, E, positions = generate_tsp_problem(N,range_position)
    P = PNode(V, E)
    proper_subsets_of_V = power_set(V)
    P.build_LP_problem(proper_subsets_of_V)

    start_time = time.time()
    z, solution = branch_and_bound_tsp(P)
    print("--- %s seconds ---" % (time.time() - start_time))
    print('Optimal Value of z = {}\nNodes generated in branching tree = {}'
          .format(z, nodes_generated))
    cycle = cycle_detector.convert_to_edge_list(solution)
    plot_result(cycle,positions)