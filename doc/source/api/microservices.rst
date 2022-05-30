*********
Microservices
*********


.. note::

  This documentation is for debugging and/or extending the functionality of Covalent.


===========================================
Architecture
===========================================

Covalent is composed of a set of services which expose APIs. These services interact in a way that allows Covalent to perform well at scale.

The services can be started as local processes managed by supervisord or as containers. When you run :code:`covalent start`, this starts supervisord which in turn runs the services on the ports defined in the local environment, either in :code:`covalent/.env.example` or your OS. Supervisord can be managed via a dashboard which by default is running on :code:`localhost:9001`.

:code:`docker-compose up --build` will build and run the containers. This can be done locally for development, although we recommend using :code:`covalent start` for local execution. Running the services in containers is designed for cloud environments and other distributed networks.

When you run :code:`covalent start` or :code:`covalent status`, Covalent will output the process IDs for each service. These can be used to find the host for each service's REST API. While normal operation wraps the REST API in a convenient Python SDK, the APIs can be queried directly. Here is an example showing the results API.

.. code:: console

   $ covalent status
   Supervisord is running in process 68432.
   covalent:data                     RUNNING   pid 68441, uptime 0:39:19
   covalent:dispatcher               RUNNING   pid 68439, uptime 0:39:19
   covalent:dispatcher_mq_consumer   RUNNING   pid 68444, uptime 0:39:19
   covalent:nats                     RUNNING   pid 68445, uptime 0:39:19
   covalent:queuer                   RUNNING   pid 68437, uptime 0:39:19
   covalent:results                  RUNNING   pid 68443, uptime 0:39:19
   covalent:runner                   RUNNING   pid 68440, uptime 0:39:19
   covalent:ui                       RUNNING   pid 68442, uptime 0:39:19

   $ lsof -i -P -n | grep LISTEN | grep 68443
   python3.8 68443 scott    4u  IPv4 0xad8e4edd50d4985      0t0  TCP 127.0.0.1:8005 (LISTEN)
   $ curl http://127.0.0.1:8005/api/v0/workflow/results | jq
     % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                      Dload  Upload   Total   Spent    Left  Speed
   100 22871  100 22871    0     0   101k      0 --:--:-- --:--:-- --:--:--  102k
   [
     {
       "dispatch_id": "2f9ddacd-c716-48c3-af5a-64c987a56932",
       "status": "COMPLETED",
       "result": 9,
       "start_time": "2022-04-19T19:01:38.819209+00:00",
       "end_time": "2022-04-19T19:01:52.617791+00:00",
       "results_dir": "/private/tmp",
       "error": null,
       "lattice": {
         "function_string": "@ct.lattice\ndef workflow(a):\n\n    task_3()\n\n    for _ in range(5):\n        task_2(a, 10)\n\n    return task_1(a)\n\n\n",
         "doc": null,
         "name": "workflow",
         "inputs": "{'args': [3], 'kwargs': {}}",
         "metadata": {
           "executor": {
             "log_stdout": "stdout.log",
             "log_stderr": "stderr.log",
             "cache_dir": "/Users/scott/.cache/covalent",
             "conda_env": "",
             "current_env_on_conda_fail": "False",
             "current_env": ""
           },
           "results_dir": "/private/tmp",
           "notify": [],
           "executor_name": "<LocalExecutor>"
         }
       },
   .
   .
   .


The services are as follows:

- :ref:`data_api`
- :ref:`queuer_api`
- :ref:`dispatcher_api`
- :ref:`runner_api`
- :ref:`results_api`
- :ref:`ui_backend_api`
- :ref:`nats`


.. image:: ./../_static/Covalent_Local_Microservices.png
   :width: 737
   :align: center


.. _data_api:

Data API
"""""""""""""""""""""""""""
The Data API documentation is located in `here <https://app.swaggerhub.com/apis/agnostiq/Covalent_Data_Service_API/0.1.0>`_

.. _queuer_api:

Queuer API
"""""""""""""""""""""""""""
The Queuer API documentation is located in `here <https://app.swaggerhub.com/apis/agnostiq/Covalent_Queue_Service_API/0.1.0>`_

.. _dispatcher_api:

Dispatcher API
"""""""""""""""""""""""""""
The Dispatcher API documentation is located in `here <https://app.swaggerhub.com/apis/agnostiq/Covalent_Dispatcher_Service_API/0.1.0>`_

.. _runner_api:

Runner API
"""""""""""""""""""""""""""
The Runner API documentation is located in `here <https://app.swaggerhub.com/apis/agnostiq/Covalent_Runner_Service_API/0.1.0>`_


.. _results_api:

Results API
"""""""""""""""""""""""""""
The Queuer API documentation is located in `here <https://app.swaggerhub.com/apis/agnostiq/Covalent_Data_Service_API/0.1.0>`_

.. _ui_backend_api:

UI Backend API
"""""""""""""""""""""""""""
The UI Backend API documentation is located in `here <https://app.swaggerhub.com/apis/agnostiq/Covalent_UI_Service_API/0.1.0>`_

.. _nats:

NATS Message Queue
"""""""""""""""""""""""""""
The `NATS Message Queue <https://nats.io/>`_ is a message queue that acts as a message bus between the microservices.
