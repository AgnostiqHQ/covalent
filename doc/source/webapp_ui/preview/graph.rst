######################
Workflow Preview Graph
######################

The Workflow Preview Graph shows the transport graph of the lattice on which the :code:`lattice.draw()` function was last called. This is useful, for example, to verify the logic of a workflow before dispatching it to run on costly compute resources.

.. image:: ../images/preview.gif
   :align: center

The preview displays only the nodes (tasks) and edges (dependencies) of the tranport graph. No dispatch information is available (Status, Start time, End time, Input, Results or Directory) since the lattice has not actually been dispatched.
