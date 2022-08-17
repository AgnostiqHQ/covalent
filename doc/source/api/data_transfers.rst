.. _file_transfer:

File and Data Transfer
"""""""""""""""""""""""""""



Basic File transfer interface
********************************

File Transfer from (source) and to (destination) local or remote files prior/post electron execution. Instances are are provided to `files` keyword argument in an electron decorator.


.. automodule:: covalent.fs
   :imported-members:
   :members:
   :undoc-members:
   :show-inheritance:


.. _file_transfer_strategies:

File transfer strategies
*************************

A set of classes with a shared interface to perform copy, download, and upload operations given two (source & destination) File objects that support various protocols.

.. automodule:: covalent.fs_strategies
   :imported-members:
   :members:
   :undoc-members:
   :show-inheritance:
