/**
 * Copyright 2021 Agnostiq Inc.
 *
 * This file is part of Covalent.
 *
 * Licensed under the GNU Affero General Public License 3.0 (the "License").
 * A copy of the License may be obtained with this software package or at
 *
 *      https://www.gnu.org/licenses/agpl-3.0.en.html
 *
 * Use of this file is prohibited except in compliance with the License. Any
 * modifications or derivative works of this file must retain this copyright
 * notice, and modified files must contain a notice indicating that they have
 * been altered from the originals.
 *
 * Covalent is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE. See the License for more details.
 *
 * Relief from the License may be granted by purchasing a commercial license.
 */

import _ from 'lodash'

/**
 * Demo mode switch based on build-time environment variable (see package.json).
 */
export const isDemo = _.toLower(process.env.REACT_APP_DEMO) === 'true'

export const demoEnhancer =
  (createStore) => (reducer, initialState, enhancer) => {
    return createStore(reducer, demoState, enhancer)
  }

export const names = [
  'remember-strong-force',
  'let-able-name',
  'have-hard-level',
  'hear-full-head',
  'serve-local-program',
  'learn-recent-law',
]

export const result = {
  dispatch_id: 'serve-local-program',
  status: 'COMPLETED',
  result: 0.720473253734701,
  start_time: '2022-01-10T17:22:27.010349+00:00',
  end_time: '2022-01-10T17:22:29.464902+00:00',
  results_dir: '/home/valentin/covalent',
  lattice: {
    function_string:
      '# @ct.lattice\ndef compute_energy(initial_height=3, distance=1.10):\n    N2 = construct_n_molecule(d=distance)\n    e_N2 = compute_system_energy(system=N2)\n\n    slab = construct_cu_slab(unit_cell=(4, 4, 2), vacuum=10.0)\n    e_slab = compute_system_energy(system=slab)\n\n    relaxed_slab = get_relaxed_slab(slab=slab, molecule=N2, height=initial_height)\n    e_relaxed_slab = compute_system_energy(system=relaxed_slab)\n    final_result = e_slab + e_N2 - e_relaxed_slab\n\n    return final_result\n\n\n',
    doc: null,
    name: 'compute_energy',
    inputs: { initial_height: 3, distance: 1.1 },
    metadata: {
      backend: ['local'],
      tempdir: '',
      dispatcher: '0.0.0.0:47007',
      results_dir: '/home/valentin/covalent',
    },
  },
  graph: {
    nodes: [
      {
        name: 'construct_n_molecule',
        kwargs: { d: 1.1 },
        metadata: { backend: ['local'], tempdir: '' },
        function_string:
          '# @ct.electron\ndef construct_n_molecule(d=0):\n    return Atoms("2N", positions=[(0.0, 0.0, 0.0), (0.0, 0.0, d)])\n\n\n',
        start_time: '2022-01-10T17:22:27.020972+00:00',
        end_time: '2022-01-10T17:22:27.046173+00:00',
        status: 'COMPLETED',
        output: "Atoms(symbols='N2', pbc=False, calculator=EMT(...))",
        error: null,
        sublattice_result: null,
        exec_plan: {
          selected_executor: 'local',
          execution_args: { tempdir: '' },
        },
        id: 0,
        doc: null,
      },
      {
        name: ':parameter:1.1',
        kwargs: { d: 1.1 },
        metadata: {
          schedule: false,
          num_cpu: 1,
          cpu_feature_set: [],
          num_gpu: 0,
          gpu_type: '',
          gpu_compute_capability: [],
          memory: '1G',
          backend: ['local'],
          budget: null,
          strategy: 'balanced',
          time_limit: '00-00:00:00',
          quantum: false,
          job_name: '',
          hostnames: [],
          conda_env: '',
          tempdir: '',
          quantum_provider: '',
          quantum_backend: '',
        },
        start_time: '2022-01-10T17:22:27.010453+00:00',
        end_time: '2022-01-10T17:22:27.010458+00:00',
        status: 'COMPLETED',
        output: 1.1,
        error: null,
        sublattice_result: null,
        id: 1,
        doc: null,
      },
      {
        name: 'compute_system_energy',
        kwargs: {
          system: "Atoms(symbols='N2', pbc=False, calculator=EMT(...))",
        },
        metadata: { backend: ['local'], tempdir: '' },
        function_string:
          '# @ct.electron\ndef compute_system_energy(system):\n    system.calc = EMT()\n    return system.get_potential_energy()\n\n\n',
        start_time: '2022-01-10T17:22:27.094907+00:00',
        end_time: '2022-01-10T17:22:27.125287+00:00',
        status: 'COMPLETED',
        output: 0.44034357303561467,
        error: null,
        sublattice_result: null,
        exec_plan: {
          selected_executor: 'local',
          execution_args: { tempdir: '' },
        },
        id: 2,
        doc: null,
      },
      {
        name: 'construct_cu_slab',
        kwargs: { unit_cell: [4, 4, 2], vacuum: 10.0 },
        metadata: { backend: ['local'], tempdir: '' },
        function_string:
          '# @ct.electron\ndef construct_cu_slab(\n    unit_cell=(4, 4, 2), vacuum=10.0,\n):\n    slab = fcc111("Cu", size=unit_cell, vacuum=vacuum)\n    return slab\n\n\n',
        start_time: '2022-01-10T17:22:27.020569+00:00',
        end_time: '2022-01-10T17:22:27.045458+00:00',
        status: 'COMPLETED',
        output:
          "Atoms(symbols='Cu32N2', pbc=[True, True, False], cell=[[10.210621920333747, 0.0, 0.0], [5.105310960166873, 8.842657971447272, 0.0], [0.0, 0.0, 22.08423447177455]], tags=..., constraint=FixAtoms(indices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]), calculator=EMT(...))",
        error: null,
        sublattice_result: null,
        exec_plan: {
          selected_executor: 'local',
          execution_args: { tempdir: '' },
        },
        id: 3,
        doc: null,
      },
      {
        name: ':parameter:(4, 4, 2)',
        kwargs: { unit_cell: [4, 4, 2] },
        metadata: {
          schedule: false,
          num_cpu: 1,
          cpu_feature_set: [],
          num_gpu: 0,
          gpu_type: '',
          gpu_compute_capability: [],
          memory: '1G',
          backend: ['local'],
          budget: null,
          strategy: 'balanced',
          time_limit: '00-00:00:00',
          quantum: false,
          job_name: '',
          hostnames: [],
          conda_env: '',
          tempdir: '',
          quantum_provider: '',
          quantum_backend: '',
        },
        start_time: '2022-01-10T17:22:27.010474+00:00',
        end_time: '2022-01-10T17:22:27.010478+00:00',
        status: 'COMPLETED',
        output: [4, 4, 2],
        error: null,
        sublattice_result: null,
        id: 4,
        doc: null,
      },
      {
        name: ':parameter:10.0',
        kwargs: { vacuum: 10.0 },
        metadata: {
          schedule: false,
          num_cpu: 1,
          cpu_feature_set: [],
          num_gpu: 0,
          gpu_type: '',
          gpu_compute_capability: [],
          memory: '1G',
          backend: ['local'],
          budget: null,
          strategy: 'balanced',
          time_limit: '00-00:00:00',
          quantum: false,
          job_name: '',
          hostnames: [],
          conda_env: '',
          tempdir: '',
          quantum_provider: '',
          quantum_backend: '',
        },
        start_time: '2022-01-10T17:22:27.010490+00:00',
        end_time: '2022-01-10T17:22:27.010495+00:00',
        status: 'COMPLETED',
        output: 10.0,
        error: null,
        sublattice_result: null,
        id: 5,
        doc: null,
      },
      {
        name: 'compute_system_energy',
        kwargs: {
          system:
            "Atoms(symbols='Cu32N2', pbc=[True, True, False], cell=[[10.210621920333747, 0.0, 0.0], [5.105310960166873, 8.842657971447272, 0.0], [0.0, 0.0, 22.08423447177455]], tags=..., constraint=FixAtoms(indices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]), calculator=EMT(...))",
        },
        metadata: { backend: ['local'], tempdir: '' },
        function_string:
          '# @ct.electron\ndef compute_system_energy(system):\n    system.calc = EMT()\n    return system.get_potential_energy()\n\n\n',
        start_time: '2022-01-10T17:22:27.097196+00:00',
        end_time: '2022-01-10T17:22:27.497928+00:00',
        status: 'COMPLETED',
        output: 11.905341687099202,
        error: null,
        sublattice_result: null,
        exec_plan: {
          selected_executor: 'local',
          execution_args: { tempdir: '' },
        },
        id: 6,
        doc: null,
      },
      {
        name: 'get_relaxed_slab',
        kwargs: {
          slab: "Atoms(symbols='Cu32N2', pbc=[True, True, False], cell=[[10.210621920333747, 0.0, 0.0], [5.105310960166873, 8.842657971447272, 0.0], [0.0, 0.0, 22.08423447177455]], tags=..., constraint=FixAtoms(indices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]), calculator=EMT(...))",
          molecule: "Atoms(symbols='N2', pbc=False, calculator=EMT(...))",
          height: 3,
        },
        metadata: { backend: ['local'], tempdir: '' },
        function_string:
          '# @ct.electron\ndef get_relaxed_slab(slab, molecule, height=1.85):\n    slab.calc = EMT()\n    add_adsorbate(slab, molecule, height, "ontop")\n    constraint = FixAtoms(mask=[a.symbol != "N" for a in slab])\n    slab.set_constraint(constraint)\n    dyn = QuasiNewton(slab, trajectory="/tmp/N2Cu.traj", logfile="/tmp/temp")\n    dyn.run(fmax=0.01)\n    return slab\n\n\n',
        start_time: '2022-01-10T17:22:27.097876+00:00',
        end_time: '2022-01-10T17:22:29.197773+00:00',
        status: 'COMPLETED',
        output:
          "Atoms(symbols='Cu32N2', pbc=[True, True, False], cell=[[10.210621920333747, 0.0, 0.0], [5.105310960166873, 8.842657971447272, 0.0], [0.0, 0.0, 22.08423447177455]], tags=..., constraint=FixAtoms(indices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]), calculator=EMT(...))",
        error: null,
        sublattice_result: null,
        exec_plan: {
          selected_executor: 'local',
          execution_args: { tempdir: '' },
        },
        id: 7,
        doc: null,
      },
      {
        name: ':parameter:3',
        kwargs: { height: 3 },
        metadata: {
          schedule: false,
          num_cpu: 1,
          cpu_feature_set: [],
          num_gpu: 0,
          gpu_type: '',
          gpu_compute_capability: [],
          memory: '1G',
          backend: ['local'],
          budget: null,
          strategy: 'balanced',
          time_limit: '00-00:00:00',
          quantum: false,
          job_name: '',
          hostnames: [],
          conda_env: '',
          tempdir: '',
          quantum_provider: '',
          quantum_backend: '',
        },
        start_time: '2022-01-10T17:22:27.010507+00:00',
        end_time: '2022-01-10T17:22:27.010511+00:00',
        status: 'COMPLETED',
        output: 3,
        error: null,
        sublattice_result: null,
        id: 8,
        doc: null,
      },
      {
        name: 'compute_system_energy',
        kwargs: {
          system:
            "Atoms(symbols='Cu32N2', pbc=[True, True, False], cell=[[10.210621920333747, 0.0, 0.0], [5.105310960166873, 8.842657971447272, 0.0], [0.0, 0.0, 22.08423447177455]], tags=..., constraint=FixAtoms(indices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]), calculator=EMT(...))",
        },
        metadata: { backend: ['local'], tempdir: '' },
        function_string:
          '# @ct.electron\ndef compute_system_energy(system):\n    system.calc = EMT()\n    return system.get_potential_energy()\n\n\n',
        start_time: '2022-01-10T17:22:29.235460+00:00',
        end_time: '2022-01-10T17:22:29.407438+00:00',
        status: 'COMPLETED',
        output: 11.625212006400115,
        error: null,
        sublattice_result: null,
        exec_plan: {
          selected_executor: 'local',
          execution_args: { tempdir: '' },
        },
        id: 9,
        doc: null,
      },
      {
        name: 'compute_system_energy_+_compute_system_energy',
        kwargs: { arg_1: 11.905341687099202, arg_2: 0.44034357303561467 },
        metadata: { backend: ['local'], tempdir: '' },
        function_string:
          '#         @electron\n        @rename(operand_1, op, operand_2)\n        def func_for_op(arg_1: Union[Any, "Electron"], arg_2: Union[Any, "Electron"]) -> Any:\n            """\n            Intermediate function for the binary operation.\n\n            Args:\n                arg_1: First operand\n                arg_2: Second operand\n\n            Returns:\n                result: Result of the binary operation.\n            """\n\n            return op_table[op](arg_1, arg_2)\n\n\n',
        start_time: '2022-01-10T17:22:29.235097+00:00',
        end_time: '2022-01-10T17:22:29.272567+00:00',
        status: 'COMPLETED',
        output: 12.345685260134816,
        error: null,
        sublattice_result: null,
        exec_plan: {
          selected_executor: 'local',
          execution_args: { tempdir: '' },
        },
        id: 10,
        doc: '\n            Intermediate function for the binary operation.\n\n            Args:\n                arg_1: First operand\n                arg_2: Second operand\n\n            Returns:\n                result: Result of the binary operation.\n            ',
      },
      {
        name: 'compute_system_energy_+_compute_system_energy_-_compute_system_energy',
        kwargs: { arg_1: 12.345685260134816, arg_2: 11.625212006400115 },
        metadata: { backend: ['local'], tempdir: '' },
        function_string:
          '#         @electron\n        @rename(operand_1, op, operand_2)\n        def func_for_op(arg_1: Union[Any, "Electron"], arg_2: Union[Any, "Electron"]) -> Any:\n            """\n            Intermediate function for the binary operation.\n\n            Args:\n                arg_1: First operand\n                arg_2: Second operand\n\n            Returns:\n                result: Result of the binary operation.\n            """\n\n            return op_table[op](arg_1, arg_2)\n\n\n',
        start_time: '2022-01-10T17:22:29.434181+00:00',
        end_time: '2022-01-10T17:22:29.451270+00:00',
        status: 'COMPLETED',
        output: 0.720473253734701,
        error: null,
        sublattice_result: null,
        exec_plan: {
          selected_executor: 'local',
          execution_args: { tempdir: '' },
        },
        id: 11,
        doc: '\n            Intermediate function for the binary operation.\n\n            Args:\n                arg_1: First operand\n                arg_2: Second operand\n\n            Returns:\n                result: Result of the binary operation.\n            ',
      },
    ],
    links: [
      { variable: 'system', source: 0, target: 2 },
      { variable: 'molecule', source: 0, target: 7 },
      { variable: 'd', source: 1, target: 0 },
      { variable: 'arg_2', source: 2, target: 10 },
      { variable: 'system', source: 3, target: 6 },
      { variable: 'slab', source: 3, target: 7 },
      { variable: 'unit_cell', source: 4, target: 3 },
      { variable: 'vacuum', source: 5, target: 3 },
      { variable: 'arg_1', source: 6, target: 10 },
      { variable: 'system', source: 7, target: 9 },
      { variable: 'height', source: 8, target: 7 },
      { variable: 'arg_2', source: 9, target: 11 },
      { variable: 'arg_1', source: 10, target: 11 },
    ],
  },
}

/**
 * Used as redux store preloaded state for static demo.
 *
 */
export const demoState = {
  results: {
    cache: _.keyBy(
      _.map(names, (name) => ({ ...result, dispatch_id: name })),
      'dispatch_id'
    ),
    fetchResult: { isFetching: false, error: null },
  },
}
