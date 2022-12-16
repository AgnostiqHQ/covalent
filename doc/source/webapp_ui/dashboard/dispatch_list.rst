=======================
Workflow Dispatch List
=======================

A filterable, sortable list of all dispatches in the Covalent server database. A typical dispatch list is shown below.

.. image:: ../images/dispatches_with_appropriate_metadata.png
   :align: center

Each line represents one dispatch, and contains the following information:

Dispatch ID
    The unique dispatch ID for the workflow invocation. This ID is used to identify the dispatch in the SDK.
Lattice
    The name of the dispatched lattice function.
Runtime
    The approximate run time of the dispatch.
Started
    The local time when a dispatch started.
Ended
    The local time when a dispatch ended (completed or failed). A dash is displayed while the dispatch is Running.
Status
   The status of a dispatch. The possible statuses are:

   Pending
        Not yet running due to scheduling or resource availability.
   Running
        Started, with one or more tasks handed off to executors.
   Failed
        Finished with one or more tasks throwing an error.
   Cancelled
        The dispatch was shut down before completion.
   Completed
        Finished with all tasks successful, and postprocessing is complete.
   Pending Postprocessing
        The dispatch has finished running, but postprocessing tasks defined for the dispatch have not started yet.
   Postprocessing
        The postprocessing tasks defined for the dispatch are running.
