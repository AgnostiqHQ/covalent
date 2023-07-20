.. _file_transfer:

File and Data Transfer
""""""""""""""""""""""

File Transfer Interface
~~~~~~~~~~~~~~~~~~~~~~~

File transfer to and from local or remote files, before or after electron execution. Provide a `FileTransfer` instance as a `files` keyword argument in the electron decorator.


.. automodule:: covalent.fs
   :imported-members:
   :members:
   :undoc-members:
   :show-inheritance:


.. _file_transfer_strategy:

Examples
~~~~~~~~

- :doc:`Transfer local files <../how_to/execution/file_transfers_for_workflows_local>`
- :doc:`Transfer remote files <../how_to/execution/file_transfers_to_from_remote>`
- :doc:`Transfer Amazon files to and from Amazon S3<../how_to/execution/file_transfers_to_from_s3>`

File Transfer Strategies
~~~~~~~~~~~~~~~~~~~~~~~~

A set of classes that support various protocols. All `FileTransferStrategy` classes share an interface to perform `copy`, `download`, and `upload` operations on two `File` objects (a source and a destination).

.. automodule:: covalent.fs_strategies
   :imported-members:
   :members:
   :undoc-members:
   :show-inheritance:
