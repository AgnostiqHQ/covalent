
.. _File transfer:

=====================
File Transfer
=====================

Covalent supports transferring files from and to remote or local filesystems. These file transfer operations can be performed by specifying a list of :code:`FileTransfer` instances (along with a corresponding File Transfer Strategy) in an electron's decorator as a list using the :code:`files` keyword argument. File Transfer operations are queued to execute prior or post electron execution in the electron’s backend execution environment.

~~~~~~
Files
~~~~~~
Files are a objects which represent files corresponding to a supplied filepath.

:code:`File` objects can support various formats of filepaths such as :code:`/my_absolute_path` but also supports URIs for specifying particular protocols such as :code:`scheme://my_file_location`.
Examples of valid URIs that can be provided to a File object are below:

- :code:`/home/ubuntu/my_file`
- :code:`file:///home/ubuntu/my_file`
- :code:`https://example.com/file`

A file can be instantiated as show below::

    import covalent as ct
    file = ct.fs.File('/home/ubuntu/my_file')

.. note::

   (Advanced) File objects can also support additional arguments such as the :code:`is_remote` flag which should only be used when using the :code:`FileTransfer` class directly to specify a file that resides on a remote host (for usage with Rsync via SSH).

A :code:`File` object's filepath can be accessed using::

    import covalent as ct
    file = ct.fs.File('/home/ubuntu/my_dir')
    print(file.filepath)

~~~~~~
Folders
~~~~~~
A :code:`Folder` is an object which represents a folder corresponding to a supplied filepath. Folders inherit from the File class so they support the same filepath formats as above.

A folder can be instantiated as show below::

    import covalent as ct
    folder = ct.fs.Folder('/home/ubuntu/my_dir')


~~~~~~
FileTransfer
~~~~~~
A :code:`FileTransfer` object is a declarative manner of specifying File Transfer operations which should be queued prior or post electron execution.
In general FileTransfer objects take a from (source) and to (destination) filepaths (or File objects) along with a File Transfer Strategy to perform download, upload, or copy operations over a corresponding protocol.

A File Transfer object can be created with the following to describe a local file transfer using Rsync::

    import covalent as ct
    ft = ct.fs.FileTransfer('/home/ubuntu/src_file','/home/ubuntu/dest_file')

By default the File Transfer will occur prior to electron execution, however one can specify that this should be performed post execution using the Order enum as such::

    import covalent as ct
    ft = ct.fs.FileTransfer('/home/ubuntu/src_file','/home/ubuntu/dest_file', order=ct.fs.Order.AFTER)

Under the hood covalent will create File objects corresponding to each filepath, but one can explicitly use File objects in a FileTransfer object::

    import covalent as ct
    source_file = ct.fs.File('/home/ubuntu/src_file')
    dest_file = ct.fs.File('/home/ubuntu/dest_file')
    ft = ct.fs.FileTransfer(source_file, dest_file, order=ct.fs.Order.BEFORE)

If a provided file argument is `None` or a :code:`File` without a specified filepath then a temporary file will be created (with a corresponding filepath located in `/tmp`)::

    temp_file = ct.fs.File() # with location temp_file.filepath
    ct.fs.FileTransfer(source_file,temp_file)

The following are equivalent statements::

    ct.fs.FileTransfer(source_file)
    ct.fs.FileTransfer(source_file, ct.fs.File())
    ct.fs.FileTransfer(from_file=source_file, to_file=None)

:code:`File` objects corresponding to a file transfer can be accessed by using either :code:`ct.fs.FileTransfer().from_file` or :code:`ct.fs.FileTransfer().to_file`.

Furhermore Folders can also be used in file transfer operations::

    import covalent as ct
    src_dir = ct.fs.Folder('/home/ubuntu/src_dir')
    dest_dir = ct.fs.Folder('/home/ubuntu/dest_dir')
    ft = ct.fs.FileTransfer(src_dir, dest_dir)

By default only folder contents are transfered to the destination folder however one can specify to also include the folder in the transfer with :code:`Folder('filepath', include_folder=True)`

To use File Transfers in a covalent workflow a list of :code:`FileTransfer` instances must be specified in an electron's decorator using the :code:`files` keyword argument.

Furthermore, a :code:`files` keyword argument also gets injected into the python function decorated by an electron when supplying :code:`FileTransfer` instances in an electron's arguments.
This :code:`files` kwarg contains a reference to the files corresponding to the source & destination filepaths in a supplied  :code:`FileTransfer` instance in the same order as the file transfers are specified::


    import covalent as ct
    @ct.electron(
        files=[ct.fs.FileTransfer('/home/ubuntu/src_file', '/home/ubuntu/dest_file')]
    )
    def my_task(files=[]):
        from_file, to_file = files[0]
        # we can read the destination filepath as the above file transfer is performed prior to electron execution
        with open('/home/ubuntu/dest_file', 'r') as f:
            return f.read()

    @ct.lattice()
    def file_transfer_workflow():
        return my_task()

    # Dispatch the workflow
    dispatch_id = ct.dispatch(file_transfer_workflow)()

.. warning:: As discussed in the next section the :code:`files` keyword argument in the electron decorated python function must always be specified when using :code:`FileTransfer` for the workflow to be constructed successfully.

~~~~~~
Strategies
~~~~~~

File Transfer Strategies define how files should be copied, downloaded, or uploaded during a file transfer operation. If a strategy is not explicitly provided in a FileTransfer object a corresponding strategy is resolved by covalent based on the provided File schemes.

A strategy can be specified in a :code:`FileTransfer` by specifying the :code:`strategy` keyword argument.

Rsync
---------------------

.. warning:: Rsync must be installed on an electron’s backend execution environment. On Debian based distros (ex. Ubuntu ) with :code:`apt-get install rsync` , rpm-based based distros (ex. CentOS, Fedora) with :code:`yum install rsync`, or MacOS with :code:`brew install rsync`

This is the default strategy when transferring files within a local filesystem.

If both the from & to filepaths are of the file scheme (i.e using filepaths of the form :code:`/home/ubuntu/...`, or :code:`file:///home/ubuntu/...`) Rsync is automatically chosen as the default file transfer strategy.

Therefore the following are equivalent::

    import covalent as ct

    ct.fs.FileTransfer('/home/ubuntu/src', '/home/ubuntu/dest')
    ct.fs.FileTransfer('/home/ubuntu/src', '/home/ubuntu/dest', strategy=ct.fs_strategies.Rsync())

Rsync (SSH)
---------------------

.. warning:: Rsync must be installed on an electron’s backend execution environment. On Debian based distros (ex. Ubuntu ) with :code:`apt-get install rsync` , rpm-based based distros (ex. CentOS, Fedora) with :code:`yum install rsync`, or MacOS with :code:`brew install rsync`

If one of the files are marked as remote the Rsync strategy will be used but will require additional information such as username and host to connect to via SSH (optionally a private key path to use).

The following will describe an Rsync file transfer operation over SSH to download a remote file and place in the specified local filepath::

    import covalent as ct

    strategy = ct.fs_strategies.Rsync(user='admin', host='44.202.86.215', private_key_path='...')
    from_remote_file = File('/home/admin/my_file', is_remote=True)
    to_local_file = File('/home/ubuntu/my_file')
    ct.fs.FileTransfer(from_remote_file, to_local_file, strategy=strategy)


S3
~~~~~~~~~~~~
.. warning:: AWS Python SDK must be installed on an electron’s backend execution environment. It can be installed using :code:`pip install boto3`

If one of the files is a S3 bucket location (s3://repository-name/file-path) S3 strategy will be used. For accessing the S3 bucket necessary credentials (aws_access_key_id, aws_secret_access_key, aws_session_token, region_name) can be passed to it. In case they are not provided default values described in the environment will be used.

The following will perform an S3 file transfer operation to download a remote file and place in the specified local filepath::

    import covalent as ct

    strategy = ct.fs_strategies.S3(aws_access_key_id = '...', aws_secret_access_key = '...', aws_session_token = '...', region_name = '...')

    ct.fs.FileTransfer('s3://covalent-tmp/temp.txt','/home/ubuntu/temp.txt',strategy = strategy)


~~~~~~
TransferFromRemote
~~~~~~

A shorthand manner of specifying file transfers from a remote source (with a default order of BEFORE) is the following::

    import covalent as ct

    strategy = ct.fs_strategies.Rsync(user='admin', host='44.202.86.215', private_key_path='...')
    ct.fs.TransferFrom('/home/admin/my_file', '/home/ubuntu/my_file', strategy=strategy)

Which is equivalent to::

    import covalent as ct

    strategy = ct.fs_strategies.Rsync(user='admin', host='44.202.86.215', private_key_path='...')
    from_remote_file = File('/home/admin/my_file', is_remote=True)
    to_local_file = File('/home/ubuntu/my_file')
    ct.fs.FileTransfer(from_remote_file, to_local_file, strategy=strategy, order=ct.fs.Order.BEFORE)

.. note::

   The order of the :code:`TransferFromRemote` operation can be specified in the same manner as :code:`FileTransfer` using the :code:`order` keyword argument with the corresponding :code:`Order` enum.

~~~~~~
TransferToRemote
~~~~~~

A shorthand manner of specifying file transfers to a remote destination (with a default order of AFTER) is the following::

    import covalent as ct

    strategy = ct.fs_strategies.Rsync(user='admin', host='44.202.86.215', private_key_path='...')
    ct.fs.TransferTo('/home/admin/my_file', '/home/ubuntu/my_file', strategy=strategy)

Which is equivalent to::

    import covalent as ct

    strategy = ct.fs_strategies.Rsync(user='admin', host='44.202.86.215', private_key_path='...')
    from_local_file = File('/home/ubuntu/my_file')
    to_remote_file = File('/home/admin/my_file', is_remote=True)
    ct.fs.FileTransfer(from_local_file, to_remote_file, strategy=strategy, order=ct.fs.Order.AFTER)

.. note::

   The order of the :code:`TransferToRemote` operation can be specified in the same manner as :code:`FileTransfer` using the :code:`order` keyword argument with the corresponding :code:`Order` enum.
