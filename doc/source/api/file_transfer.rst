File Transfer
"""""""""""""""""""""""""""

File Transfer from (source) and to (destination) local or remote files prior/post electron execution. Instances are are provided to `files` keyword argument in an electron decorator.

.. autoclass:: covalent._file_transfer.file.File
    :members:
    :inherited-members:

.. autoclass:: covalent._file_transfer.folder.Folder
    :members:
    :inherited-members:

.. autoclass:: covalent._file_transfer.file_transfer.FileTransfer
    :members:
    :inherited-members:

.. autofunction:: covalent._file_transfer.file_transfer.TransferFromRemote

.. autofunction:: covalent._file_transfer.file_transfer.TransferToRemote

Examples
~~~~~~~~

- :doc:`Transfer files locally <../how_to/coding/file_transfers_for_workflows_local>`
- :doc:`Transfer files to and from a remote host <../how_to/coding/file_transfer_to_from_remote>`
- :doc:`Transfer files to and from an S3 bucket <../how_to/coding/file_transfers_to_from_s3>`
