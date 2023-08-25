.. currentmodule:: covalent

############
Covalent API
############

This is the component reference for the Covalent Python API.

Index
#####

:doc:`Here<./index>` is an alphabetical index.

Contents
########

.. include:: ./toc.rst


API
###

.. _workflow_components_api:
.. include:: ./section_workflow_components.rst


.. _task_helpers_api:
.. include:: ./section_task_helpers.rst


.. _executors_api:
.. include:: ./section_executors.rst


.. _dispatch_infrastructure_api:
.. include:: ./section_dispatch_infrastructure.rst

.. _qelectrons_api:

Quantum Electrons
"""""""""""""""""""""""""""

.. autodecorator:: covalent.qelectron


----------------------------------------------------------------

.. _qclusters_api:

Quantum Clusters
"""""""""""""""""""""""""""

.. autopydantic_model:: covalent.executor.QCluster


----------------------------------------------------------------

.. _covalent_cli_tool_api:
.. include:: ./section_covalent_cli_tool.rst


.. toctree::
   :maxdepth: 1
   :hidden:

   section_workflow_components
   section_task_helpers
   section_executors
   section_dispatch_infrastructure
   section_covalent_cli_tool
