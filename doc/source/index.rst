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

Covalent is a Python-language – and `Pythonic <https://www.udacity.com/blog/2020/09/what-is-pythonic-style.html>`_ – workflow tool for computational scientists, AI/ML software engineers, and anyone who needs a way to run experiments on limited or expensive computing resources. Such resources can include quantum computers, HPC clusters, GPU arrays, and cloud services. Covalent manages workflows in heterogeneous environments that contain any or all of these advanced platforms.

Covalent enables you to:

Isolate operations that don't require advanced compute resources so you can run them on commonly available hardware.
    Covalent dispatches tasks to any number of executors backed by heterogeneous hardware platforms. Run non-critical tasks on commodity hardware, reserving advanced hardware only for the heavy computations. Covalent makes using a heterogeneous environment almost as easy as running with a monolithic backend.

Test individual functions or groups of functions on local hardware before committing them to advanced hardware.
    Not only does Covalent run different workflow tasks on different platforms,  but reassigning a task to a different platform is as easy as changing a single attribute in a function decorator. Test locally, then do the real work on big hardware.

Iteratively run prototypes and exploratory research models and save results.
    Covalent saves the data required to reproduce every run of every workflow, along with its results. Manage running workflows, view task dependencies, and examine results in Covalent's intuitive browser-based UI.

Automate and manage workflows from a Jupyter notebook or Python command line.
    The Covalent scheduler runs locally or on a server. Run experiments as you normally would, swapping parameters and datasets, from Jupyter or any other interactive Python environment.

Run experiments faster with parallel processing.
    Covalent automatically parallelizes independent tasks to accelerate job completion.

.. admonition:: Ready to try it?

    Skip to `Getting Started <https://covalent.readthedocs.io/en/latest/getting_started/index.html>`_.

Covalent is designed and developed from the ground up for data experimentation and prototyping. Covalent features:

Pure Python
    Covalent automatically constructs complex workflows when you program with native Python functions. Make your code Covalent-ready simply by adding one-line decorators to your functions.

A robust user interface
    Covalent provides an intuitive and aesthetic browser-based UI to monitor and manage your workflows.

Result management
    Covalent manages the results of your workflows. Covalent stores and saves the run of every experiment in a reproducible format, making it easy to modify any part of your workflow from inputs to components.

Low overhead
    Covalent is designed to be as lightweight as possible and is optimized for the most common use cases. Covalent's overhead is less than 0.1% of the total runtime for typical high-compute applications and often has a constant overhead of ~ 10-100μs – and this is constantly being optimized.

Interactive
    Unlike other workflow tools, Covalent is interactive. You can view, modify, and re-submit workflows directly within a Jupyter notebook.

.. admonition:: Ready to try it?

    Skip to `Getting Started <https://covalent.readthedocs.io/en/latest/getting_started/index.html>`_.


Is It Really That Easy?
#######################

Don't be fooled the simplicity of Covalent's decorator-based code syntax. Each decorator is a wrapper hiding sophisticated task management software that analyzes function input and output and enables the Covalent server to abstract the code from the backend implementation.

That said, you do have a responsibility when you use a Covalent decorator to make your code task-oriented and Pythonic.

Task-oriented, because the more you use small, independent, single-purpose tasks, the more efficiently Covalent can manage your workflow. Long, shambolic scripts are not a good candidate for Covalent scheduling – at least not without refactoring.

Pythonic, because using Python best practices enables Covalent to automatically construct workflow graphs without having to specify graph edges explicitly in another language such as YAML.

For a more in-depth description of Covalent's features and how they work, refer to the `Concepts <https://covalent.readthedocs.io/en/latest/concepts/concepts.html>`_ page in the documentation.

.. |

.. .. raw:: html

   <div style="position: relative; padding-bottom: 56.25%; padding-top: 30px; height: 0; overflow: hidden; margin-bottom: -15px">

   <iframe
   style="position: absolute; top: 0; left: 50%; width: 100%; height: 100%; max-width: 600px; max-height: 400px; transform:translateX(-50%); -webkit-transform:translateX(-50%); -moz-transform: translateX(-50%);"
   src="https://www.youtube.com/embed/tZ92zRbnuAA"
   frameborder="0"
   allowfullscreen="">
   </iframe>
   </div>

Next Steps
##########

Check out the :doc:`Getting Started <./getting_started/index>` page to learn how to immediately start using Covalent. After you're set up, come back and dig deeper in the Concepts and Tutorials. Once you're comfortable with the basics, use the How-To Guides and the API Reference to start building your own applications.

.. panels::

   :column: col-lg-12 p-2
   .. link-button:: getting_started/index
    :type: ref
    :text: Getting Started
    :classes: btn-outline-primary btn-block

   ----------------

   Concepts
   ^^^^^^^^^^^^^^^^^^^^^^
   What is a workflow? How does Covalent work? This section covers the "big picture", including design principles and motivations for using Covalent.

   +++

   .. link-button:: concepts/concepts
      :type: ref
      :text: Go To Concepts
      :classes: btn-outline-primary btn-block stretched-link

   ------------------------------------------------

   Tutorials
   ^^^^^^^^^^^^^^^^^^^^^^
   Learn how Covalent is being used in real-world research applications. The tutorials range in difficulty and span a variety of subjects.

   +++

   .. link-button:: tutorials/tutorials
       :type: ref
       :text: Go To Tutorials
       :classes: btn-outline-primary btn-block stretched-link

   ------------------------------------------------

   How-To Guides
   ^^^^^^^^^^^^^^^^^^^^^^
   Quick references and examples for users who know what they're looking for.

   +++

   .. link-button:: how_to/index
       :type: ref
       :text: Go To How-To Guides
       :classes: btn-outline-primary btn-block stretched-link

   ------------------------------------------------

   API Reference
   ^^^^^^^^^^^^^^^^^^^^^^
   Learn more about the syntax of Covalent's classes, functions, and modules.

   +++

   .. link-button:: api/api
      :type: ref
      :text: Go To API Reference
      :classes: btn-outline-primary btn-block stretched-link

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

Covalent is a quickly growing and vibrant community of enthusiasts, researchers, scientists, and engineers. Start contributing now by navigating to Covalent's `GitHub <https://github.com/AgnostiqHQ/covalent>`_ homepage or learn more about how Covalent can be used in your business on Covalent's `product <https://agnostiq.ai/covalent>`_ page. You are also welcome to engage with other users in the GitHub `discussions <https://github.com/AgnostiqHQ/covalent/discussions>`_ page.


.. toctree::
   :maxdepth: 3
   :hidden:

   Getting Started <getting_started/index>
   Concepts <concepts/concepts>
   Tutorials <tutorials/tutorials>
   How-To Guides <how_to/index>
   User Interface <webapp_ui/index>
   🔌 Plugins <plugins>
   Credentials <credentials>
   API Documentation <api/index>


.. toctree::
   :maxdepth: 1
   :caption: Developers:
   :hidden:

   Project Homepage <https://github.com/AgnostiqHQ/covalent>
   Contribution Guidelines <https://github.com/AgnostiqHQ/covalent/blob/develop/CONTRIBUTING.md>
   Code of Conduct <https://github.com/AgnostiqHQ/covalent/blob/develop/CODE_OF_CONDUCT.md>
