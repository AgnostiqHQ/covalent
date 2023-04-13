##########
Server Log
##########

To view the Covalent server log, click the |logs| icon.

.. image:: ../images/logs_list.gif
   :align: center

Each log entry represents a single event; most are one line but some (such as tracebacks) are multi-line. An entry contains the following columns:

Time
    The time and date of the log entry. Time format for time and date are hh:mm:ss,ms and yyyy-mm-dd.

Status
    The status of the log entry, indicating the severity of the event. The available statuses are: INFO, DEBUG, WARNING, ERROR, and CRITICAL.

Messages
    The log message. Click on a log message to copy it to the clipboard. In the case of a multi-line message, all lines are copied.

.. |logs| image:: ../images/logs_icon.png
    :width: 20px

Log Navigation
--------------

The following navigation tools are available for the Covalent server log:

* :doc:`search`
* :doc:`pagination`
* :doc:`sort`

Download
--------

.. image:: ../images/logs_download.gif
   :align: center

Click |download| to download the Covalent server log as a text file.

.. |download| image:: ../images/download.png
    :width: 20px
