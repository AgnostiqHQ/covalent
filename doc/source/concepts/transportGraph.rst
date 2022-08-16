.. _Transport graph:

~~~~~~~~~~~~~~~~
Transport graph
~~~~~~~~~~~~~~~~

After the workflow has been defined, and before it can be executed, one of the first steps performed by the dispatcher server is to construct a dependency graph of the tasks. This `directed acyclic graph` is referred to as the Transport Graph, which is constructed by sequentially inspecting the electrons used within the lattice. As each electron is reached, a corresponding node and its input-output relations are added to the transport graph. The user can visualize the transport graph in the Covalent UI. Furthermore, the graph contains information on :ref:`execution status<Workflow status polling>`, task definition, runtime, input parameters, and more. Below, we see an example of transport graph for a machine learning workflow as it appears in the Covalent UI.

.. image:: ./images/transport_graph.png
    :align: center
    :scale: 45 %
