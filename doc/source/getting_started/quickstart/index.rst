==================
Quick start Guide
==================

Once Covalent has been installed in your preferred conda environment, it is quite simple to get started with creating, prototyping and dispatching workflows. Here we provide easy
to follow examples of varying levels of complexity to illustrate the core aspects of Covalent and how one can quickly start using it as their default workflow orchestration tool.

.. list-table::
    :widths: 20 15 65
    :header-rows: 1
    :align: center

    * - Example
      - Complexity
      - Description

    * - :doc:`Hello Covalent! <./beginner/hello_covalent/index>`
      - Beginner
      - This simple workflow illustrates the core features of Covalent ``electrons & lattices``

    * - :doc:`Single node workflows <./beginner/single_node_workflow/index>`
      - Beginner
      - This example illustrates how users can create workflows consisting of a single node quite easily using a combination of the ``electron`` and ``lattice`` decorators

    * - :doc:`Matrix eigenvalues <./intermediate/matrix_eigenvalues/index>`
      - Intermediate
      - This example illustrates how one can offload computationally heavy tasks to a remote machine using ``remote executors`` in Covalent