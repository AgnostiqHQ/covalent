.. covalent

.. raw:: html

   <style>
   h1 {
     text-align: center;
   }
   </style>

======================
COVALENT DOCUMENTATION
======================

|

.. image:: _static/covalent_ui_rtd.png
   :align: center
|

Covalent is a Pythonic workflow tool used to execute tasks on advanced computing hardware. Users can decorate their existing Python functions as electrons (tasks) or lattices (workflows) and then run these functions locally or dispatch them to various classical and quantum backends according to the hardware requirements. After submitting a workflow, users can navigate to the Covalent UI to view a variety of information about it, such as the status, errors, the workflow's dependency graph, and metadata, among other things. Covalent is designed to make it easy for users to keep track of their computationally heavy experiments by providing a simple and intuitive framework to store, modify, and re-analyze computational experiments. Covalent is rapidly expanding to include support for a variety of cloud interfaces, including HPC infrastructure tools developed by major cloud providers as well as emerging quantum APIs. It has never been easier to deploy your code on the world's most advanced computing hardware with Covalent.

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

Join the Community
##################

Covalent is a quickly growing and vibrant community of enthusiasts, researchers, scientists, and engineers. Start contributing now by navigating to Covalent's `GitHub <https://github.com/AgnostiqHQ/covalent>`_ homepage or learn more about how Covalent can be used in your business on Covalent's `product <https://agnostiq.ai/covalent>`_ page. You are also welcome to engage with other users in the GitHub `discussions <https://github.com/AgnostiqHQ/covalent/discussions>`_ page.


.. toctree::
   :maxdepth: 1
   :hidden:

   Getting Started <getting_started/index>
   Concepts <concepts/concepts>
   Tutorials <tutorials/tutorials>
   How-To Guides <how_to/index>
   API Documentation <api/api>


.. toctree::
   :maxdepth: 1
   :caption: Developers:
   :hidden:

   Project Homepage <https://github.com/AgnostiqHQ/covalent>
   Contribution Guidelines <https://github.com/AgnostiqHQ/covalent/blob/develop/CONTRIBUTING.md>
   Code of Conduct <https://github.com/AgnostiqHQ/covalent/blob/develop/CODE_OF_CONDUCT.md>
