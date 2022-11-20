.. covalent

.. raw:: html

   <style>
   a[href="#covalent-documentation"] {
     position: absolute;
   }
   h1 {
     text-align: center;
   }
   </style>

======================
COVALENT DOCUMENTATION
======================

.. raw:: html

   <center>
   <a href="https://pypi.org/project/covalent/"><img alt="Downloads per Month Badge" src="https://img.shields.io/pypi/dm/covalent"></a>
   <a href="https://www.gnu.org/licenses/agpl-3.0.en.html"><img alt="AGPL License Badge" src="https://img.shields.io/badge/License-AGPL_v3-lightgray.svg"></a>
   <a href="https://github.com/AgnostiqHQ/covalent/releases/latest"><img alt="Latest Release Badge" src="https://img.shields.io/github/v/release/AgnostiqHQ/covalent"></a>
   <img alt="Supported Platforms Badge" src="https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10-blueviolet">
   </center>

|

.. image:: _static/covalent_platform.svg
   :align: center

|

Covalent is a Pythonic workflow tool for computational scientists, AI/ML software engineers, and anyone who needs to run experiments on limited or expensive computing resources including quantum computers, HPC clusters, GPU arrays, and cloud services.

Covalent enables a researcher to run computation tasks on an advanced hardware platform – such as a quantum computer or serverless HPC cluster – using a single line of code.

💭 Why Covalent?
################

Covalent overcomes computational and operational challenges inherent in AI/ML experimentation.

.. list-table::
    :widths: auto
    :header-rows: 1

    * -  Computational Challenges
      - Operational Challenges
    * - Advanced compute hardware is expensive, and access is often limited – shared with other researchers, for example.
      - Proliferation of models, datasets, and hardware trials.
    * - You'd like to iterate quickly, but running large models takes time
      - Switching between development tools, including notebooks, scripts, and submission queues.
    * - Parallel computation speeds execution, but requires careful attention to data relationships.
      - Tracking, repeating, and sharing results.

With Covalent, you:

* Assign functions to appropriate resources: Use advanced hardware (quantum computers, HPC clusters) for the heavy lifting and commodity hardware for bookkeeping.
* Test functions on local servers before shipping them to advanced hardware.
* Let Covalent's services analyze functions for data independence and automatically parallelize them.
* Run experiments from a Jupyter notebook (or whatever your preferred interactive Python environment is).
* Track workflows and examine results in a browser-based GUI.


Get Started
~~~~~~~~~~~

.. panels::

    .. link-button:: getting_started/quick_start
        :type: ref
        :text: Quick Start
        :classes: btn-outline-primary btn-block stretched-link

    +++

    Install Covalent, start a local server, and run an example workflow in 10 minutes.

    ------------------------------------------------

    .. link-button:: getting_started/index
        :type: ref
        :text: Getting Started
        :classes: btn-outline-primary btn-block stretched-link

    +++

    Install Covalent and see how easy it is to execute the same task on different backends. Also describes how to build Covalent from source – start here if you want to contribute to the Covalent OS project.

Learn More
~~~~~~~~~~

.. panels::

    .. link-button:: concepts/concepts
        :type: ref
        :text: Concepts
        :classes: btn-outline-primary btn-block stretched-link

    +++

    How does Covalent work? An architectural overview.

    ------------------------------------------------

    .. link-button:: api/api
        :type: ref
        :text: API Reference
        :classes: btn-outline-primary btn-block stretched-link

    +++

    Covalent's classes, functions, and modules. Parameters and attributes of Workflows, Tasks, and Executors.

Build Workflows
~~~~~~~~~~~~~~~

.. panels::

    .. link-button:: how_to/index
        :type: ref
        :text: How-To Guides
        :classes: btn-outline-primary btn-block stretched-link

    +++

    Build your own workflows with this cookbook-style collection of instructions for every stage of a project, from orchestration to execution to results.

    ------------------------------------------------

    .. link-button:: tutorials/tutorials
        :type: ref
        :text: Tutorials
        :classes: btn-outline-primary btn-block stretched-link

    +++

    Learn how to apply Covalent in real-world research applications. The tutorials range in complexity from beginner to advanced and span a variety of topic areas.


Recent Changes
##############

The latest release of Covalent includes two new feature sets and three major enhancements. True to its modular nature, Covalent now allows users to define custom pre- and post-hooks to electrons to facilitate various use cases from setting up remote environments (using `DepsPip`) to running custom functions. We also now support data/file transfers between remote electrons in a very modular way, including `Rsync`, `HTTP`, and `S3` protocols. As part of the enhancements, Covalent now internally uses an SQL database instead of storing results in a serialized format, which has resulted in impressive speedups and stability across the platform.  We have further made the Covalent server leaner by not requiring it to have any dependencies of electrons installed.  Covalent now only requires that your electron’s software dependencies exist on the client (the machine submitting the workflows) and backend (hardware running the tasks).

Summary of major features/enhancements

- Pre- and post-hooks to setup the software environment and to run other custom functions
- Data transfer/management between electrons
- Robust database for storing and managing results
- User interface enhancements

Join the Community
##################

Covalent is a quickly growing and vibrant community of enthusiasts, researchers, scientists, and engineers. Start contributing now by navigating to Covalent's `GitHub <https://github.com/AgnostiqHQ/covalent>`_ homepage or learn more about how Covalent can be used in your business on Covalent's `product <https://agnostiq.ai/covalent>`_ page. You can also engage with other users in the GitHub `discussions <https://github.com/AgnostiqHQ/covalent/discussions>`_ page.


.. toctree::
   :maxdepth: 3

   Quick Start <getting_started/quick_start>
   Getting Started <getting_started/index>
   Concepts <concepts/concepts>
   API Reference <api/index>
   How-To Guides <how_to/index>
   Tutorials <tutorials/tutorials>
   User Interface <webapp_ui/index>
   Credentials <credentials>


.. toctree::
   :maxdepth: 1
   :caption: Developers:
   :hidden:

   Project Homepage <https://github.com/AgnostiqHQ/covalent>
   Contribution Guidelines <https://github.com/AgnostiqHQ/covalent/blob/develop/CONTRIBUTING.md>
   Code of Conduct <https://github.com/AgnostiqHQ/covalent/blob/develop/CODE_OF_CONDUCT.md>
