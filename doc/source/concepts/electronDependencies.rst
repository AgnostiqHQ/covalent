.. _Workflow electron dependencies:

=====================
Electron Dependencies
=====================
The installation of an electron's dependencies is managed within the electron's execution environment. In essence, one can specify different types of dependencies in an electron which will be installed or executed in the electron's backend execution environment.

~~~~~~
Deps
~~~~~~
:code:`Deps` is an ABC class for managing any kind of electron dependency. Other kinds of dependencies inherit attributes of the :code:`Deps` class and override its  :code:`__init__()` and :code:`apply()` methods.

:code:`:__init__()`: The :code:`__init__()` method is the constructor that takes in variables
including :code:`apply_fn` which is the callable function to be applied in the backend environment and a set of :code:`args` and :code:`kwargs`.
When a :code:`Deps` object is initialized, the :code:`apply_fn`, :code:`args`, and :code:`kwargs` are serialized into transportable objects.

:code:`:apply()`: The :code:`:apply()` function returns a :code:`Tuple` containing serialized copies of :code:`apply_fn`, :code:`args` and :code:`kwargs`.

The following kinds of dependencies are supported at the electron level:

* DepsPip - used in managing pip dependencies in an electron.
* DepsBash - used in managing bash dependencies in an electron.
* DepsCall - used in managing functions that are called before or after executing an electron.

~~~~~~~
DepsPip
~~~~~~~
:code:`DepsPip` is the class that is responsible for managing the list of required PyPI packages which have to be installed in the backend environment prior to executing the electron.

:code:`__init__()`: The :code:`__init__()` constructor of :code:`DepsPip` takes a list of required PyPI packages and/or a path to the file that contains the list of required PyPI packages. It overrides :code:`Deps`'s :code:`__init_()` by
using :code:`apply_pip_deps` which is a callable that installs the required PyPI packages.

Below is an example of using :code:`DepsPip` to specify a list of PyPI packages in an electron::

    import covalent as ct
    from covalent import DepsPip

    @ct.electron(
        deps_pip=DepsPip(packages=["numpy==0.23", "qiskit"]),
    )
    def task():
    ...

Alternatively, one can specify the path to a :code:`requirements.txt` file that contains the list of required packages.
Assuming the path to the file is :code:`/usr/foo/requirements.txt`::

    @ct.electron(
        deps_pip=DepsPip(reqs_path="/usr/foo/requirements.txt")
    )

~~~~~~~~
DepsBash
~~~~~~~~

:code:`DepsBash` is the class that is responsible for managing the execution of bash commands that are required by an electron.

:code:`__init_()`: The :code:`__init__()` constructor of :code:`DepsBash` accepts a list of bash commands as its argument.
It overrides :code:`Deps`'s :code:`__init__()` by accepting :code:`apply_bash_commands` which is the callable that executes the commands and :code:`apply_args`
which references the specified list of commands.

:code:`apply_bash_commands`: This takes the list of commands and executes them as subprocesses in the same environment as the electron.

Below is an example of using :code:`DepsBash` to specify a list of bash commands in an electron::

    import covalent as ct
    from covalent import DepsBash

    @ct.electron(
        deps_bash=DepsBash(["echo $PATH", "ssh foo@bar.com"]),
    )
    def task():
    ...

~~~~~~~~
DepsCall
~~~~~~~~

:code:`DepsCall` is the class that is responsible for managing Python functions and other electron dependencies that need to be invoked in the same backend environment as the electron.
It also functions as a parent class for :code:`DepsBash`, :code:`DepsPip`, and :code:`Deps` and can apply those dependencies before or after the electron's execution.

:code:`__init__()`: :code:`DepsCall` :code:`__init__()` constructor takes in :code:`func` which is a callable
that is invoked in the electron's environment. It also takes a list of :code:`args` and :code:`kwargs`
which are passed as arguments when overriding the parent :code:`Deps` class.

Below is an example of using :code:`DepsCall` to declare functions that are called before and after an electron is executed::

    import covalent as ct
    from covalent import DepsCall

    def execute_before_electron():
    ...

    def shutdown_after_electron():
    ...

    @ct.electron(
        call_before=DepsCall(execute_before_electron, args=[1, 2])
        call_after=DepsCall(shutdown_after_electron),
    )
    def task():
    ...

Another example shows hows to pass :code:`DepsBash` objects to :code:`call_before` and :code:`call_after`::

    from covalent import DepsBash

    @ct.electron(
    call_before=DepsBash("cp file.txt target_directory/"),
    call_after=DepsBash("cp target_directory/file.txt  ."),
    )
    def task():
    ...

*Note*: It's also possible to implicitly declare multiple kinds of dependencies in an electron::

    import covalent as ct
    from covalent import DepsPip, DepsBash, DepsCall

    def execute_before_electron(a, b):
    ...

    def shutdown_after_electron():
    ...

    @ct.electron(
        deps_pip=DepsPip(packages=["numpy==0.23", "qiskit"]),
        deps_bash=DepsBash(commands=["echo $PATH", "ssh foo@bar.com"]),
        call_before=DepsCall(execute_before_electron, args=(1, 2)),
        call_after=DepsCall(shutdown_after_electron),
    )

Alternatively, one can explicitly specify each kind of dependency::

    @ct.electron(
        deps_pip=["numpy==0.23", "qiskit"]
        deps_bash=["echo $PATH", "ssh foo@bar.com"]
        call_before=[execute_before_electron, (1, 2)],
        call_after=[shutdown_after_electron],
    )
    def task():
    ...

Lastly, one can directly apply other types of :code:`Deps` in the electron's environment by passing them as variables to :code:`call_before` and :code:`call_after`::

    import covalent as ct
    from covalent import DepsPip, DepsBash, DepsCall

    deps_pip=DepsPip(packages=["numpy==0.23", "qiskit"]),
    deps_bash=DepsBash(commands=["echo $PATH", "ssh foo@bar.com"])

    @ct.electron(
        call_before=[deps_pip, deps_bash],
        call_after=[shutdown_after_electron],
    )
    def task():
    ...
