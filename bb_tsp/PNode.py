from pulp import *


class PNode:
    def __init__(self, V, E, E_0=[], E_1=[], node_x=1, name=''):
        self.P = None
        self.V = V
        self.E = E
        self.E_0 = E_0
        self.E_1 = E_1
        self.node_x = node_x
        self.LB = float('inf')
        self.solution = []
        self.name = name

    def build_LP_problem(self, Proper_subsets_of_V):
        if self.node_x not in self.V:
            self.V.insert(0, self.node_x)

        self.P = LpProblem("1_tree", LpMinimize)
        x = LpVariable.dicts("x", [(i, j)
                                   for i in self.V
                                   for j in self.V
                                   if i < j], 0, 1, LpBinary)

        self.P += lpSum(self.E[i - 1, j - 1] * x[(i, j)]
                        for i in self.V
                        for j in self.V
                        if (i != j and i < j))

        # Adding constraint
        self.V.remove(self.node_x)
        self.P = self.add_constraint_1_tree(x, Proper_subsets_of_V)
        self.V.insert(0, self.node_x)

    def add_constraint_1_tree(self, x, proper_subset):
        # Constraint (1)
        self.P += lpSum(x[(self.node_x, j)] for j in self.V if self.node_x != j) == 2

        # (2)
        for S in proper_subset:
            # V / S
            V_S = list(set(self.V) - set(S))
            if 2 <= len(S) < len(self.V):
                #print(S)
                vector = []
                for i in S:
                    for j in V_S:
                        if i < j:
                            vector.append(x[(i, j)])
                        else:
                            vector.append(x[(j, i)])
                self.P += lpSum(vector) >= 1

        for edge in self.E_0:
            self.P += lpSum(x[(edge[0], edge[1])]) == 0
        for edge in self.E_1:
            self.P += lpSum(x[(edge[0], edge[1])]) == 1

        return self.P

    def common_data(self, E_0, E_1):
        result = False
        for x in E_0:
            for y in E_1:
                if x == y:
                    return True
        return result

    def solve(self):
        z, solution = None, None
        if not self.common_data(self.E_0, self.E_1):
            self.P.solve(PULP_CBC_CMD(msg=False))
            z, solution = self.P.objective.value(), list(filter(lambda x_ij: x_ij.value() == 1, self.P.variables()))
            self.solution = solution
            self.LB = z
        #print("z = {} \nx = {} \n".format(z, solution))

    def update_E_set(self, E_0, E_1):
        for v in E_0:
            if v not in self.E_0:
                self.E_0.append(v)
        for v in E_1:
            if v not in self.E_1:
                self.E_1.append(v)

        #print("E_0 : {} E_1 : {}".format(self.E_0, self.E_1))

    #
    # Procedure for check if solution is Hamiltonian Cycle
    #
    def is_hamilton_cycle(self):
        for v in self.V:
            degree_v = 0
            for edge in self.solution:
                if self.edge_contains_v(edge, v):
                    degree_v += 1
            if degree_v != 2:
                return False
        # every node has degree_v = 2
        print('Hamiltonian Cycle FOUND in subproblem {}'.format(self.name))
        return True

    def edge_contains_v(self, edge, v):
        i, j = self.vertex_in_edge(edge)
        return j == v or i == v

    def vertex_in_edge(self, edge):
        i = (edge.name.split('('))[1].split(',')[0]
        j = (edge.name.split(',_'))[1].split(')')[0]
        return int(i), int(j)
