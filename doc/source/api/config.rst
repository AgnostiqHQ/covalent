.. _config:


Setting Defaults
""""""""""""""""""

Default configuration for covalent can be set by defining the environment variable :code:`COVALENT_CONFIG_DIR`, by default, config files are stored in :code:`~/.config/covalent/covalent.conf`.


Example settings in config file

.. note:: 
    
    This is a YAML file, so you can use any YAML syntax.


.. tip:: 
    
    Each executer comes with its own configuration parameters that is stored in this same config file config file.
    For example, for SSH plugin, we have the following settings:

    .. code:: shell

        [executors.ssh]
        username = "user"
        hostname = "host.hostname.org"
        remote_dir = "/home/user/.cache/covalent"
        ssh_key_file = "/home/user/.ssh/id_rsa"


Typical Configuration settings
******************************

Generated each time covalent is installed and can be found at :code:`~/.config/covalent/covalent.conf`

.. code:: shell

    [sdk]
    log_dir = "/Users/voldemort/.cache/covalent"
    log_level = "warning"
    enable_logging = "false"
    executor_dir = "/Users/voldemort/.config/covalent/executor_plugins"

    [dispatcher]
    address = "localhost"
    port = 48008
    cache_dir = "/Users/voldemort/.cache/covalent"
    results_dir = "results"
    log_dir = "/Users/voldemort/.cache/covalent"

    [dask]
    cache_dir = "/Users/voldemort/.cache/covalent"
    log_dir = "/Users/voldemort/.cache/covalent"
    mem_per_worker = "auto"
    threads_per_worker = 1
    num_workers = 8
    scheduler_address = "tcp://127.0.0.1:60690"
    dashboard_link = "http://127.0.0.1:8787/status"
    process_info = "<DaskCluster name='LocalDaskCluster' parent=80903 started>"
    pid = 80924
    admin_host = "127.0.0.1"
    admin_port = 60682

    [workflow_data]
    db_path = "/Users/voldemort/.local/share/covalent/workflow_db.sqlite"
    storage_type = "local"
    base_dir = "/Users/voldemort/.local/share/covalent/workflow_data"

    [user_interface]
    address = "localhost"
    port = 48008
    log_dir = "/Users/voldemort/.cache/covalent"
    dispatch_db = "/Users/voldemort/.cache/covalent/dispatch_db.sqlite"

    [executors.local]
    log_stdout = "stdout.log"
    log_stderr = "stderr.log"
    cache_dir = "/Users/voldemort/.cache/covalent"

    [executors.dask]
    log_stdout = "stdout.log"
    log_stderr = "stderr.log"
    cache_dir = "/Users/voldemort/.cache/covalent"