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

"""Configuration file for the Sphinx documentation builder."""

import os
import sys

# Project information
project = ""
copyright = "2021 Agnostiq Inc."
author = "Agnostiq"

html_static_path = ["_static"]


# Sphinx Extensions
sys.path.append(os.path.abspath("./extensions"))

extensions = [
    "sphinx.ext.autodoc",
    "sphinx_panels",
    "sphinx.ext.napoleon",
    "sphinx_automodapi.automodapi",
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
    "sphinx.ext.mathjax",
    "sphinx.ext.viewcode",
    "sphinx.ext.autosummary",
    "sphinx_design",
    "autodocsumm",
    "nbsphinx",
    "sphinx_autodoc_typehints",
    "sphinx-prompt",
    "sphinx_inline_tabs",
    "sphinx_execute_code",
    "sphinx_click.ext",
    "sphinx_autodoc_typehints",
    "myst_parser",
    'sphinx_reredirects'
]

# Sphinx variables
numpydoc_show_class_members = False
autosummary_generate = True
autodoc_default_options = {
    "autosummary": True,
}
exclude_patterns = ["_build", "**.ipynb_checkpoints"]
nbsphinx_execute = "never"
highlight_language = "python"
html_scaled_image_link = False
add_module_names = True

templates_path = ["_templates"]

# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# Options for HTML output
html_static_path = ["_static"]
templates_path = ["_templates"]
html_theme = "furo"

html_title = ""
html_favicon = "_static/covalent-logo-blue-favicon.png"
html_theme_options = {
    "light_logo": "covalent-logo-horizontal-blue.png",
    "dark_logo": "covalent-logo-horizontal-light.png",
    "light_css_variables": {
        "color-brand-primary": "#5552FF",
        "color-brand-content": "#6D7CFF",
    },
    "dark_css_variables": {
        "color-brand-primary": "#5552FF",
        "color-brand-secondary": "#AEB6FF",
        "color-brand-ternary": "#6E33ED",
        "color-brand-content": "#6D7CFF",
    },
}

# Options for Markdown files
myst_enable_extensions = [
    "colon_fence",
    "deflist",
]
myst_heading_anchors = 3

baseurl="https://docs.covalent.xyz"

redirects = {
"tutorials/tutorials": '%s%s' % (baseurl , "/docs/user-documentation/tutorials"),
"credentials": '%s%s' % (baseurl ,"/docs/user-documentation/credentials"),
"api/executors/index":'%s%s' % (baseurl ,"/docs/features/executor-plugins/exe"),
"how_to/index":'%s%s' % (baseurl ,"/docs/user-documentation/how-to/how-to-guide"),
"index":'%s%s' % (baseurl ,"/docs/"),
"getting_started/quick_start/index":'%s%s' % (baseurl ,"/docs/get-started/quick-start"),
"getting_started/first_experiment/index":'%s%s' % (baseurl ,"/docs/get-started/first-experiment"),
"concepts/concepts":'%s%s' % (baseurl ,"/docs/user-documentation/credentials/"),
"concepts/basics":'%s%s' % (baseurl ,"/docs/user-documentation/concepts/covalent-basics"),
"concepts/architecture":'%s%s' % (baseurl ,"/docs/user-documentation/concepts/covalent-arch/covalent-architecture"),
"concepts/api_concepts":'%s%s' % (baseurl ,"/docs/user-documentation/concepts/covalent-arch/covalent-sdk"),
"concepts/server_concepts":'%s%s' % (baseurl ,"/docs/user-documentation/concepts/covalent-arch/covalent-services"),
"concepts/ui_concepts":'%s%s' % (baseurl ,"/docs/user-documentation/concepts/covalent-arch/covalent-gui"),
"tutorials/0_ClassicalMachineLearning/mnist_images/source":'%s%s' % (baseurl ,"/docs/user-documentation/tutorials/mnist/"),
"tutorials/1_QuantumMachineLearning/pennylane_hybrid/source":'%s%s' % (baseurl ,"/docs/user-documentation/tutorials/hybrid/"),
"tutorials/0_ClassicalMachineLearning/autoencoders/source":'%s%s' % (baseurl ,"/docs/user-documentation/tutorials/autoencoders/"),
"tutorials/5_QPUAccessIBM/source":'%s%s' % (baseurl ,"/docs/user-documentation/tutorials/qpuaccessibm/"),
"tutorials/1_QuantumMachineLearning/pennylane_iris_classification/source":'%s%s' % (baseurl ,"/docs/user-documentation/tutorials/iris/"),
"tutorials/1_QuantumMachineLearning/pennylane_parity_classifier/source":'%s%s' % (baseurl ,"/docs/user-documentation/tutorials/parityclassify/"),
"tutorials/machine_learning/dnn_comparison":'%s%s' % (baseurl ,"/docs/user-documentation/tutorials/dnn_comparison/"),
"tutorials/3_QuantumChemistry/nitrogen_copper_interaction/source":'%s%s' % (baseurl ,"/docs/user-documentation/tutorials/nitrogencopper/"),
"tutorials/3_QuantumChemistry/dynamic_quantum_chemistry/source":'%s%s' % (baseurl ,"/docs/user-documentation/tutorials/quantumchemistry/"),
"tutorials/1_QuantumMachineLearning/classical_quantum_svm/source":'%s%s' % (baseurl ,"/docs/user-documentation/tutorials/svm/"),
"tutorials/1_QuantumMachineLearning/quantum_embedding_kernel/source":'%s%s' % (baseurl ,"/docs/user-documentation/tutorials/quantumembedding/"),
"tutorials/1_QuantumMachineLearning/qaoa_maxcut/source":'%s%s' % (baseurl ,"/docs/user-documentation/tutorials/qaoa/"),
"tutorials/1_QuantumMachineLearning/pennylane_ensemble_classification/source":'%s%s' % (baseurl ,"/docs/user-documentation/tutorials/ensemble/"),
"tutorials/2_Astronomy/star_tracker/source":'%s%s' % (baseurl ,"/docs/user-documentation/tutorials/star_tracker/"),
"tutorials/4_QuantumGravity/spacetime_classification/source":'%s%s' % (baseurl ,"/docs/user-documentation/tutorials/spacetime/"),
"how_to/coding/construct_electron":'%s%s' % (baseurl ,"/docs/user-documentation/how-to/construct-electron"),
"how_to/coding/construct_lattice":'%s%s' % (baseurl ,"/docs/user-documentation/how-to/construct-lattice"),
"how_to/coding/add_electron_to_lattice":'%s%s' % (baseurl ,"/docs/user-documentation/how-to/add-electron-to-lattice"),
"how_to/coding/test_electron":'%s%s' % (baseurl ,"/docs/user-documentation/how-to/test-electron"),
"how_to/coding/use_iterable":'%s%s' % (baseurl ,"/docs/user-documentation/how-to/use-iterable"),
"how_to/coding/looping":'%s%s' % (baseurl ,"/docs/user-documentation/how-to/looping"),
"how_to/coding/visualize_lattice":'%s%s' % (baseurl ,"/docs/user-documentation/how-to/visualize-lattice"),
"how_to/coding/add_constraints_to_lattice":'%s%s' % (baseurl ,"/docs/user-documentation/how-to/add-constraints-to-lattice"),
"how_to/coding/wait_for_another_electron":'%s%s' % (baseurl ,"/docs/user-documentation/how-to/wait-for-another-electron"),
"how_to/coding/file_transfers_for_workflows_local":'%s%s' % (baseurl ,"/docs/user-documentation/how-to/file-transfers-for-workflows-local"),
"how_to/coding/file_transfers_to_from_remote":'%s%s' % (baseurl ,"/docs/user-documentation/how-to/file-transfers-to-from-remote"),
"how_to/coding/file_transfers_to_from_s3":'%s%s' % (baseurl ,"/docs/user-documentation/how-to/file-transfers-to-from-s3"),
"how_to/coding/construct_lepton":'%s%s' % (baseurl ,"/docs/user-documentation/how-to/construct-lepton"),
"how_to/coding/construct_c_task":'%s%s' % (baseurl ,"/docs/user-documentation/how-to/construct-c-task"),
"how_to/coding/add_pip_dependencies_to_electron":'%s%s' % (baseurl ,"/docs/user-documentation/how-to/add-pip-dependencies-to-electron"),
"how_to/coding/add_bash_dependencies_to_electron":'%s%s' % (baseurl ,"/docs/user-documentation/how-to/add-bash-dependencies-to-electron"),
"how_to/coding/add_callable_dependencies_to_electron":'%s%s' % (baseurl ,"/docs/user-documentation/how-to/add-callable-dependencies-to-electron"),
"how_to/coding/construct_bash_task":'%s%s' % (baseurl ,"/docs/user-documentation/how-to/construct-bash-task"),
"how_to/execution/covalent_cli":'%s%s' % (baseurl ,"/docs/user-documentation/how-to/execution/covalent-cli"),
"how_to/execution/execute_lattice":'%s%s' % (baseurl ,"/docs/user-documentation/how-to/execution/execute-lattice"),
"how_to/execution/redispatch":'%s%s' % (baseurl ,"/docs/user-documentation/how-to/execution/redispatch"),
"how_to/execution/execute_individual_electron":'%s%s' % (baseurl ,"/docs/user-documentation/how-to/execution/execute-individual-electron"),
"how_to/execution/execute_lattice_multiple_times":'%s%s' % (baseurl ,"/docs/user-documentation/how-to/execution/execute-lattice-multiple-times"),
"how_to/execution/execute_multiple_lattices":'%s%s' % (baseurl ,"/docs/user-documentation/how-to/execution/execute-multiple-lattices"),
"how_to/execution/execute_sublattice":'%s%s' % (baseurl ,"/docs/user-documentation/how-to/execution/execute-sublattice"),
"how_to/execution/choosing_executors":'%s%s' % (baseurl ,"/docs/user-documentation/how-to/execution/choosing-executors"),
"how_to/execution/choosing_conda_environments":'%s%s' % (baseurl ,"/docs/user-documentation/how-to/execution/choosing-conda-environments"),
"how_to/status/query_lattice_execution_status":'%s%s' % (baseurl ,"/docs/user-documentation/how-to/status/query-lattice-execution-status"),
"how_to/status/query_electron_execution_status":'%s%s' % (baseurl ,"/docs/user-documentation/how-to/status/query-electron-execution-status"),
"how_to/status/query_lattice_execution_time":'%s%s' % (baseurl ,"/docs/user-documentation/how-to/status/query-lattice-execution-time"),
"how_to/collection/query_multiple_lattice_execution_results":'%s%s' % (baseurl ,"/docs/user-documentation/how-to/status/query-multiple-lattice-execution-results"),
"how_to/collection/query_lattice_execution_result":'%s%s' % (baseurl ,"/docs/user-documentation/how-to/status/query-lattice-execution-result"),
"how_to/collection/query_electron_execution_result":'%s%s' % (baseurl ,"/docs/user-documentation/how-to/status/query-electron-execution-result"),
"how_to/config/customization":'%s%s' % (baseurl ,"/docs/user-documentation/how-to/customization"),

}
