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

const result = {
  dispatch_id: 'df4601e7-7658-4a14-a860-f91a35a1b453',
  status: 'COMPLETED',
  result: 0.3241872821704259,
  start_time: '2022-01-25T20:13:07.184270+00:00',
  end_time: '2022-01-25T20:13:20.531358+00:00',
  results_dir: '/home/valentin/code/agnostiq/examples/results',
  lattice: {
    function_string:
      '# @ct.lattice(backend=executor1)\ndef compute_energy(initial_height=3, distance=1.10):\n    N2 = construct_n_molecule(d=distance)\n    e_N2 = compute_system_energy(system=N2)\n\n    slab = construct_cu_slab(unit_cell=(4, 4, 2), vacuum=10.0)\n    e_slab = compute_system_energy(system=slab)\n\n    relaxed_slab = get_relaxed_slab(slab=slab, molecule=N2, height=initial_height)\n    e_relaxed_slab = compute_system_energy(system=relaxed_slab)\n    final_result = e_slab + e_N2 - e_relaxed_slab\n\n    return final_result\n\n\n',
    doc: null,
    name: 'compute_energy',
    kwargs: { initial_height: '3', distance: '1.1' },
    metadata: {
      backend: '<LocalExecutor>',
      dispatcher: 'localhost:48008',
      results_dir: '/home/valentin/code/agnostiq/examples/results',
      executor: {
        log_stdout: '/tmp/results/log_stdout.txt',
        log_stderr: '/tmp/results/log_stderr.txt',
        conda_env: 'covalent',
        cache_dir: '',
        current_env_on_conda_fail: 'True',
        current_env: '',
      },
    },
  },
  graph: {
    nodes: [
      {
        name: 'construct_n_molecule',
        kwargs: { d: '1.1' },
        metadata: {
          backend: '<LocalExecutor>',
          executor: {
            log_stdout: '/tmp/results/log_stdout.txt',
            log_stderr: '/tmp/results/log_stderr.txt',
            conda_env: 'covalent',
            cache_dir: '',
            current_env_on_conda_fail: 'True',
            current_env: '',
          },
        },
        function_string:
          '# @ct.electron\ndef construct_n_molecule(d=0):\n    return Atoms("2N", positions=[(0.0, 0.0, 0.0), (0.0, 0.0, d)])\n\n\n',
        start_time: '2022-01-25T20:13:07.194613+00:00',
        end_time: '2022-01-25T20:13:08.539967+00:00',
        status: 'COMPLETED',
        output: "Atoms(symbols='N2', pbc=False, calculator=EMT(...))",
        error: null,
        sublattice_result: null,
        stdout: '',
        stderr: '',
        exec_plan: {
          selected_executor:
            '</home/valentin/code/agnostiq/covalent-staging/covalent/executor/executor_plugins/local.LocalExecutor object at 0x7f10c18f0ac0>',
          execution_args: {},
        },
        id: 0,
        doc: null,
      },
      {
        name: ':parameter:1.1',
        kwargs: { d: '1.1' },
        metadata: {
          schedule: false,
          num_cpu: 1,
          cpu_feature_set: [],
          num_gpu: 0,
          gpu_type: '',
          gpu_compute_capability: [],
          memory: '1G',
          backend: 'local',
          time_limit: '00-00:00:00',
          budget: 0,
          conda_env: '',
          executor: {
            log_stdout: 'stdout.log',
            log_stderr: 'stderr.log',
            conda_env: '',
            cache_dir: '/tmp/covalent',
            current_env_on_conda_fail: 'False',
            current_env: '',
          },
        },
        start_time: '2022-01-25T20:13:07.184559+00:00',
        end_time: '2022-01-25T20:13:07.184568+00:00',
        status: 'COMPLETED',
        output: 1.1,
        error: null,
        sublattice_result: null,
        stdout: null,
        stderr: null,
        id: 1,
        doc: null,
      },
      {
        name: 'compute_system_energy',
        kwargs: {
          system: "Atoms(symbols='N2', pbc=False, calculator=EMT(...))",
        },
        metadata: {
          backend: '<LocalExecutor>',
          executor: {
            log_stdout: '/tmp/results/log_stdout2.txt',
            log_stderr: '/tmp/results/log_stderr2.txt',
            conda_env: '',
            cache_dir: '',
            current_env_on_conda_fail: 'True',
            current_env: '',
          },
        },
        function_string:
          '# @ct.electron(backend=executor2)\ndef compute_system_energy(system):\n    system.calc = EMT()\n    return system.get_potential_energy()\n\n\n',
        start_time: '2022-01-25T20:13:08.641523+00:00',
        end_time: '2022-01-25T20:13:08.749618+00:00',
        status: 'COMPLETED',
        output: 0.44034357303561467,
        error: null,
        sublattice_result: null,
        stdout: '',
        stderr: '',
        exec_plan: {
          selected_executor:
            '</home/valentin/code/agnostiq/covalent-staging/covalent/executor/executor_plugins/local.LocalExecutor object at 0x7f10c8036bb0>',
          execution_args: {},
        },
        id: 2,
        doc: null,
      },
      {
        name: 'construct_cu_slab',
        kwargs: { unit_cell: '(4, 4, 2)', vacuum: '10.0' },
        metadata: {
          backend: '<LocalExecutor>',
          executor: {
            log_stdout: '/tmp/results/log_stdout.txt',
            log_stderr: '/tmp/results/log_stderr.txt',
            conda_env: 'covalent',
            cache_dir: '',
            current_env_on_conda_fail: 'True',
            current_env: '',
          },
        },
        function_string:
          '# @ct.electron(backend=executor1)\ndef construct_cu_slab(\n    unit_cell=(4, 4, 2), vacuum=10.0,\n):\n    slab = fcc111("Cu", size=unit_cell, vacuum=vacuum)\n    return slab\n\n\n',
        start_time: '2022-01-25T20:13:07.194813+00:00',
        end_time: '2022-01-25T20:13:08.600670+00:00',
        status: 'COMPLETED',
        output:
          "Atoms(symbols='Cu32N2', pbc=[True, True, False], cell=[[10.210621920333747, 0.0, 0.0], [5.105310960166873, 8.842657971447272, 0.0], [0.0, 0.0, 22.08423447177455]], tags=..., constraint=FixAtoms(indices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]), calculator=EMT(...))",
        error: null,
        sublattice_result: null,
        stdout: '',
        stderr: '',
        exec_plan: {
          selected_executor:
            '</home/valentin/code/agnostiq/covalent-staging/covalent/executor/executor_plugins/local.LocalExecutor object at 0x7f10c18f0ac0>',
          execution_args: {},
        },
        id: 3,
        doc: null,
      },
      {
        name: ':parameter:(4, 4, 2)',
        kwargs: { unit_cell: '(4, 4, 2)' },
        metadata: {
          schedule: false,
          num_cpu: 1,
          cpu_feature_set: [],
          num_gpu: 0,
          gpu_type: '',
          gpu_compute_capability: [],
          memory: '1G',
          backend: 'local',
          time_limit: '00-00:00:00',
          budget: 0,
          conda_env: '',
          executor: {
            log_stdout: 'stdout.log',
            log_stderr: 'stderr.log',
            conda_env: '',
            cache_dir: '/tmp/covalent',
            current_env_on_conda_fail: 'False',
            current_env: '',
          },
        },
        start_time: '2022-01-25T20:13:07.184603+00:00',
        end_time: '2022-01-25T20:13:07.184608+00:00',
        status: 'COMPLETED',
        output: [4, 4, 2],
        error: null,
        sublattice_result: null,
        stdout: null,
        stderr: null,
        id: 4,
        doc: null,
      },
      {
        name: ':parameter:10.0',
        kwargs: { vacuum: '10.0' },
        metadata: {
          schedule: false,
          num_cpu: 1,
          cpu_feature_set: [],
          num_gpu: 0,
          gpu_type: '',
          gpu_compute_capability: [],
          memory: '1G',
          backend: 'local',
          time_limit: '00-00:00:00',
          budget: 0,
          conda_env: '',
          executor: {
            log_stdout: 'stdout.log',
            log_stderr: 'stderr.log',
            conda_env: '',
            cache_dir: '/tmp/covalent',
            current_env_on_conda_fail: 'False',
            current_env: '',
          },
        },
        start_time: '2022-01-25T20:13:07.184635+00:00',
        end_time: '2022-01-25T20:13:07.184640+00:00',
        status: 'COMPLETED',
        output: 10.0,
        error: null,
        sublattice_result: null,
        stdout: null,
        stderr: null,
        id: 5,
        doc: null,
      },
      {
        name: 'compute_system_energy',
        kwargs: {
          system:
            "Atoms(symbols='Cu32N2', pbc=[True, True, False], cell=[[10.210621920333747, 0.0, 0.0], [5.105310960166873, 8.842657971447272, 0.0], [0.0, 0.0, 22.08423447177455]], tags=..., constraint=FixAtoms(indices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]), calculator=EMT(...))",
        },
        metadata: {
          backend: '<LocalExecutor>',
          executor: {
            log_stdout: '/tmp/results/log_stdout2.txt',
            log_stderr: '/tmp/results/log_stderr2.txt',
            conda_env: '',
            cache_dir: '',
            current_env_on_conda_fail: 'True',
            current_env: '',
          },
        },
        function_string:
          '# @ct.electron(backend=executor2)\ndef compute_system_energy(system):\n    system.calc = EMT()\n    return system.get_potential_energy()\n\n\n',
        start_time: '2022-01-25T20:13:08.641030+00:00',
        end_time: '2022-01-25T20:13:08.843983+00:00',
        status: 'COMPLETED',
        output: 11.509056283570393,
        error: null,
        sublattice_result: null,
        stdout: '',
        stderr: '',
        exec_plan: {
          selected_executor:
            '</home/valentin/code/agnostiq/covalent-staging/covalent/executor/executor_plugins/local.LocalExecutor object at 0x7f10c8036bb0>',
          execution_args: {},
        },
        id: 6,
        doc: null,
      },
      {
        name: 'get_relaxed_slab',
        kwargs: {
          slab: "Atoms(symbols='Cu32N2', pbc=[True, True, False], cell=[[10.210621920333747, 0.0, 0.0], [5.105310960166873, 8.842657971447272, 0.0], [0.0, 0.0, 22.08423447177455]], tags=..., constraint=FixAtoms(indices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]), calculator=EMT(...))",
          molecule: "Atoms(symbols='N2', pbc=False, calculator=EMT(...))",
          height: '3',
        },
        metadata: {
          backend: '<LocalExecutor>',
          executor: {
            log_stdout: '/tmp/results/log_stdout.txt',
            log_stderr: '/tmp/results/log_stderr.txt',
            conda_env: 'covalent',
            cache_dir: '',
            current_env_on_conda_fail: 'True',
            current_env: '',
          },
        },
        function_string:
          '# @ct.electron\ndef get_relaxed_slab(slab, molecule, height=1.85):\n    slab.calc = EMT()\n    add_adsorbate(slab, molecule, height, "ontop")\n    constraint = FixAtoms(mask=[a.symbol != "N" for a in slab])\n    slab.set_constraint(constraint)\n    dyn = QuasiNewton(slab, trajectory="/tmp/N2Cu.traj", logfile="/tmp/temp")\n    dyn.run(fmax=0.01)\n    return slab\n\n\n',
        start_time: '2022-01-25T20:13:08.636238+00:00',
        end_time: '2022-01-25T20:13:14.601058+00:00',
        status: 'COMPLETED',
        output:
          "Atoms(symbols='Cu32N2', pbc=[True, True, False], cell=[[10.210621920333747, 0.0, 0.0], [5.105310960166873, 8.842657971447272, 0.0], [0.0, 0.0, 22.08423447177455]], tags=..., constraint=FixAtoms(indices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]), calculator=EMT(...))",
        error: null,
        sublattice_result: null,
        stdout: '',
        stderr: '',
        exec_plan: {
          selected_executor:
            '</home/valentin/code/agnostiq/covalent-staging/covalent/executor/executor_plugins/local.LocalExecutor object at 0x7f10c18f0ac0>',
          execution_args: {},
        },
        id: 7,
        doc: null,
      },
      {
        name: ':parameter:3',
        kwargs: { height: '3' },
        metadata: {
          schedule: false,
          num_cpu: 1,
          cpu_feature_set: [],
          num_gpu: 0,
          gpu_type: '',
          gpu_compute_capability: [],
          memory: '1G',
          backend: 'local',
          time_limit: '00-00:00:00',
          budget: 0,
          conda_env: '',
          executor: {
            log_stdout: 'stdout.log',
            log_stderr: 'stderr.log',
            conda_env: '',
            cache_dir: '/tmp/covalent',
            current_env_on_conda_fail: 'False',
            current_env: '',
          },
        },
        start_time: '2022-01-25T20:13:07.184667+00:00',
        end_time: '2022-01-25T20:13:07.184672+00:00',
        status: 'COMPLETED',
        output: 3,
        error: null,
        sublattice_result: null,
        stdout: null,
        stderr: null,
        id: 8,
        doc: null,
      },
      {
        name: 'compute_system_energy',
        kwargs: {
          system:
            "Atoms(symbols='Cu32N2', pbc=[True, True, False], cell=[[10.210621920333747, 0.0, 0.0], [5.105310960166873, 8.842657971447272, 0.0], [0.0, 0.0, 22.08423447177455]], tags=..., constraint=FixAtoms(indices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]), calculator=EMT(...))",
        },
        metadata: {
          backend: '<LocalExecutor>',
          executor: {
            log_stdout: '/tmp/results/log_stdout2.txt',
            log_stderr: '/tmp/results/log_stderr2.txt',
            conda_env: '',
            cache_dir: '',
            current_env_on_conda_fail: 'True',
            current_env: '',
          },
        },
        function_string:
          '# @ct.electron(backend=executor2)\ndef compute_system_energy(system):\n    system.calc = EMT()\n    return system.get_potential_energy()\n\n\n',
        start_time: '2022-01-25T20:13:14.709556+00:00',
        end_time: '2022-01-25T20:13:15.267267+00:00',
        status: 'COMPLETED',
        output: 11.625212574435581,
        error: null,
        sublattice_result: null,
        stdout: '',
        stderr: '',
        exec_plan: {
          selected_executor:
            '</home/valentin/code/agnostiq/covalent-staging/covalent/executor/executor_plugins/local.LocalExecutor object at 0x7f10c8036bb0>',
          execution_args: {},
        },
        id: 9,
        doc: null,
      },
      {
        name: 'compute_system_energy_+_compute_system_energy',
        kwargs: { arg_1: '11.509056283570393', arg_2: '0.44034357303561467' },
        metadata: {
          backend: '<LocalExecutor>',
          executor: {
            log_stdout: '/tmp/results/log_stdout.txt',
            log_stderr: '/tmp/results/log_stderr.txt',
            conda_env: 'covalent',
            cache_dir: '',
            current_env_on_conda_fail: 'True',
            current_env: '',
          },
        },
        function_string:
          '# compute_system_energy_+_compute_system_energy was not inspectable\n\n',
        start_time: '2022-01-25T20:13:14.702711+00:00',
        end_time: '2022-01-25T20:13:17.712509+00:00',
        status: 'COMPLETED',
        output: 11.949399856606007,
        error: null,
        sublattice_result: null,
        stdout: '',
        stderr: '',
        exec_plan: {
          selected_executor:
            '</home/valentin/code/agnostiq/covalent-staging/covalent/executor/executor_plugins/local.LocalExecutor object at 0x7f10c18f0ac0>',
          execution_args: {},
        },
        id: 10,
        doc: '\n            Intermediate function for the binary operation.\n\n            Args:\n                arg_1: First operand\n                arg_2: Second operand\n\n            Returns:\n                result: Result of the binary operation.\n            ',
      },
      {
        name: 'compute_system_energy_+_compute_system_energy_-_compute_system_energy',
        kwargs: { arg_1: '11.949399856606007', arg_2: '11.625212574435581' },
        metadata: {
          backend: '<LocalExecutor>',
          executor: {
            log_stdout: '/tmp/results/log_stdout.txt',
            log_stderr: '/tmp/results/log_stderr.txt',
            conda_env: 'covalent',
            cache_dir: '',
            current_env_on_conda_fail: 'True',
            current_env: '',
          },
        },
        function_string:
          '# compute_system_energy_+_compute_system_energy_-_compute_system_energy was not inspectable\n\n',
        start_time: '2022-01-25T20:13:17.762343+00:00',
        end_time: '2022-01-25T20:13:20.495661+00:00',
        status: 'COMPLETED',
        output: 0.3241872821704259,
        error: null,
        sublattice_result: null,
        stdout: '',
        stderr: '',
        exec_plan: {
          selected_executor:
            '</home/valentin/code/agnostiq/covalent-staging/covalent/executor/executor_plugins/local.LocalExecutor object at 0x7f10c18f0ac0>',
          execution_args: {},
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

export default result
