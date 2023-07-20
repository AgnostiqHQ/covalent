##############
Best Practices
##############

This guide describes some best practices for use with Covalent. Most are coding best practices to be followed when writing workflows. Others include server configuration and runtime considerations.

.. note:: The coding best practices are illustrated examples using Jupyter notebook files (formerly IPython files; they have an `ipynb` file extension). You can open a file and run the example on your local machine. To run an example:

    1. `Install Jupyter <https://jupyter.org/install>`_.
    2. :doc:`Install Covalent<../getting_started/quick_start/index>`.
    3. :doc:`Start the Covalent server<./execution/covalent_cli>`.
    4. Download the IPython (`.ipynb`) file by replacing `html` with `ipynb` in the How-to document URL. For example, change "https://covalent.readthedocs.io/en/stable/how_to/orchestration/construct_electron.html" to "https://covalent.readthedocs.io/en/stable/how_to/orchestration/construct_electron.ipynb"\.
    5. `Open the IPython (.ipynb) file in a Jupyter notebook <https://docs.jupyter.org/en/latest/running.html#how-do-i-open-a-specific-notebook>`_.

The coding practices described here fall into two categories:

- Patterns and techniques that improve Covalent implementations in some way. These improvements can be in efficiency, performance, code maintainability, or any of a number of other attributes considered desireable in a development project.
- Techniques that must be followed when using Covalent. These usually reflect requirements for server-based dispatch and execution of workflows. The consequences of violating these requirements are demonstrated in the individual entries; in most cases, they cause the workflow to fail.

Coding Best Practices
---------------------

:doc:`Implementing Dynamic Workflows <./patterns/dynamic_workflow>`
    Use sublattices to encapsulate dynamic code.

:doc:`Creating One Executor per Resource <./patterns/executor_assignment>`
    Create one executor object per compute resource and assign the executor to electrons as needed.

:doc:`Transferring Large Data Objects <./patterns/large_object_transfer>`
    Save large data objects to a data store and read the object to electrons as needed.

:doc:`Containing Computations in Tasks <./patterns/post_process>`
    Use an electron to generate the return value of a workflow.

:doc:`Writing Result-Dependent Branch Decisions <./patterns/result_dependent_if_else>`
    Encapsulate result-dependent if/else statements in an electron.

:doc:`Writing Result-Dependent Loops <./patterns/result_dependent_loop>`
    Encapsulate result-dependent loops in an electron.

:doc:`Returning Multiple Values from a Function <./patterns/return_multiple_values_from_task>`
    To avoid needlessly proliferating functions, return multiple values from a task in an array.

:doc:`Deploying a Covalent Server <./patterns/deployment>`
    Follow these guidelines when running Covalent on a server.

----------------------------------

Is anything missing? Contribute a suggested technique on `GitHub <https://github.com/AgnostiqHQ/covalent/issues>`_.
