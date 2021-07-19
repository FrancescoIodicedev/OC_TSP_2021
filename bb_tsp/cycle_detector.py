# detect cycles in a graph

def findNewCycles(path, G, cycles):
    start_node = path[0]
    next_node= None
    sub = []

    #visit each edge and each node of each edge
    for edge in G:
        node1, node2 = edge
        if start_node in edge:
            if node1 == start_node:
                next_node = node2
            else:
                next_node = node1
            if not visited(next_node, path):
                # neighbor node not on path yet
                sub = [next_node]
                sub.extend(path)
                # explore extended path
                findNewCycles(sub, G, cycles)
            elif len(path) > 2  and next_node == path[-1]:
                # cycle found
                p = rotate_to_smallest(path);
                inv = invert(p)
                if isNew(p, cycles) and isNew(inv, cycles):
                    cycles.append(p)


def invert(path):
    return rotate_to_smallest(path[::-1])


#  rotate cycle path such that it begins with the smallest node
def rotate_to_smallest(path):
    n = path.index(min(path))
    return path[n:]+path[:n]


def isNew(path, cycles):
    return not path in cycles


def visited(node, path):
    return node in path

####################
# SUPPORT Function #
####################

# convert list of LP variable in list of edge
def convert_to_edge_list(solution):
    edge_list = list()
    for var in solution:
        i, j = vertex_in_edge(var)
        edge_list.append((i, j))
    return edge_list


def vertex_in_edge(edge):
    i = (edge.name.split('('))[1].split(',')[0]
    j = (edge.name.split(',_'))[1].split(')')[0]
    return int(i), int(j)

def get_cycles(G):
    cycles = []
    for edge in G:
        for node in edge:
            findNewCycles([node], G, cycles)
    edge_list = post_processing(cycles[0])
    return edge_list


# From [a,b,c,d] to [[a,b][b,c][c,d][d,a]]
def post_processing(cycles):
    edge_list = []
    for i in range(len(cycles)):
        if i == len(cycles)-1:
            edge_list.append([cycles[i], cycles[0]])
        else:
            edge_list.append([cycles[i], cycles[i+1]])

    # Sorting
    for edge in edge_list:
        edge.sort()

    return edge_list


if __name__ == '__main__':
    graph = [[1, 2], [1, 3], [1, 4], [2, 3], [3, 4], [2, 6], [4, 6], [8, 7], [8, 9], [9, 7]]
    cycles = []

    for edge in graph:
        for node in edge:
            findNewCycles([node], graph, cycles)

    for cy in cycles:
        path = [str(node) for node in cy]
        s = ",".join(path)
        print(s)