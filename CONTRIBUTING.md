First Steps
===========

To get started contributing to Covalent, you should fork this repository for your own development. (Learn more about [how to fork a repo](https://docs.github.com/en/get-started/quickstart/fork-a-repo).)

Clone your fork locally:

```shell
git clone https://github.com/my-github/covalent
```

where `my-github` is your personal GitHub account.

We recommend using [Conda](https://www.anaconda.com/) to create an environment to install and develop Covalent. After you have [installed](https://docs.anaconda.com/anaconda/install/index.html) `conda`, create an environment:

```shell
conda create -n covalent-dev python=3.8
conda activate covalent-dev
```

Install Covalent's core requirements as well as the developer requirements:
```shell
conda config --add channels conda-forge
conda config --set channel_priority strict
conda install setuptools pip nodejs yarn requests
python setup.py webapp
pip install -e .
pip install -r tests/requirements.txt
pre-commit install
```

Start the Covalent servers in developer mode:
```shell
covalent start -d
```

:bulb:*Note*
We have seen `OSError: protocol not found` when running Covalent in development mode for the first time on some Debian based systems. Running this command may fix the problem.
```
apt-get -o Dpkg::Options::="--force-confmiss" install --reinstall netbase
```
See more information on [Stackoverflow](https://stackoverflow.com/questions/65745342/oserror-protocol-not-found).

Check the [writing tests](#writing-tests) section for more details on installing test specific packages. Finally, run the tests to verify your installation:
```shell
pytest -v
```

Getting started with feature development
========================================

Note that for complex issues, planning out the implementation details (on the issues page) is a very important step before writing any code in the feature branch. The feature development steps are listed below.

### Create and checkout the feature branch

Once an issue has been assigned to you, create a feature branch to implement the proposed changes. When beginning implementation on an issue, first create a branch off of develop:

```bash
git branch branch_name develop
```

To checkout the branch:

```bash
git checkout branch_name
```

The two commands can be combined into:

```bash
git checkout -b branch_name develop
```

### How and when to open a Pull Request

Pull requests should be done as soon as the implementation on an issue has started on the feature branch. (Learn more about [how to open a pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request).)

### Linking Pull Request to issue number

In order to link a Pull Request to a given issue number, the first commit should be accompanied with a comment containing the issue number, for example:

```bash
git commit -m 'fixes #57'
```

This could also be done manually on the Pull Request page using the `Linked issues` button (Learn more about [linking a pull request to an issue](https://docs.github.com/en/issues/tracking-your-work-with-issues/linking-a-pull-request-to-an-issue)).

### Tag reviewers

Once the changes in the feature branch are ready to be reviewed, tag the relevant reviewer(s) on the Pull Request page.

### Merging the feature branch to develop

If all the reviewers have approved the Pull Request and all the actions have passed, the last person to review the branch is responsible for merging the feature branch to develop.

Style Guide
===========

Contributing to the Covalent codebase should be an easy process, but there are a few things to consider to ensure your contributions meet the minimum software quality standards. The main points are explained below, and they are roughly grouped into the following categories: stylization, documentation, and testing.

## General Guidelines
-   Use American English spellings and grammar.  Documentation with typos will be rejected.
-   Use complete sentences with capitalization and punctuation, except in short descriptions of arguments, return values, attributes, and exceptions in source code.
-   Multi-sentence argument descriptions, or longer sentence fragments with mid-sentence punctuation marks, should use capitalization and punctuation.
-   Comments may be written more informally than docstrings, as long as consistency and clarity are maintained. Capitalization and punctuation should be used with multi-sentence comments to aid with readability.
-   Avoid complex stylization in docstrings; these must be readable for users in a terminal/Jupyter environment.
-   Assume the user does not have access to any source files.
-   Variables must be restricted to the scope in which they are used; avoid use of global variables except when absolutely necessary.
-   Limit all lines to 99 characters.  Use a four-character indent for Python files; bash files use a two-character indent, and C uses a tab indent. These will be adjusted as needed by the pre-commit hooks.
-   A pre-commit hook, `detect-secrets` would run for detecting secrets based on `.secrets.baseline` file. To create a new `.secrets.baseline` file run `detect-secrets scan` command.  Refer to file `.pre-commit-config.yaml` file for the additional filters used and [detect-secrets repo](https://github.com/Yelp/detect-secrets#quickstart) for detailed documentation.
-   Input parameters to scripts should be passed using flags, rather than positional arguments. This may be implemented using the `getopt` libraries.  Bash scripts may accept parameters passed with or without flags.
-   Functions should perform a single task.  Generally functions should not contain more than 30 lines of code, not including line breaks, comments, and whitespace.
-   Use the `pylint` tool to improve the quality of your code. Contributions which decrease the codebase's code quality will be rejected.
-   All changes must be documented in the [changelog](./CHANGELOG.md).
-   New features or changes to UX must include a usage description in the form of a [how-to guide](https://covalent.readthedocs.io/en/latest/how_to/index.html).
-   All software source files should contain the copyright boilerplate displayed below, which includes a docstring describing the purpose of the file.

## Source Code Boilerplate
All files submitted must contain the following before all other lines:

```python
# Copyright 2021 Agnostiq Inc.
#
# This file is part of Covalent.
#
# Licensed under the GNU Affero General Public License 3.0 (the "License").
# A copy of the License may be obtained with this software package or at
#
#      https://www.gnu.org/licenses/agpl-3.0.en.html
#
# Use of this file is prohibited except in compliance with the License. Any
# modifications or derivative works of this file must retain this copyright
# notice, and modified files must contain a notice indicating that they have
# been altered from the originals.
#
# Covalent is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the License for more details.
#
# Relief from the License may be granted by purchasing a commercial license.

"""Single-sentence description of the file."""
```

Bash files may contain the shebang `#!/usr/bin/env bash` on a line before the boilerplate.  Afterwards, the following should be written before the body of code:

```bash
set -eu -o pipefail
```

and files should end with an explicit exit code, e.g., `exit 0` indicates a successful exit.

## Naming Conventions
-   Class names use `CamelCase`
-   Functions, variables, filenames, and directories use `snake_case`
-   Constants use `SCREAMING_SNAKE_CASE`
-   Acronyms are a sequence of all-capitalized letters
-   Names should be descriptive and concise
-   Mathematical variables (“x”) may be used only when they are documented. This may be appropriate for standard variables used in literature.
-   Avoid using “I”, “l”, and “O” as variable names
-   Private objects and methods/functions of a class should start with an underscore, e.g., `self._variable` or `self._internal_function()`. A "private" class object is one that should not be used outside of the class definition. Unlike C++, Python has no way of stopping a user/developer from accessing or modifying any object in the class (hence the quotations around private). The underscore lets them know the object is for internal use only and that its internal usage could change without warning.

## References
-   Add references to other code units where applicable. Use the roles :class:, :func:, :attr:, :meth:, and :mod: so that Sphinx generates a cross-reference in generated documentation.
-   Add URL references to code taken from or inspired by code found online.
-   All digital references must specify a DOI, ISBN, arXiv ID, or URL, in that order of preference.
-   Add references to literature where applicable.  Academic journal articles should be in the following format:

```
A.B. Lastname1, C. Lastname2 and D. Lastname3. Title of Article. Jour. Abbrev. 1, 123456 (2021).
doi: 10.1001/abcdef
arXiv: quant-ph/000000
```

Standard journal abbreviations can be found [here](https://www.library.caltech.edu/journal-title-abbreviations).  In the above example, ‘1’ refers to the volume number, and ‘123456’ refers to the first page number of the article.  For six or more authors use the first author’s name followed by *et al.*  References to other material should follow the *apsrev4-1* bibliography style and generally follow the same stylization as that for articles.  The DOI, if one exists, should be on the first line following a reference; if an arXiv ID also exists it may be added on a line following the DOI.

## Python Docstrings

Docstrings should follow [Google style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings).

### Functions and Methods

```python
def func(arg1: <arg1_type>, arg2: <arg2_type>, arg3: <arg3_type> = "default_value", **kwargs) -> <return_type>:
    """Single sentence that summarizes the function.

    Multi-line description of the function (optional, only if necessary).

    Args:
        arg1: Description.
            Continuation line is indented if needed.
        arg2: Description.
        arg3: Description. Do not provide the default.
            value, as this is already present in the signature.

    Returns:
        Description of the return type and semantics.
        Continuation line is on the same indent level.

    Raises:
        <exception_type>: description

    .. seealso:: :func:`~.relevant_func`, :class:`~.RelevantClass` (optional)

    Example:
        Minimal example with 1 or 2 code blocks (required).
        .. code-block:: python

           myvalue = func(arg1, arg2, arg3)


    Usage Details:
        More complicated use cases, options, and larger code blocks (optional).

    Related tutorials:
        Links to any relevant notebook examples (optional).

    References:
        References to academic articles, books, or websites (optional).

        A.B. Lastname1, C. Lastname2 and D. Lastname3. Title of Article. Jour. Abbrev. 1, 123456 (2021).
        doi: 10.1001/abcdef
        arXiv: quant-ph/000000
    """
```

-   Relevant mathematical expressions should be formatted using inline latex and placed in the multi-line description.  Important or long equations may go on their own line.
-   Algorithmic functions should contain details about scaling with time and/or problem size, e.g., O(N); this information also goes in the multi-line description.
-   `<arg1_type>`, `<arg2_type>`, `<arg3_type>` and `<return_type>` are placeholders for the type hints of `arg1`, `arg2`, `arg3` and the return value.

### Classes

```python
class MyClass:
    """Single sentence that summarizes the class.

    Multi-line description of the class (optional, if required).

    Attributes:
        attr1: description
    """
```

-   Include public attributes here in the `Attributes` section, using the same formatting as a function's `Args` section.
-   Do not list methods in the class docstring.
-   Private attributes of a class do not need to be described in the class docstring. These are class objects that should not be used outside of the class definition.

### Variables
Variables may optionally be documented using a docstring below their definition:

```python
num_gates = {"CNOT": 17, "RY": 31}
"""dict[str, int]: Number of gates in wire 2"""
```

## Bash Docstrings

All bash scripts must begin by validating input parameters and offering a help string:

```bash
# This example uses two parameters: an integer and a string
if [ $# -eq 2 ] && [ $1 =~ '^[+-]?[0-9]+$' ] ; then
  var1=$1
  var2=$2
else
  echo "$(basename $0) [var1] [var2] -- short description of this script."
  echo "Longer help string and explanation of parameters."
  exit 1
fi

# Continue with the rest of the script
```

## Code Examples

-   You may assume that ‘covalent’ is imported as ‘ct’. All other imports must be specified explicitly.
-   For single line statements and associated output, use Python console syntax (pycon):

```python
>>> ct.dispatch(pipeline)(**params) # Dispatching a workflow returns a unique dispatch id.
'8a7bfe54-d3c7-4ca1-861b-f55af6d5964a'
```

-   Multi-line statements should use “...” to indicate continuation lines:

```python
>>> dispatch_ids = []
>>> params = [1, 2, 3, 4]
>>> for a in params:
...     dispatch_ids.append(ct.dispatch(pipeline)(a=a))
```

-   For larger, more complicated code blocks, use standard Python code-block with Python console syntax for displaying output:

```python
>>> @ct.electron
... def identity(x):
...     return x
...
>>> @ct.lattice
... def pipeline(a):
...     res = identity(a)
...     return res
...
>>> dispatch_id = ct.dispatch(pipeline)(a=1)
>>> result = pipeline.get_result(dispatch_id=dispatch_id)
>>> print(result)

Lattice Result
==============
status: COMPLETED
result: 1
inputs: {'a': 1}
error: None

start_time: 2022-01-24 04:13:00.667919+00:00
end_time: 2022-01-24 04:13:00.684457+00:00

results_dir: /home/user/covalent
dispatch_id: e4efd26c-240d-4ab1-9826-26ada91e429f
```

## Code Comments

-   Comments are used to explain the implementation or algorithm.  Assume the reader is a proficient programmer and understands basic principles and syntax.
-   Self-document code when possible.  Code should be clear and concise, flow logically, and be organized into stanzas according to what’s happening.  This helps avoid *unnecessary* comments.
-   Comments should occur directly above the code that is being described.  Use a single space between the "#" character and the start of text.

## Python Type Hints

Type hints should be used for input parameters in functions and classes, as well as for return values as well. The typing module should be used for several circumstances:

- When a parameter or return type is a container for multiple parameters.  Examples include a dict mapping strings to floats uses, `Dict[str,float]`, or a list of integers uses, `List[int]`

- Nested Types: A dict mapping an integer to a list of floats is written `Dict[int,List[float]]`

- If a parameter can be multiple types, use `Union`. E.g., if it can be a string **or** a list of strings **or** an integer, use `Union[str,List[str],int]`.

- If a parameter can be anything, use `Any`. This is more permissive than using `object`. Type checkers will ignore it completely.

- Optional parameters use `Optional`. E.g., an optional integer is written `Optional[int]`.

Any user-defined class type can be used in a type hint, but the class must have been imported beforehand.

Some examples of type hints in use:

```python
from typing import Union, List, Dict, Any, Optional

import MyClass

def some_function(some_variable: float,
                  some_index: int,
                  float_or_string: Union[float,str],
                  some_integer_list: List[int],
                  some_string_list: List[str],
                  my_class_object: MyClass, # This will fail if MyClass has not been imported
                  some_dict: Dict[int,str],
                  literally_anything: Any,
                  optional_string: Optional[str] = 'default string',
                  optional_int: Optional[int] = -1,
                  optional_int_or_string: Optional[Union[int,str]] = 9999
                  optional_int_list: Optional[List[int]] = [0,1,2,3]) -> Union[str,float,None]:

    """Function description

    Args:
        some_variable: some_variable description
        some_index: some_index description
        float_or_string: float_or_string description
        some_integer_list: some_integer_list description
        some_string_list: some_string_list description
        my_class_object: my_class_object description
        some_dict: some_dict description
        literally_anything: literally_anything description
        optional_string: optional_string description
        optional_int: optional_int description
        optional_int_or_string: optional_int_or_string description
        optional_int_list: optional_int_list description

    Returns:
        return_variable: return description
    """

    n = 5 * some_index

    if n == 20:
        return 'ok'
    elif n == 455:
        return n * 3.14159
    else:
        return
```

## Python Logging

Covalent uses the Python logging module for errors, warnings, debug and info statements. There is a small module (`covalent/_shared_files/logger.py`) which encapsulates the default logger. Modules can access the logger using the following:

```python
from covalent._shared_files import logger
app_log = logger.app_log
log_stack_info = logger.log_stack_info
log_debug_info = logger.log_debug_info
```

Warning, info and debug statements are done with the following commands:

```python
>>> app_log.warning('here is the warning message')
<file_name>: Line 8 in <function_name>:
WARNING - here is the warning message
>>> app_log.info('message for informational purposes')
<file_name>: Line 12 in <function_name>:
INFO - message for informational purposes
>>> app_log.debug('debug statement')
<file_name>: Line 15 in <function_name>:
DEBUG - debug statement
```

where `<file_name>` and `<function_name>` are stand-ins for the file and function that the log statement occurred in.

For more urgent messages, denoting errors which will stop the program from executing correctly, use error statements. Usage is similar, except that we want the program to exit and optionally show a stack-trace pointing to the error.

The level of warning seen when executing code depends on the user's environment variable `LOGLEVEL`. Choices are:


|Level|Numeric value|
|-----|-------------|
|CRITICAL|50|
|ERROR|40|
|WARNING|30|
|INFO|20|
|DEBUG|10|
|NOTSET|0|

The lower the level, the more log messages are shown to the user. Executing, for example,

```
export LOGLEVEL=INFO
```

guarantees all info, warning, error and critical messages will be shown. If this environment variable is not set, the default value of `WARNING` is used.

## Writing Tests
All feature changes and bug fixes should be accompanied by tests. The bulk of the tests in the repo should be unit tests as opposed to functional or integration tests. A short definition of each type of test:

1. Unit tests - the scope of unit tests are usually at a functional level, i.e. given an input, check if the output is as expected. Furthermore, care needs to be taken to mock other functions, context managers, I/O tasks within the function that is being tested.
2. Integration tests - the scope of integration tests varies from a functional to module level. Here, we also test that functions or methods behave in certain ways given an input without mocking some of the other functions. The objective is to test how different functions / modules behave when "integrated".
3. Functional tests - the scope of these tests are on a user experience level. The purpose here is to ensure that commonly defined software use cases leads to expected behaviour / output (without encountering runtime errors etc.) for a given input.


Below, we list some important guidelines when writing tests.

* **Write unit tests as opposed to integration or functional tests (unless there's a really good reason for it).**

* In the case of bug fixes, write tests for which the code breaks before implementing the bug fix.

When writing tests, consider the following questions as guiding principles:

1. Are these tests easily maintainable as the code is updated over time? - Try to minimize the number of tests that would need to be modified when an implementation is changed.
2. Are these tests lightweight, i.e. not resource or time intensive? - Try to minimize test runtime and the number of operations that are carried out.
3. Are these tests going to be helpful for debugging when a feature is added or modified?

### Installing test packages
When it comes to testing, `pytest` is the recommended framework for this repository. Install all testing related packages with the following step:

1. Navigate to the `tests` folder in the Covalent root directory.
2. Run `pip install -r requirements.txt`.

### Running tests locally

The Covalent test suite can be run locally from the root directory with `pytest` (add the tags `-vv -s` for a more verbose setting).

Running the entire test suite everytime the code has been updated will take a while. The following commands are useful to hone in on a smaller subset of tests for development purposes.

1. To run a specific test module:
```bash
pytest tests/covalent_dispatcher_tests/_executor/local_test.py -vv -s
```

2. To run a specific test:

```bash
pytest tests/electron_return_value_test.py::test_arithmetic_1_rev -vv -s
```

Note: In order to run some of the functional tests (which will eventually be deprecated), the covalent dispatcher needs to be started in developer mode (discussed in _First Steps_ section).

### Mocking

Mocking is a very important part of writing proper unit tests. Scenarios where mocking is essential are listed below:

1. Making server calls.
2. Reading and writing to files.
3. Getting environment variable values.
4. Getting file or directory paths.
5. If a function A is composed of functions B and C, the calls to functions B and C should be mocked. This ensures maintainability, since changes to functions B would then only require us to update the test for function B (instead of both A and B).

Check out the official [pytest documentation](https://pypi.org/project/pytest-mock/).

#### Mocking via `mocker`

Some important commands to know about:

1. `mocker.patch` - allows mocking function calls, return values etc.
2. The previous command combined with the parameter `side_effects` allows mocking return values for multiple calls of the mocked function. Furthermore, it allows mocking the outcome of `try / except` clauses.
3. Some other commands used to check if a mocked function (`mocked_func`) has been called or called with particular arguments once are `mocked_func.assert_called_once()`, `mocked_func.assert_called_once_with(..)`.
4. If a mocked function has been called multiple times within a function, it can be checked via `mocked_func.mock_calls`. Check out this [discussion](https://stackoverflow.com/questions/59839192/python-pytest-mock-assert-has-calls) on stackoverflow.
5. Check out this [discussion](https://stackoverflow.com/questions/28850070/python-mocking-a-context-manager) on mocking context managers (such as `with open(..):` etc.).

#### Mocking via `monkeypatch`

This module can be used to mock module variables, environment variables etc. Check out the official [monkeypatch documentation](https://docs.pytest.org/en/6.2.x/monkeypatch.html).


## Covalent with Docker

This repository contains a Dockerfile that can be used in a variety of ways for development and deployment. Note that we use the Dockerfile 1.4 syntax which requires BuildKit. For most users, it is sufficient to set the environment variable `DOCKER_BUILDKIT=1` before attempting to build images. All of the examples below use build arguments and target stages referenced in the Dockerfile. For a full list of build arguments, run `grep ARG Dockerfile`.

### Covalent Server

The Covalent server can run inside a container. Build this container using the default options:

```shell
docker build --tag covalent-server:latest .
```

It is recommended a date and version are included using build arguments whenever an image is build. This can be done by including these options:

```shell
--build-arg COVALENT_BUILD_DATE=`date -u +%Y-%m-%d` --build-arg COVALENT_BUILD_VERSION=`cat ./VERSION` --tag covalent-server:`cat ./VERSION`
```

### Covalent SDK

The Covalent SDK can also run inside a container. This is useful in scenarios where containerized tasks use Covalent, e.g., in executor plugins.  Build the container using these options:

```shell
docker build --build-arg COVALENT_INSTALL_TYPE=sdk --tag covalent-sdk:latest .
```

### Development Images

By referencing an intermediate build target, we can also generate a build environment that can be used for developing Covalent:

```shell
# Does not include Covalent source
docker build --tag covalent-build:latest --target build_server .

# Includes Covalent source
docker build --tag covalent-dev:latest --target covalent_install .
```

### Selecting a Covalent Source

Different circumstances will require Covalent coming from different sources. The build arguments can be leveraged to specify either a local source, a PyPI release, or a commit SHA checked into GitHub. The default source is local, i.e., it uses the Covalent source code next to the Dockerfile.

```shell
# PyPI Release
--build-arg COVALENT_SOURCE=pypi --build-arg COVALENT_RELEASE=0.202.0.post1

# GitHub Commit
--build-arg COVALENT_SOURCE=sha --build-arg COVALENT_COMMIT_SHA=abcdef
```

### Custom Base Image

Finally, users can specify a custom base image, which can be useful when users are trying to incorporate Covalent SDK or Server into their existing tech stack:

```shell
--build-arg COVALENT_BASE_IMAGE=<my_registry.io>/<my_image>:<my_tag>
```

Note that the base image must include a compatible version of Python and must be based on either Ubuntu or Debian.

Building Read the Docs (RTD) locally
====================================

Contributing to the Covalent documentation is highly encouraged. This could mean adding How-To guides, tutorials etc. The steps required to build the RTD locally are listed below:

#### Installation

Navigate to the `/covalent/doc` folder and install the packages to build the documentation:

```bash
pip install -r requirements.txt
```

Note that some additional packages might need to be installed as well, depending on the operating system.

#### Building the docs

Navigate to the root folder (`/covalent/`) of the repo and run:

```bash
python setup.py docs
```

When running this command for the first time some users might get a `pandoc missing` error. This can be resolved via:

```bash
pip install pandoc
```

In case `pandoc` is not installed via above, follow the installation instructions provided [here](https://pandoc.org/installing.html).

#### Viewing the locally built RTD

In order to view the local RTD build, navigate to the `/covalent/doc/build/html` folder. Left click on `index.html` file and copy the path. Paste the path into the browser to access the RTD that was built locally.

#### Cleaning the doc build

The local RTD build can be cleaned using:

```bash
python setup.py docs --clean
```

Contributor License Agreement
=============================

All contributors to Covalent must agree to the terms in the [Contributor License Agreement](https://gist.github.com/wjcunningham7/3f21c684fc60c7598e0fe711caeb9ac1). Individual contributors should sign on their own behalf, while corporate contributors should sign on behalf of their employer. If you have any questions, direct them to the [support team](mailto:support@agnostiq.ai).
