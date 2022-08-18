.. currentmodule:: covalent_dispatcher

.. _dispatcher_server_api:

Covalent CLI Tool
""""""""""""""""""

This Command Line Interface (CLI) tool is used to manage Covalent server.

.. click:: covalent_dispatcher._cli.cli:cli
    :prog: covalent
    :commands: start,stop,restart,status,purge,logs,cluster
    :nested: full
