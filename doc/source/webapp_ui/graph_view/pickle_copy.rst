.. _pickle_copy:

Copying Python Objects from the UI
----------------------------------

Some fields in the Graph View are copyable as string-serialized Python objects. These copyable Python objects include the Input and Result fields in the Lattice Sidebar and the Electron Sidebar, and are identified by the message *Copy python object* when you mouse over the field.

To copy a Python object field, mouse over the field and click. The object is copied as a byte stream wrapped in a :code:`pickle.loads()` statement. To view the data object, paste the string into a Python interpreter or notebook and execute it.

.. note:: The Python environment in which you view the pickled data structure must contain all packages on which it depends. 

For example, the following string was copied from a simple input in the Covalent GUI Electron Sidebar Input text field:

.. code:: Python

    import pickle
    pickle.loads(b'\x80\x05\x95\x1f\x00\x00\x00\x00\x00\x00\x00}\x94(\x8c\x04args\x94\x8c\x03100\x94\x85\x94\x8c\x06kwargs\x94}\x94u.')

Executing the string in a Jupyter notebook yields the input as displayed in the Input text field:

.. code:: Python

    {'args': ('100',), 'kwargs': {}}

.. note:: This might seem like unnecessary extra work for such a simple data structure. For complex  data structures, however, using the pickled object is less error-prone than trying to copy and paste the text representation. An example of such a complex data structure is the :code:`construct_cu_slab` result in `this example <https://demo.covalent.xyz/eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a>`_. The example, an atomicistic simulation, requires the :code:`ase` package.
