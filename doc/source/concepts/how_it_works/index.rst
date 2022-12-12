
============
How It Works
============

Covalent has three main components:
- A Python module containing an API that you use to build manageable workflows out of new or existing Python functions.
- A set of services that run locally or on a server to dispatch and execute workflow tasks.
- A browser-based UI from which to to manage workflows and view results.

You compose workflows using the Covalent API and submit them to the Covalent server. The server analyzes the workflow to determine dependencies between tasks, then dispatches each task to its specified execution backend. Independent tasks are executed concurrently if resources are available.

The Covalent UI displays the progress of each workflow at the level of individual tasks.

The Covalent API
################

The Covalent API is a Python module containing a small collection of classes that implement server-based workflow management. The key elements are two decorators that wrap functions to create managed *tasks* and *workflows*.

The task decorator is called an *electron*. The electron decorator simply turns the function into a dispatchable task.

The workflow decorator is called a *lattice*. The lattice decorator turns a function composed of electrons into a manageable workflow.

<img src="https://raw.githubusercontent.com/AgnostiqHQ/covalent/master/doc/source/_static/cova_archi.png" align="right" width="40%" alt="Covalent Architecture"/>

Covalent Services
#################

The Covalent server is a lightweight service that runs on your local machine or a server. A dispatcher analyzes workflows (lattices) and hands its component functions (electrons) off to executors. Each executor is an adaptor to a backend hardware resource. Covalent has a growing list of turn-key executors for common compute backends. If no executor exists yet for your compute platform, Covalent supports writing your own.

The Covalent GUI
################

The Covalent user interface runs as a web server on the machine where the Covalent server is running. The GUI dashboard shows a list of dispatched workflows. From there, you can drill down to workflow details or a graphical view of the workflow. You can also view logs, settings, and result sets.
