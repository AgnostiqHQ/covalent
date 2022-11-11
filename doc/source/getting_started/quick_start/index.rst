=================
Quick Start Guide
=================

To quickly install Covalent and run a short demo, follow the four steps below.

.. admonition:: Before you start

  Ensure you are using a compatible OS and Python version. See the :doc:`Compatibility <./compatibility>` page for supported Python versions and operating systems.


Step 1: Install Covalent
########################

  Use Pip to install the Covalent server and libraries locally:

.. code:: bash

   pip install covalent


Step 2: Start the Server
########################

Start the Covalent server:

.. code:: console

   $ covalent start
   Covalent server has started at http://localhost:48008


Step 3: Run a Workflow
######################

Run this simple "Hello World" example to see Covalent in action.

Open a Jupyter notebook or Python console and create the following workflow:

.. code:: python

import covalent as ct

executor = ct.executor.EC2Executor(
    instance_type="t2.micro",
    volume_size=8, #GiB
    ssh_key_file="~/.ssh/ec2_key"
)

    @ct.electron(
        executor=executor
    )
    def compute_pi(n):
        # Leibniz formula for π
        return 4 * sum(1.0/(2*i + 1)*(-1)**i for i in range(n))

    @ct.lattice
    def workflow(n):
        return compute_pi(n)


    dispatch_id = ct.dispatch(workflow)(100000000)
    result = ct.get_result(dispatch_id=dispatch_id, wait=True)
    print(result.result)


Step 4: View Results
####################

Use the Covalent GUI to view the workflow progress. Navigate to the Covalent UI at `<http://localhost:48008>`_ to see your workflow in the queue:

.. image:: ./../_static/hello_covalent_queue.png
  :align: center

Click on the dispatch ID to view the workflow graph:

.. image:: ./../_static/hello_covalent_graph.png
  :align: center
