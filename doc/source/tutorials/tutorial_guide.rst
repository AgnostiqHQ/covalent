****************************
Tutorial Writing Guide
****************************

This guide covers best practices for Covalent tutorials. These principles are indended to guide but not constrain the author.

Set the scope
-------------

Good tutorials are small and self-contained. They do not overcomplicate things and cater to a mixed audience. Any examples highlighted should be straightforward and friendly to beginners.

Introduce the example
---------------------

Introduce background material and describe what we will be trying to achieve in the tutorial. Separate the logical components and show what purpose each of them serves.

Prototype the solution
----------------------

Write code with commented explanations wherever necessary. Write it without Covalent, in a functional manner, where it is clear what each of the components is doing in the context of the example.

Run the workflows
-----------------

Add decorators to the functions without changing their definitions. Show representative screenshots of the UI to help readers understand the problem being solved. A good tutorial also provides typical input parameters and the corresponding typical runtimes.

Analyze the results
-------------------

View the results in the Covalent UI, and query them programatically as well.  Summarize the findings using a meaningful plot or chart. Discuss the metadata returned in the result object.


Discuss the concepts
--------------------

Highlight how different components of Covalent are used to accomplish objectives or to obey constraints.
