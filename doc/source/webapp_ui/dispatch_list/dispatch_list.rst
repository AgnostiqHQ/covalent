=======================
Workflow Dispatch List
=======================

A typical dispatch list is shown below.

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
    The status of a dispatch. The four possible statuses are:

    Pending
        Not yet running due to scheduling or resource availability.
    Running
        Started, with one or more tasks handed off to executors.
    Failed
        Finished with one or more tasks throwing an error.
    Completed
        Finished with all tasks successful.
