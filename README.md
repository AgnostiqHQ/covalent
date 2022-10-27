&nbsp;

<div align="center">

<img src="https://raw.githubusercontent.com/AgnostiqHQ/covalent/master/doc/source/_static/covalent_readme_banner.svg" width=150%>

[![version](https://img.shields.io/github/v/tag/AgnostiqHQ/covalent?color=navy&include_prereleases&label=version&sort=semver)](https://github.com/AgnostiqHQ/covalent/blob/develop/CHANGELOG.md)
[![python](https://img.shields.io/pypi/pyversions/cova)](https://github.com/AgnostiqHQ/covalent)
[![tests](https://github.com/AgnostiqHQ/covalent/actions/workflows/tests.yml/badge.svg)](https://github.com/AgnostiqHQ/covalent/actions/workflows/tests.yml)
[![docs](https://readthedocs.org/projects/covalent/badge/?version=latest)](https://covalent.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/AgnostiqHQ/covalent/branch/master/graph/badge.svg?token=YGHCB3DE4P)](https://codecov.io/gh/AgnostiqHQ/covalent)
[![agpl](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0.en.html)

</div>

## What is Covalent?

Covalent is a Python-language – and [Pythonic(https://www.udacity.com/blog/2020/09/what-is-pythonic-style.html)] – workflow tool for computational scientists, AI/ML software engineers, and anyone who needs a way to run experiments on limited or expensive computing resources. Such resources can include quantum computers, HPC clusters, GPU arrays, and cloud services. Covalent manages workflows in heterogeneous environments that contain any or all of these advanced platforms.

Covalent enables you to:

Isolate operations that don't require advanced compute resources so you can run them on commonly available hardware.

> Covalent dispatches tasks to any number of executors backed by heterogeneous hardware platforms. Run non-critical tasks on commodity hardware, using advanced hardware only for the heavy computations: Using a heterogeneous environment is almost as easy as running with a monolithic backend.

Test individual functions or groups of functions on local hardware before committing them to advanced hardware.

> Not only does Covalent run different workflow tasks on different platforms; but reassigning a task to a different platform is as easy as changing a single attribute in a function decorator. Test locally, then do the real work on big hardware.

Iteratively run prototypes and exploratory research models and save results.

> Covalent saves the data required to reproduce every run of every workflow, along with its results. Manage running workflows, view task dependencies, and examine results in Covalent's intuitive browser-based UI.

Automate and manage workflows from a Jupyter notebook or any other interactive Python environment.

> The Covalent scheduler runs locally or on a server. Run experiments as you normally would, swapping parameters and datasets, from Jupyter or any other interactive Python environment.

Run experiments faster with parallel processing.

> Covalent automatically parallelizes independent tasks to accelerate job completion.

Ready to try it? Skip to [Getting Started](https://covalent.readthedocs.io/en/latest/getting_started/index.html)

Covalent is designed and developed from the ground up for data experimentation and prototyping. Covalent features:

Pure Python

> Covalent automatically constructs complex workflows when you program with native Python functions. Make your code Covalent-ready simply by adding one-line decorators to your functions.

A robust user interface

> Covalent provides an intuitive and aesthetic browser-based UI to monitor and manage your workflows.

Result management

> Covalent manages the results of your workflows. Whenever you need to modify parts of your workflow, from inputs to components, Covalent stores and saves the run of every experiment in a reproducible format.

Low overhead

> Covalent is designed to be as lightweight as possible and is optimized for the most common use cases. Covalent's overhead is less than 0.1% of the total runtime for typical high-compute applications and often has a constant overhead of ~ 10-100μs – and this is constantly being optimized.

Interactive

> Unlike other workflow tools, Covalent is interactive. You can view, modify, and re-submit workflows directly within a Jupyter notebook.

Ready to try it? Skip to [Getting Started](https://covalent.readthedocs.io/en/latest/getting_started/index.html)

## Is It Really That Easy?

Don't be fooled the simplicity of Covalent's decorator-based code syntax. Each decorator is a wrapper hiding sophisticated task management software that analyzes function input and output and enables the Covalent server to abstract the code from the backend implementation.

You do have some responsibilities when you use a Covalent decorator. Your code should be task-oriented and Pythonic. Task-oriented, because the more you use small, independent, single-purpose tasks, the more efficiently Covalent can manage your workflow. Long, shambolic scripts are not a good candidate for Covalent scheduling – at least not without refactoring.

Pythonic, because using Python best practices enables Covalent to automatically construct workflow graphs without having to specify graph edges explicitly in another language such as YAML.
</div>

For a more in-depth description of Covalent's features and how they work, refer to the [Concepts](https://covalent.readthedocs.io/en/latest/concepts/concepts.html) page in the documentation.

## 📖 Example

Begin by starting the Covalent servers:

```console
covalent start
```

Navigate to the user interface at `http://localhost:48008` to monitor workflow execution progress.

In your Python code, it's as simple as adding a few decorators!  Consider the following example which uses a support vector machine (SVM) to classify types of iris flowers.

<table style='margin-left: auto; margin-right: auto; word-wrap: break-word;'>
<tr>
<th style='text-align:center;'>Without Covalent</th>
<th style='text-align:center;'>With Covalent</th>
</tr>

<tr>
<td valign="top">

``` python
from numpy.random import permutation
from sklearn import svm, datasets

def load_data():
    iris = datasets.load_iris()
    perm = permutation(iris.target.size)
    iris.data = iris.data[perm]
    iris.target = iris.target[perm]
    return iris.data, iris.target

def train_svm(data, C, gamma):
    X, y = data
    clf = svm.SVC(C=C, gamma=gamma)
    clf.fit(X[90:], y[90:])
    return clf

def score_svm(data, clf):
    X_test, y_test = data
    return clf.score(
    	X_test[:90],
	y_test[:90]
    )

def run_experiment(C=1.0, gamma=0.7):
    data = load_data()
    clf = train_svm(
    	data=data,
	C=C,
	gamma=gamma
    )
    score = score_svm(data=data, clf=clf)
    return score

result=run_experiment(C=1.0, gamma=0.7)
```
</td>
<td valign="top">



```python
from numpy.random import permutation
from sklearn import svm, datasets
import covalent as ct

@ct.electron
def load_data():
    iris = datasets.load_iris()
    perm = permutation(iris.target.size)
    iris.data = iris.data[perm]
    iris.target = iris.target[perm]
    return iris.data, iris.target

@ct.electron
def train_svm(data, C, gamma):
    X, y = data
    clf = svm.SVC(C=C, gamma=gamma)
    clf.fit(X[90:], y[90:])
    return clf

@ct.electron
def score_svm(data, clf):
    X_test, y_test = data
    return clf.score(
    	X_test[:90],
	y_test[:90]
    )

@ct.lattice
def run_experiment(C=1.0, gamma=0.7):
    data = load_data()
    clf = train_svm(
    	data=data,
	C=C,
	gamma=gamma
    )
    score = score_svm(
    	data=data,
	clf=clf
    )
    return score

dispatchable_func = ct.dispatch(run_experiment)

dispatch_id = dispatchable_func(
    	C=1.0,
    	gamma=0.7
    )
result = ct.get_result(dispatch_id)
```
</td>
</tr>
<tr>
<td valign="top">

```python
>>> print(result)
0.988888888
```
</td>
<td valign="top">

```python
>>> print(f"""
... status     = {result.status}
... input      = {result.inputs}
... result     = {result.result}
... """)
status     = Status(STATUS='COMPLETED')
input      = {'C': 1.0, 'gamma': 0.7}
result     = 0.988888888
```
</td>
</tr>
</table>


For more examples, please refer to the [Covalent tutorials](https://covalent.readthedocs.io/en/latest/tutorials/tutorials.html).

## 📦 Installation

Covalent is developed using Python version 3.8 on Linux and macOS. The easiest way to install Covalent is using the PyPI package manager:

```console
pip install covalent
```

Refer to the [Getting Started](https://covalent.readthedocs.io/en/latest/getting_started/index.html) guide for more details on setting up. For a full list of supported platforms, consult the Covalent [compatibility matrix](https://covalent.readthedocs.io/en/latest/getting_started/compatibility.html).

## 🔧 How it Works

Users compose workflows using the Covalent SDK and submit them to the Covalent server. Upon receiving a workflow, the server analyzes the dependencies between tasks and dispatches each task to its specified execution backend. Independent tasks may be executed concurrently. The Covalent UI displays the execution progress of each workflow at the level of individual tasks.

<div align="center">

![covalent architecture](https://raw.githubusercontent.com/AgnostiqHQ/covalent/master/doc/source/_static/cova_archi.png)

</div>

## 📚 Documentation

The official documentation includes tips on getting started, some high level concepts, a handful of tutorials, and the API documentation. To learn more, please refer to the [Covalent documentation](https://covalent.readthedocs.io/en/latest/).

## ✔️  Contributing

To contribute to Covalent, refer to the [Contribution Guidelines](https://github.com/AgnostiqHQ/covalent/blob/master/CONTRIBUTING.md). We use GitHub's [issue tracking](https://github.com/AgnostiqHQ/covalent/issues) to manage known issues, bugs, and pull requests. Get started by forking the develop branch and submitting a pull request with your contributions. Improvements to the documentation, including tutorials and how-to guides, are also welcome from the community. Participation in the Covalent community is governed by the [Code of Conduct](https://github.com/AgnostiqHQ/covalent/blob/master/CODE_OF_CONDUCT.md).

## 📝 Release Notes

The latest release includes two new feature sets and three major enhancements. True to its modular nature, Covalent now allows users to define custom pre- and post-hooks to electrons to facilitate various use cases from setting up remote environments (using DepsPip) to running custom functions. We also now support data/file transfers between remote electrons in a very modular way, including Rsync, HTTP, and S3 protocols. As part of the enhancements, Covalent now internally uses an SQL database instead of storing results in a serialized format, which has resulted in impressive speedups and stability across the platform.  We have further made the Covalent server leaner by not requiring it to have any dependencies of electrons installed.  Covalent now only requires that your electron’s software dependencies exist on the client (the machine submitting the workflows) and backend (hardware running the tasks).

Summary of major features/enhancements:
- Pre- and post-hooks to setup the software environment and to run other custom functions
- Data transfer/management between electrons
- Robust database for storing and managing results
- User interface enhancements

The detailed history of changes can be viewed in the [Changelog](https://github.com/AgnostiqHQ/covalent/blob/master/CHANGELOG.md).


## ⚓ Citation

Please use the following citation in any publications:

> W. J. Cunningham, S. K. Radha, F. Hasan, J. Kanem, S. W. Neagle, and S. Sanand.
> *Covalent.* Zenodo, 2022. https://doi.org/10.5281/zenodo.5903364

## 📃 License

Covalent is licensed under the GNU Affero GPL 3.0 License. Covalent may be distributed under other licenses upon request. See the [LICENSE](https://github.com/AgnostiqHQ/covalent/blob/master/LICENSE) file or contact the [support team](mailto:support@agnostiq.ai) for more details.
