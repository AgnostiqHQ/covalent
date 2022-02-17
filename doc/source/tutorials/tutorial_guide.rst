****************************
Tutorial Writing Guide
****************************

This guide will cover things that should be taken care of while writing tutorials for Covalent. It can also be seen as a way to highlight covalent's strenghts in real world projects.

.. note:: This is a basic structure and can be modified depending on what kind of tutorial is being written. Since it is not a full-fledged template it gives the author some leeway to write however they deem the tutorial fit.

===========
Readability
===========

First and foremost, the tutorial should be small enough to not overcomplicate things which will discourage newcomers from reading it.
Whatever example is chosen, should be straightforward and beginner friendly.


=======================
Introducing the example
=======================

Describe what we will be trying to achieve. Separate the components and show what each of them will do.


================
Without Covalent
================

Write code with commented explanations wherever necessary. This time we will be writing it without covalent in a functional manner, where it is clear what each of the components is doing.



Results
-------

Run the code, benchmark, and show how much time it took. Also show the changes to the code that we'll need to do in order to a) see the execution time, b) get the error if any of the components failed, c) track the status of each component, d) execute the independent components in parallel, etc.


=============
With Covalent
=============

Add decorators to those functions without changing their definitions. Show the the UI which they can use to track all of the above mentioned information. Also, indicate that the user can continue working on something else instead of waiting for the result. This can be done by running a trivial code snippet in the following cell after dispatching the job.



Results
-------

Do ct.get_result, and indicate that they didn't have to do anything extra in order to get all of the above information about the execution which can be found inside a single result object.


=================
Covalent Concepts
=================

Highlight what each covalent's component's role and importance in executing the example.
