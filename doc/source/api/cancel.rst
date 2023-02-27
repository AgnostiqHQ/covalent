.. _cancel:

Overview
==========

Covalent users or admins may wish to cancel dispatches or individual tasks from a dispatch as per their requirements. For instance, under a self-hosted scenario if a dispatch has consumed more than the allocated cloud resources budget it should be canceled. Given that Covalent supports multi-cloud execution with its executor plugins, canceling a task involves the following actions

* Canceling tasks
  * Canceling a task may imply canceling the job being executed by a executor using remote cloud/on-prem resources
  * Interrupt the executor processing the job immediately. For instance, if a job's dependencies such as pickle callable, arguments and keyword arguments are uploaded but the backend has not yet started executing it, abort right away and do not provision any compute resources

* Canceling dispatches
    * When a dispatch is canceled, cancel all tasks that are part of the dispatch immediately. Any tasks currently being processed will be killed immediately and any unprocessed tasks will be abandoned.
    * Cancel all post-processing task


To cancel a dispatch, the UX is quite straightforward. To cancel an entire workflow, users only need to know the ``dispatch_id`` of their workflow and invoke the cancellation as follows

.. code:: python

   import covalent as ct

   dispatch_id = ct.dispatch(workflow)(args, kwargs)

   # cancel the workflow
   ct.cancel(dispatch_id)
