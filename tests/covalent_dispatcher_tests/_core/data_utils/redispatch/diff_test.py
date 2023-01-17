import networkx as nx

from covalent_dispatcher._core.data_utils.redispatch.diff import compare_transport_graphs, max_cbms


def test_max_cbms():
    """Test function for determining a largest cbms"""

    A = nx.MultiDiGraph()
    B = nx.MultiDiGraph()
    C = nx.MultiDiGraph()
    D = nx.MultiDiGraph()

    #    0     5  6
    #  /  \
    # 1    2
    A.add_edge(0, 1)
    A.add_edge(0, 2)
    A.nodes[1]["color"] = "red"
    A.add_node(5)
    A.add_node(6)

    #    0     5
    #  /  \\
    # 1    2
    B.add_edge(0, 1)
    B.add_edge(0, 2)
    B.add_edge(0, 2)
    B.nodes[1]["color"] = "black"
    B.add_node(5)

    #    0    3
    #  /  \  /
    # 1    2
    C.add_edge(0, 1)
    C.add_edge(0, 2)
    C.add_edge(3, 2)

    #    0    3
    #  /  \  /
    # 1    2
    #     /
    #   4
    D.add_edge(0, 1)
    D.add_edge(0, 2)
    D.add_edge(3, 2)
    D.add_edge(2, 4)

    A_node_status, B_node_status = max_cbms(A, B)
    assert A_node_status == {0: True, 1: False, 2: False, 5: True, 6: False}
    assert B_node_status == {0: True, 1: False, 2: False, 5: True}

    A_node_status, C_node_status = max_cbms(A, C)
    assert A_node_status == {0: True, 1: False, 2: False, 5: False, 6: False}
    assert C_node_status == {0: True, 1: False, 2: False, 3: False}

    C_node_status, D_node_status = max_cbms(C, D)
    assert C_node_status == {0: True, 1: True, 2: True, 3: True}
    assert D_node_status == {0: True, 1: True, 2: True, 3: True, 4: False}


def test_compare_transport_graphs():
    """Test method for computing reusable nodes from another transport graph"""
    import covalent as ct

    @ct.electron
    def task_1(x):
        return x

    @ct.electron
    def task_2(x):
        return 2 * x

    @ct.electron
    def task_2a(x, y):
        return x + y

    @ct.electron
    def task_3(x):
        return 3 * x

    #  1 -> 0
    @ct.lattice
    def workflow_1(x):
        res1 = task_1(x)
        return res1

    # 1 -> 0 -> 2
    @ct.lattice
    def workflow_2(x):
        res1 = task_1(x)
        res2 = task_2(res1)
        return res2

    # 1 -> 0 -> 2
    @ct.lattice
    def workflow_3(x):
        res1 = task_1(x)
        res2 = task_3(res1)
        return res2

    #      1  2   5
    #     /    \ /
    #    0      3
    #  /
    # 4
    @ct.lattice
    def workflow_4(x, y, z):
        res1 = task_1(x)
        res2 = task_1(y)
        res3 = task_2(res1)
        res4 = task_2a(res2, z)

    return 1

    workflow_1.build_graph(5)
    workflow_2.build_graph(5)
    workflow_3.build_graph(5)

    tg1 = workflow_1.transport_graph
    tg2 = workflow_2.transport_graph
    tg3 = workflow_3.transport_graph

    assert compare_transport_graphs(tg1, tg2) == [0, 1]
    assert compare_transport_graphs(tg2, tg2) == [0, 1, 2]
    assert compare_transport_graphs(tg2, tg3) == [0, 1]

    workflow_3.build_graph(2)
    tg3 = workflow_3.transport_graph
    assert compare_transport_graphs(tg2, tg3) == []

    workflow_4.build_graph(1, 2, 3)
    tg4_1 = workflow_4.transport_graph
    workflow_4.build_graph(1, 2, 4)
    tg4_2 = workflow_4.transport_graph
    workflow_4.build_Graph(1, 3, 3)
    tg4_3 = workflow_4.transport_graph

    assert compare_transport_graphs(tg4_1, tg4_2) == [0, 1, 2, 4]
    assert compare_transport_graphs(tg4_1, tg4_3) == [0, 1, 4]
