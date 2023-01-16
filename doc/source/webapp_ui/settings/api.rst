###
SDK
###

Use the SDK Settings page to view and change SDK-related preferences.

.. image:: ../images/sdk.png
  :align: center

.. note:: You must restart Covalent for changes on this page to take effect.

Config File
    The configuration file for all settings. Defaults to `/Users/mini-me/.config/covalent/covalent.conf`. We recommend not editing or moving this file; changes could cause unexpected behavior or errors.
Log Directory
    The directory path containing Covalent's log file.
Log Level
    Select the minimum logging level of SDK-related events to log.
Enable Logging
    Turn SDK logging on (True) or off (False).
Executor Directory
    The directory path containing remote executor plugin modules used by the SDK.
No Cluster
    Turn Dask clustering on (False) or off (True). With No Cluster set to True, the default executor is local.
