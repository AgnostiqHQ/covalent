########
Glossary
########

.. glossary::
    API
        Application Programming Interface.

        In general, the components of a software product that are exposed or made public so that third-party developers can extend the product or incorporate it into other software.

        In Covalent, a Python module containing a small collection of classes that implement server-based workflow management. A superset of the Covalent :term:`SDK`.

    Cluster
        A pool of identical workers, typically computational processes, that can be accessed by a multiple :term:`executors<executor>` in :term:`parallel`. The computational processes can be on separate :term:`host`s, one or more VMs, or under management of a container service on the same host.

    Contributor
        A volunteer who contributes work to an open source project. Usually but not always a software engineer. The work can be software, documentation, testing, or other types of support.

        Covalent contributors develop and maintain the Covalent API, server code, plug-ins, documentation, examples, and tutorials, and help publicize and promote Covalent.

    Covalent
        A Pythonic workflow manager engineered especially for interactive data science experimentation with high-performance and specialized computation platforms, including quantum computers.

    Credentials
        Any of a number of encryption-based keys, storable in a data file, that serves to `authenticate or authorize <https://www.okta.com/identity-101/authentication-vs-authorization/>`_ access to a computing resource such as a cloud-based virtual machine instance.

    Dask
        An open source Python library and scheduler for parallel and distributed computation. Covalent uses Dask as its default :term:`executor` for :term:`workflow` :term:`tasks`.

    Dispatch
        In general, to send a :term:`workflow` or other computational job to be run by a scheduler.

        In Covalent, ``dispatch()`` is a function that sends a :term:`lattice` to the Covalent server.

        A *dispatcher* is a server process that dispatches workflow tasks. See also :term:`scheduler`.

    Electron
        Covalent's Pythonic class representing a :term:`task`, or the class instantiated as an object. More precisely, by typographical convention:

        :code:`Electron` (capital "E")
            The :doc:`Covalent API class <../api/electrons>` representing a computational task that can be run by a Covalent executor.

        electron (lower-case "e")
            An object that is an instantiation of the :code:`Electron` class.

        :code:`@covalent.electron`
            The decorator used to (1) turn a function into an electron; (2) wrap a function in an electron, and (3) instantiate an instance of :code:`Electron` containing the decorated function (all three descriptions are equivalent).

    Executor
        In Covalent, an interface to a computational resource. The compute resource is said to *back*, or be the "backend" for, the executor. The backend can be local, remote, or cloud-based. A single executor is backed by exactly one resource (though that resource could be a :term:`cluster`).

        A :term:`workflow` can have access to any number of executors, backed by any number of different resources of any number of types. Each :term:`task` within the workflow is assigned an executor, explicitly or by default.

        Covalent comes with a default executor backed by a local :term:`Dask` cluster.

    Experiment
        A computational script or notebook that performs data analysis, parametric data modeling, or machine learning, usually with the intent of developing a predictive model in some scientific domain.

        Covalent is designed to facilitate interactive development of an experiment, typically with the intent of working toward an analysis or model running massive data on a HPC or quantum compute resource.

    Function
        In Python, a runnable object that takes input parameters and produces a result, either in the form of a return value, side effects, or both.

    GUI
        Graphical user interface. The *Covalent GUI* is a browser-based system for viewing and managing Covalent dispatches, results, and logs.

    Host
        A single physical computer, as distinct from a :term:`virtual machine (VM)<vm>`. Also commonly called a "node" or "machine".

        "Host" and "node" can also refer more generally to a standalone computer that may either be a physical machine or a VM. Context usually distinguishes which usage is intended.

    Lattice
        Covalent's Pythonic class representing a :term:`workflow`, or the class instantiated as an object. More precisely, by typographical convention:

        :code:`Lattice` (capital "L")
            The :doc:`Covalent API class <../api/lattice>` representing a workflow that can be run by a Covalent dispatcher.

        :code:`lattice` (lower-case "l")
            An object that is an instantiation of the :code:`Lattice` class.

        :code:`@covalent.lattice`
            The decorator used to create a lattice by wrapping a function in the :code:`Lattice` class.

    Local
        The descriptor for a computer that you are working on directly – a laptop or desktop workstation. Also called a *client* when you're using it to connect to a :term:`remote` server.

    Management
        The Covalent server *manages* workflows in the sense that it analyzes and runs them using different :term:`executors<executor>` as specified in the code. This is in contrast to an *unmanaged* experiment or script, which is simply in a Python interpreter without specifying or saving the execution details or results.

    Parallelism
        Decomposing a workflow to run in two or more parallel processes or threads to improve real-time performance.

    Python
        A high-level computer language. Covalent is written in Python.

        The Python open-source community has developed several features that make it popular with machine learning researchers and data scientists, including:

        * Many libraries that facilitate data analytics and ML/AI. Some of the most popular are Pandas, NumPy, SciKit-Learn, Scrapy, PyTorch, and TensorFlow.
        * Compilers for improving the performance of Python code (Python is nominally an interpreted language).
        * Notebooks such as Jupyter for developing, running and documenting :term:`experiment`s.

    Remote
        The descriptor for a :term:`host`, or for a Covalent server running on a host, that you connect to via a network. A remote host can be on-premise or in the cloud, for example on an AWS instance.

    Result
        In Covalent, a Python object that represents the return value of an :term:`electron` or :term:`lattice`.
    S3
        Simple Storage System. S3 is a cloud object storage system offered on Amazon Web Services' (AWS).

    Scheduler
        Server software that manages a queue of workflow requests. Sometimes used interchangeably with :term:`dispatcher`, but technically not the same thing. A scheduler manages workflow requests; a dispatcher runs tasks and manages :term:`results`.

    SDK
        Software Development Kit.

        In general, the components of an :term:`API` that enable it to be incorporated into a larger software product.

        In Covalent, the module containing the :term:`lattice`, :term:`electron`, :term:`dispatcher<dispatch>` and other classes that enable the Covalent server to manage workflows.

    Server
        Refers to both a :term:`remote` :term:`host`, and to software (such as Covalent) running on that host.

    Sublattice
        In Covalent, a :term:`lattice` that has been encapsulated with an :term:`electron` decorator so that it can be included as a single task in a larger lattice.

    Subtask
        Obsolete terminology for an :term:`electron`.

    Task
        A unit of work in a workflow. In Covalent, a task is:

        * Contained in a single function
        * Denoted by the :term:`@electron<electron>` decorator
        * Assigned an :term:`executor` on which to run

    Transport Graph
        A `directed, acyclic graph <https://en.wikipedia.org/wiki/Directed_acyclic_graph>`_ that represents a :term:`workflow` in Covalent. The nodes of a transport graph are tasks and parameters, and the edges of the graph are dependencies.

    User
        In general, a software industry term that describes a person using a particular application program or software system.

        In Covalent, a data professional who employs the Covalent :term:`SDK<sdk>` to run :term:`workflows` from a notebook or interactive Python session.

    VM
        Virtual machine. A software emulation of a computer, complete with its own compute, storage, and network resources, that runs in a set of partitioned-off address spaces on a physical :term:`host`.

    Workflow
        A sequence of computational :term:`tasks` designed to implement a data model or analysis.

        In Covalent, a workflow is wrapped in the :term:`lattice` decorator so it can be analyzed, scheduled and, executed on the Covalent server.
