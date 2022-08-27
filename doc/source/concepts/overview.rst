*********
Overview
*********

===========================================
What is Covalent?
===========================================

Covalent is a Pythonic workflow management tool that can be used to perform computations on advanced classical and quantum computing hardwares. To start, the user defines a workflow, or a set of interdependent tasks, using Covalent's electron and lattice decorators. An electron is a Python function that performs some granular task, while a lattice is a workflow that executes various tasks to accomplish a larger computation. Workflows can be run locally or dispatched to quantum and classical hardwares using custom executors. Running computationally intensive jobs on HPC and quantum hardware can be expensive, so users can construct, visualize, and execute the workflow locally first. Once a workflow is submitted to the dispatcher, the execution progress can be tracked in the Covalent UI. The user interface is useful not just for monitoring the execution progress of individual tasks, but it also shows users the workflow graph. The workflow graph is the visual representation of the tasks and their dependency relations, so users can better understand and communicate their computations at a conceptual level. Lastly, Covalent allows users to easily analyze, reuse, and share results of both individual tasks as well as the workflow as a whole, so that users can iterate faster and collaborate more easily.

Users may find Covalent useful for a variety of reasons:

Covalent...

* minimizes the need to learn new syntax. Once it has been installed, it is as easy as breaking your script into functions and attaching decorators.
* parallelizes mutually independent parts of workflows.
* provides an intuitive user interface to monitor workflows.
* allows users to view, modify and re-submit workflows directly within a Jupyter notebook.
* manages the results of your workflows. Whenever the workflow is modified, Covalent natively stores and saves the run of every experiment in a reproducible format.

In summary, Covalent is an easy-to-use workflow orchestration tool that makes deploying high performance computing jobs seamless. The browser-based user interface and the design of the package makes it extremely easy to track the status of the computations. Covalent has been designed so that it is very easy to modify or build on top of previous computational experiments.

Users interact with Covalent in 5 main ways:

* :ref:`Workflow construction<Workflow construction>`

* :ref:`Workflow execution<Workflow execution>`

* :ref:`Status polling<Workflow status polling>`

* :ref:`Results collection<Workflow result collection>`
* :ref:`Electron Dependencies<Workflow electron dependencies>`

* :ref:`File Transfers<File transfer>`
