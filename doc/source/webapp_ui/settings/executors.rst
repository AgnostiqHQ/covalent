#########
Executors
#########

Use the Executors Settings page to view and change executor preferences for local and Dask cluster executors. When you use a remote executor, the executor's settings become available in the Executors list.

.. note:: Click Save to enable all changes made in the Executors list. Clicking Cancel reverts all fields to their pre-changed values.

.. image:: ../images/executors.png
    :align: center

Local
-----

Log Standard Out
    The name of the file to which the local executor logs :code:`stdout`. The file is located in dispatch- and node-specific subdirectories of the results directory.
Log Standard Error
    The name of the file to which the local executor logs :code:`stderr`. The file is located in dispatch- and node-specific subdirectories of the results directory.
Cache Directory
    The directory path ???


Dask
----

Log Standard Out
    The name of the file to which the local executor logs :code:`stdout`. The file is located in dispatch- and node-specific subdirectories of the results directory.
Log Standard Error
    The name of the file to which the local executor logs :code:`stderr`. The file is located in dispatch- and node-specific subdirectories of the results directory.
Cache Directory
    The directory path ???


Remote
------

Poll Freq
    How often, in ???, the Dask cluster polls ???
Remote Cache
    The directory path used by the remote executor ???
Credentials File
    The path of the file containing the connection credentials for the remote compute node. For example, the path of the AWS config file for AWS Cloud credentials.
