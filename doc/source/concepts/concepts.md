(concepts)=
# Concepts

This concepts guide is an introduction to the concepts that make Covalent unique as a workflow management system for machine learning experimentation. The guide has two parts.

The first part, {doc}`basics`, introduces the key code elements that make up Covalent. These elements are the building blocks of Covalent workflows:

::::::{grid} 1

:::::{grid-item-card} Covalent Basics
:text-align: center
:link: basic_primitives
:link-type: ref
:::::

:::::{grid-item-card}

::::{grid} 1 2 3 3

:::{grid-item-card} `@electron`
:link: basic_primitives_electrons
:link-type: ref
:img-top: images/electron.png

A task, the smallest unit of computational work in Covalent

:::

:::{grid-item-card} `@lattice`
:link: basic_primitives_lattice
:link-type: ref
:img-top: images/lattice.png

A workflow composed of tasks

:::

:::{grid-item-card} `dispatch()`
:link: basic_primitives_dispatch
:link-type: ref
:img-top: images/dispatch.png

A function to submit a workflow to the Covalent server

:::

:::{grid-item-card} `executor`
:link: basic_primitives_executor
:link-type: ref
:img-top: images/executor.jpg

A plugin to execute individual tasks

:::

:::{grid-item-card} `get_result()`
:link: basic_primitives_result
:link-type: ref
:img-top: images/get_result.png

A function to retrieve the product of a workflow

:::

::::

:::::

::::::


The second part, {doc}`architecture`, outlines the three main parts of the Covalent architecture and introduces the in-depth descriptions that follow:

::::::{grid} 1

:::::{grid-item-card} Covalent Architecture
:text-align: center
:link: architecture
:link-type: ref
:::::

:::::{grid-item-card}

::::{grid} 1 3 3 3
:::{grid-item-card}  Covalent SDK
:link: architecture_sdk
:link-type: ref
:img-top: ../_static/covalent_sdk2x.png


Describes the workflow model embodied in Covalent's API, including the Python code elements introduced in Basics.
:::
:::{grid-item-card}  Covalent Server
:link: architecture_server
:link-type: ref
:img-top: ../_static/covalent_server2x.png

Describes in detail how the Covalent server handles workflows and dispatches tasks for execution.
:::
:::{grid-item-card}  Covalent GUI
:link: architecture_gui
:link-type: ref
:img-top: ../_static/covalent_gui2x.png

Shows how the Covalent GUI displays dispatched workflows in summary and detail forms, and how it saves and retrieves results.

:::

::::

:::::

::::::


:::{toctree}
:maxdepth: 2
:hidden:

basics
architecture
