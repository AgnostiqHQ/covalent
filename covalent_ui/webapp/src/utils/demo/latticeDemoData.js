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

const latticeDetailsDemoData = [];

//   Dispatch 2537c3b0-c150-441b-81c6-844e3fd88ef3
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"] = {}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].latticeDetails =
{
    "dispatch_id": "2537c3b0-c150-441b-81c6-844e3fd88ef3",
    "lattice_name": "compute_energy",
    "runtime": 13000,
    "total_electrons": 8,
    "total_electrons_completed": 8,
    "started_at": "2022-06-13T12:14:30",
    "ended_at": "2022-06-13T12:14:43",
    "status": "COMPLETED",
    "updated_at": "2022-08-11T12:14:40",
    "directory": "/home/covalent/Desktop/workflows/results/2537c3b0-c150-441b-81c6-844e3fd88ef3",
};
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].latticeError = null;
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].latticeResult = {
    "data": "0.3241872821704259"
};
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].latticeInput = {
    "data": "{ initial_height: '3', distance: '1.1' }"
};
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].latticeFunctionString = {
    "data": '# @ct.lattice(backend=executor1)\ndef compute_energy(initial_height=3, distance=1.10):\n    N2 = construct_n_molecule(d=distance)\n    e_N2 = compute_system_energy(system=N2)\n\n    slab = construct_cu_slab(unit_cell=(4, 4, 2), vacuum=10.0)\n    e_slab = compute_system_energy(system=slab)\n\n    relaxed_slab = get_relaxed_slab(slab=slab, molecule=N2, height=initial_height)\n    e_relaxed_slab = compute_system_energy(system=relaxed_slab)\n    final_result = e_slab + e_N2 - e_relaxed_slab\n\n    return final_result\n\n\n'
};
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].latticeExecutor = {
    "executor_name": "dask",
    "executor_details": "log_stdout: stdout.log\n    log_stderr: stderr.log\n   cache_dir: /tmp/covalent\n    current_env_on_conda_fail: False"
};
// electron data initilisation
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron = []
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[0] = {}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[2] = {}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[3] = {}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[6] = {}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[7] = {}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[9] = {}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[10] = {}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[11] = {}

latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[0].electronDetails = {
    "id": 0,
    "node_id": 0,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/2537c3b0-c150-441b-81c6-844e3fd88ef3/node_4",
    "name": "construct_n_molecule",
    "status": "COMPLETED",
    "started_at": "2022-06-13T12:14:30",
    "ended_at": "2022-06-13T12:14:30",
    "runtime": 50
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[0].electronResult = {
    "data": "Atoms(symbols='N2', pbc=False, calculator=EMT(...))"
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[0].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[0].electronFunctionString = {
    "data": '# @ct.electron\ndef construct_n_molecule(d=0):\n    return Atoms("2N", positions=[(0.0, 0.0, 0.0), (0.0, 0.0, d)])\n\n\n'
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[0].electronError = null
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[0].electronInput = {
    "data": "d=1.1"
}

latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[6].electronDetails = {
    "id": 6,
    "node_id": 6,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/2537c3b0-c150-441b-81c6-844e3fd88ef3/node_4",
    "name": "compute_system_energy",
    "status": "COMPLETED",
    "started_at": "2022-06-13T12:14:30",
    "ended_at": "2022-06-13T12:14:30",
    "runtime": 50
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[6].electronInput = {
    "data": "system=Atoms(symbols='Cu32N2', pbc=[True, True, False], cell=[[10.210621920333747, 0.0, 0.0], [5.105310960166873, 8.842657971447272, 0.0], [0.0, 0.0, 22.08423447177455]], tags=..., constraint=FixAtoms(indices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]), calculator=EMT(...))"
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[6].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[6].electronFunctionString = {
    "data": '# @ct.electron(backend=executor2)\ndef compute_system_energy(system):\n    system.calc = EMT()\n    return system.get_potential_energy()\n\n\n',
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[6].electronError = null
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[6].electronResult = {
    "data": "11.509056283570393"
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[3].electronDetails = {
    "id": 3,
    "node_id": 3,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/2537c3b0-c150-441b-81c6-844e3fd88ef3/node_4",
    "name": "construct_cu_slab",
    "status": "COMPLETED",
    "started_at": "2022-06-13T12:14:30",
    "ended_at": "2022-06-13T12:14:30",
    "runtime": 50
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[3].electronResult = {
    "data": "Atoms(symbols='Cu32N2', pbc=[True, True, False], cell=[[10.210621920333747, 0.0, 0.0], [5.105310960166873, 8.842657971447272, 0.0], [0.0, 0.0, 22.08423447177455]], tags=..., constraint=FixAtoms(indices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]), calculator=EMT(...))"
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[3].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[3].electronFunctionString = {
    "data": '# @ct.electron(backend=executor1)\ndef construct_cu_slab(\n    unit_cell=(4, 4, 2), vacuum=10.0,\n):\n    slab = fcc111("Cu", size=unit_cell, vacuum=vacuum)\n    return slab\n\n\n',
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[3].electronError = null
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[3].electronInput = {
    "data": "unit_cell=(4, 4, 2), vacuum=10.0"
}

latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[2].electronDetails = {
    "id": 2,
    "node_id": 2,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/2537c3b0-c150-441b-81c6-844e3fd88ef3/node_4",
    "name": "compute_system_energy",
    "status": "COMPLETED",
    "started_at": "2022-06-13T12:14:30",
    "ended_at": "2022-06-13T12:14:30",
    "runtime": 50
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[2].electronResult = {
    "data": "0.44034357303561467"
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[2].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[2].electronFunctionString = {
    "data": '# @ct.electron(backend=executor2)\ndef compute_system_energy(system):\n    system.calc = EMT()\n    return system.get_potential_energy()\n\n\n',
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[2].electronError = null
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[2].electronInput = {
    "data": "system=Atoms(symbols='N2', pbc=False, calculator=EMT(...))"
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[7].electronDetails = {
    "id": 7,
    "node_id": 7,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/2537c3b0-c150-441b-81c6-844e3fd88ef3/node_4",
    "name": "get_relaxed_slab",
    "status": "COMPLETED",
    "started_at": "2022-06-13T12:14:30",
    "ended_at": "2022-06-13T12:14:30",
    "runtime": 50
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[7].electronResult = {
    "data": "Atoms(symbols='Cu32N2', pbc=[True, True, False], cell=[[10.210621920333747, 0.0, 0.0], [5.105310960166873, 8.842657971447272, 0.0], [0.0, 0.0, 22.08423447177455]], tags=..., constraint=FixAtoms(indices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]), calculator=EMT(...))"
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[7].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[7].electronFunctionString = {
    "data": '# @ct.electron\ndef get_relaxed_slab(slab, molecule, height=1.85):\n    slab.calc = EMT()\n    add_adsorbate(slab, molecule, height, "ontop")\n    constraint = FixAtoms(mask=[a.symbol != "N" for a in slab])\n    slab.set_constraint(constraint)\n    dyn = QuasiNewton(slab, trajectory="/tmp/N2Cu.traj", logfile="/tmp/temp")\n    dyn.run(fmax=0.01)\n    return slab\n\n\n',
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[7].electronError = null
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[7].electronInput = {
    "data": "slab=Atoms(symbols='Cu32N2', pbc=[True, True, False], cell=[[10.210621920333747, 0.0, 0.0], [5.105310960166873, 8.842657971447272, 0.0], [0.0, 0.0, 22.08423447177455]], tags=..., constraint=FixAtoms(indices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]), calculator=EMT(...)), molecule=Atoms(symbols='N2', pbc=False, calculator=EMT(...)), height=3"
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[9].electronDetails = {
    "id": 9,
    "node_id": 9,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/2537c3b0-c150-441b-81c6-844e3fd88ef3/node_4",
    "name": "compute_system_energy",
    "status": "COMPLETED",
    "started_at": "2022-06-13T12:14:30",
    "ended_at": "2022-06-13T12:14:30",
    "runtime": 50
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[9].electronInput = {
    "data": "system=Atoms(symbols='Cu32N2', pbc=[True, True, False], cell=[[10.210621920333747, 0.0, 0.0], [5.105310960166873, 8.842657971447272, 0.0], [0.0, 0.0, 22.08423447177455]], tags=..., constraint=FixAtoms(indices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]), calculator=EMT(...))"
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[9].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[9].electronFunctionString = {
    "data": '# @ct.electron(backend=executor2)\ndef compute_system_energy(system):\n    system.calc = EMT()\n    return system.get_potential_energy()\n\n\n',
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[9].electronError = null
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[9].electronResult = {
    "data": "11.625212574435581"
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[10].electronDetails = {
    "id": 10,
    "node_id": 10,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/2537c3b0-c150-441b-81c6-844e3fd88ef3/node_4",
    "name": "compute_system_energy_+_compute_system_energy",
    "status": "COMPLETED",
    "started_at": "2022-06-13T12:14:30",
    "ended_at": "2022-06-13T12:14:30",
    "runtime": 50
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[10].electronResult = {
    "data": "11.949399856606007"
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[10].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[10].electronFunctionString = {
    "data": '# compute_system_energy_+_compute_system_energy was not inspectable\n\n',
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[10].electronError = null
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[10].electronInput = {
    "data": "arg_1=11.509056283570393, arg_2=0.44034357303561467"
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[11].electronDetails = {
    "id": 11,
    "node_id": 11,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/2537c3b0-c150-441b-81c6-844e3fd88ef3/node_4",
    "name": "compute_system_energy_+_compute_system_energy_-_compute_system_energy",
    "status": "COMPLETED",
    "started_at": "2022-06-13T12:14:30",
    "ended_at": "2022-06-13T12:14:30",
    "runtime": 50
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[11].electronResult = {
    "data": "0.3241872821704259"
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[11].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[11].electronFunctionString = {
    "data": '# compute_system_energy_+_compute_system_energy_-_compute_system_energy was not inspectable',
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[11].electronError = null
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[11].electronInput = {
    "data": "arg_1=11.949399856606007, arg_2=11.625212574435581"
}

//   Dispatch eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a
latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"] = {}
latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].latticeDetails =
{
    "dispatch_id": "eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a",
    "lattice_name": "compute_energy",
    "runtime": 13000,
    "total_electrons": 8,
    "total_electrons_completed": 8,
    "started_at": "2022-06-13T12:14:30",
    "ended_at": "2022-06-13T12:14:43",
    "status": "COMPLETED",
    "updated_at": "2022-08-11T12:14:40",
    "directory": "/home/covalent/Desktop/workflows/results/eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a",
};
latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].latticeError = null;
latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].latticeResult = {
    "data": "0.3241872821704259"
};
latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].latticeInput = {
    "data": "{ initial_height: '3', distance: '1.1' }"
};
latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].latticeFunctionString = {
    "data": '# @ct.lattice(backend=executor1)\ndef compute_energy(initial_height=3, distance=1.10):\n    N2 = construct_n_molecule(d=distance)\n    e_N2 = compute_system_energy(system=N2)\n\n    slab = construct_cu_slab(unit_cell=(4, 4, 2), vacuum=10.0)\n    e_slab = compute_system_energy(system=slab)\n\n    relaxed_slab = get_relaxed_slab(slab=slab, molecule=N2, height=initial_height)\n    e_relaxed_slab = compute_system_energy(system=relaxed_slab)\n    final_result = e_slab + e_N2 - e_relaxed_slab\n\n    return final_result\n\n\n'
};
latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].latticeExecutor = {
    "executor_name": "dask",
    "executor_details": "log_stdout: stdout.log\n    log_stderr: stderr.log\n   cache_dir: /tmp/covalent\n    current_env_on_conda_fail: False"
};
// electron data initilisation
latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].electron = []
latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].electron[0] = {}
latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].electron[2] = {}
latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].electron[3] = {}
latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].electron[6] = {}
latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].electron[7] = {}
latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].electron[9] = {}
latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].electron[10] = {}
latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].electron[11] = {}

latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].electron[0].electronDetails = {
    "id": 0,
    "node_id": 0,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a/node_4",
    "name": "construct_n_molecule",
    "status": "COMPLETED",
    "started_at": "2022-06-13T12:14:30",
    "ended_at": "2022-06-13T12:14:30",
    "runtime": 50
}
latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].electron[0].electronResult = {
    "data": "Atoms(symbols='N2', pbc=False, calculator=EMT(...))"
}
latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].electron[0].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].electron[0].electronFunctionString = {
    "data": '# @ct.electron\ndef construct_n_molecule(d=0):\n    return Atoms("2N", positions=[(0.0, 0.0, 0.0), (0.0, 0.0, d)])\n\n\n'
}
latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].electron[0].electronError = null
latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].electron[0].electronInput = {
    "data": "d=1.1"
}

latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].electron[6].electronDetails = {
    "id": 6,
    "node_id": 6,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a/node_4",
    "name": "compute_system_energy",
    "status": "COMPLETED",
    "started_at": "2022-06-13T12:14:30",
    "ended_at": "2022-06-13T12:14:30",
    "runtime": 50
}
latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].electron[6].electronInput = {
    "data": "system=Atoms(symbols='Cu32N2', pbc=[True, True, False], cell=[[10.210621920333747, 0.0, 0.0], [5.105310960166873, 8.842657971447272, 0.0], [0.0, 0.0, 22.08423447177455]], tags=..., constraint=FixAtoms(indices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]), calculator=EMT(...))"
}
latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].electron[6].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].electron[6].electronFunctionString = {
    "data": '# @ct.electron(backend=executor2)\ndef compute_system_energy(system):\n    system.calc = EMT()\n    return system.get_potential_energy()\n\n\n',
}
latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].electron[6].electronError = null
latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].electron[6].electronResult = {
    "data": "11.509056283570393"
}
latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].electron[3].electronDetails = {
    "id": 3,
    "node_id": 3,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a/node_4",
    "name": "construct_cu_slab",
    "status": "COMPLETED",
    "started_at": "2022-06-13T12:14:30",
    "ended_at": "2022-06-13T12:14:30",
    "runtime": 50
}
latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].electron[3].electronResult = {
    "data": "Atoms(symbols='Cu32N2', pbc=[True, True, False], cell=[[10.210621920333747, 0.0, 0.0], [5.105310960166873, 8.842657971447272, 0.0], [0.0, 0.0, 22.08423447177455]], tags=..., constraint=FixAtoms(indices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]), calculator=EMT(...))"
}
latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].electron[3].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].electron[3].electronFunctionString = {
    "data": '# @ct.electron(backend=executor1)\ndef construct_cu_slab(\n    unit_cell=(4, 4, 2), vacuum=10.0,\n):\n    slab = fcc111("Cu", size=unit_cell, vacuum=vacuum)\n    return slab\n\n\n',
}
latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].electron[3].electronError = null
latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].electron[3].electronInput = {
    "data": "unit_cell=(4, 4, 2), vacuum=10.0"
}

latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].electron[2].electronDetails = {
    "id": 2,
    "node_id": 2,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a/node_4",
    "name": "compute_system_energy",
    "status": "COMPLETED",
    "started_at": "2022-06-13T12:14:30",
    "ended_at": "2022-06-13T12:14:30",
    "runtime": 50
}
latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].electron[2].electronResult = {
    "data": "0.44034357303561467"
}
latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].electron[2].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].electron[2].electronFunctionString = {
    "data": '# @ct.electron(backend=executor2)\ndef compute_system_energy(system):\n    system.calc = EMT()\n    return system.get_potential_energy()\n\n\n',
}
latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].electron[2].electronError = null
latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].electron[2].electronInput = {
    "data": "system=Atoms(symbols='N2', pbc=False, calculator=EMT(...))"
}
latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].electron[7].electronDetails = {
    "id": 7,
    "node_id": 7,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a/node_4",
    "name": "get_relaxed_slab",
    "status": "COMPLETED",
    "started_at": "2022-06-13T12:14:30",
    "ended_at": "2022-06-13T12:14:30",
    "runtime": 50
}
latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].electron[7].electronResult = {
    "data": "Atoms(symbols='Cu32N2', pbc=[True, True, False], cell=[[10.210621920333747, 0.0, 0.0], [5.105310960166873, 8.842657971447272, 0.0], [0.0, 0.0, 22.08423447177455]], tags=..., constraint=FixAtoms(indices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]), calculator=EMT(...))"
}
latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].electron[7].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].electron[7].electronFunctionString = {
    "data": '# @ct.electron\ndef get_relaxed_slab(slab, molecule, height=1.85):\n    slab.calc = EMT()\n    add_adsorbate(slab, molecule, height, "ontop")\n    constraint = FixAtoms(mask=[a.symbol != "N" for a in slab])\n    slab.set_constraint(constraint)\n    dyn = QuasiNewton(slab, trajectory="/tmp/N2Cu.traj", logfile="/tmp/temp")\n    dyn.run(fmax=0.01)\n    return slab\n\n\n',
}
latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].electron[7].electronError = null
latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].electron[7].electronInput = {
    "data": "slab=Atoms(symbols='Cu32N2', pbc=[True, True, False], cell=[[10.210621920333747, 0.0, 0.0], [5.105310960166873, 8.842657971447272, 0.0], [0.0, 0.0, 22.08423447177455]], tags=..., constraint=FixAtoms(indices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]), calculator=EMT(...)), molecule=Atoms(symbols='N2', pbc=False, calculator=EMT(...)), height=3"
}
latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].electron[9].electronDetails = {
    "id": 9,
    "node_id": 9,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a/node_4",
    "name": "compute_system_energy",
    "status": "COMPLETED",
    "started_at": "2022-06-13T12:14:30",
    "ended_at": "2022-06-13T12:14:30",
    "runtime": 50
}
latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].electron[9].electronInput = {
    "data": "system=Atoms(symbols='Cu32N2', pbc=[True, True, False], cell=[[10.210621920333747, 0.0, 0.0], [5.105310960166873, 8.842657971447272, 0.0], [0.0, 0.0, 22.08423447177455]], tags=..., constraint=FixAtoms(indices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]), calculator=EMT(...))"
}
latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].electron[9].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].electron[9].electronFunctionString = {
    "data": '# @ct.electron(backend=executor2)\ndef compute_system_energy(system):\n    system.calc = EMT()\n    return system.get_potential_energy()\n\n\n',
}
latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].electron[9].electronError = null
latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].electron[9].electronResult = {
    "data": "11.625212574435581"
}
latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].electron[10].electronDetails = {
    "id": 10,
    "node_id": 10,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a/node_4",
    "name": "compute_system_energy_+_compute_system_energy",
    "status": "COMPLETED",
    "started_at": "2022-06-13T12:14:30",
    "ended_at": "2022-06-13T12:14:30",
    "runtime": 50
}
latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].electron[10].electronResult = {
    "data": "11.949399856606007"
}
latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].electron[10].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].electron[10].electronFunctionString = {
    "data": '# compute_system_energy_+_compute_system_energy was not inspectable\n\n',
}
latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].electron[10].electronError = null
latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].electron[10].electronInput = {
    "data": "arg_1=11.509056283570393, arg_2=0.44034357303561467"
}
latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].electron[11].electronDetails = {
    "id": 11,
    "node_id": 11,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a/node_4",
    "name": "compute_system_energy_+_compute_system_energy_-_compute_system_energy",
    "status": "COMPLETED",
    "started_at": "2022-06-13T12:14:30",
    "ended_at": "2022-06-13T12:14:30",
    "runtime": 50
}
latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].electron[11].electronResult = {
    "data": "0.3241872821704259"
}
latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].electron[11].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].electron[11].electronFunctionString = {
    "data": '# compute_system_energy_+_compute_system_energy_-_compute_system_energy was not inspectable',
}
latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].electron[11].electronError = null
latticeDetailsDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"].electron[11].electronInput = {
    "data": "arg_1=11.949399856606007, arg_2=11.625212574435581"
}

//   Dispatch fcd385e2-7881-4bcd-862c-2ac99706d2f9
latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"] = {}
latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].latticeDetails =
{
    "dispatch_id": "fcd385e2-7881-4bcd-862c-2ac99706d2f9",
    "lattice_name": "compute_energy",
    "runtime": 13000,
    "total_electrons": 8,
    "total_electrons_completed": 8,
    "started_at": "2022-06-15T10:14:40",
    "ended_at": "2022-06-15T10:14:53",
    "status": "COMPLETED",
    "updated_at": "2022-08-11T12:14:40",
    "directory": "/home/covalent/Desktop/workflows/results/fcd385e2-7881-4bcd-862c-2ac99706d2f9",
};
latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].latticeError = null;
latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].latticeResult = {
    "data": "0.3241872821704259"
};
latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].latticeInput = {
    "data": "{ initial_height: '3', distance: '1.1' }"
};
latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].latticeFunctionString = {
    "data": '# @ct.lattice(backend=executor1)\ndef compute_energy(initial_height=3, distance=1.10):\n    N2 = construct_n_molecule(d=distance)\n    e_N2 = compute_system_energy(system=N2)\n\n    slab = construct_cu_slab(unit_cell=(4, 4, 2), vacuum=10.0)\n    e_slab = compute_system_energy(system=slab)\n\n    relaxed_slab = get_relaxed_slab(slab=slab, molecule=N2, height=initial_height)\n    e_relaxed_slab = compute_system_energy(system=relaxed_slab)\n    final_result = e_slab + e_N2 - e_relaxed_slab\n\n    return final_result\n\n\n'
};
latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].latticeExecutor = {
    "executor_name": "dask",
    "executor_details": "log_stdout: stdout.log\n    log_stderr: stderr.log\n   cache_dir: /tmp/covalent\n    current_env_on_conda_fail: False"
};
// electron data initilisation
latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].electron = []
latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].electron[0] = {}
latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].electron[2] = {}
latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].electron[3] = {}
latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].electron[6] = {}
latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].electron[7] = {}
latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].electron[9] = {}
latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].electron[10] = {}
latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].electron[11] = {}

latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].electron[0].electronDetails = {
    "id": 0,
    "node_id": 0,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/fcd385e2-7881-4bcd-862c-2ac99706d2f9/node_4",
    "name": "construct_n_molecule",
    "status": "COMPLETED",
    "started_at": "2022-06-15T10:14:40",
    "ended_at": "2022-06-15T10:14:40",
    "runtime": 50
}
latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].electron[0].electronResult = {
    "data": "Atoms(symbols='N2', pbc=False, calculator=EMT(...))"
}
latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].electron[0].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].electron[0].electronFunctionString = {
    "data": '# @ct.electron\ndef construct_n_molecule(d=0):\n    return Atoms("2N", positions=[(0.0, 0.0, 0.0), (0.0, 0.0, d)])\n\n\n'
}
latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].electron[0].electronError = null
latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].electron[0].electronInput = {
    "data": "d=1.1"
}

latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].electron[6].electronDetails = {
    "id": 6,
    "node_id": 6,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/fcd385e2-7881-4bcd-862c-2ac99706d2f9/node_4",
    "name": "compute_system_energy",
    "status": "COMPLETED",
    "started_at": "2022-06-15T10:14:40",
    "ended_at": "2022-06-15T10:14:40",
    "runtime": 50
}
latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].electron[6].electronInput = {
    "data": "system=Atoms(symbols='Cu32N2', pbc=[True, True, False], cell=[[10.210621920333747, 0.0, 0.0], [5.105310960166873, 8.842657971447272, 0.0], [0.0, 0.0, 22.08423447177455]], tags=..., constraint=FixAtoms(indices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]), calculator=EMT(...))"
}
latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].electron[6].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].electron[6].electronFunctionString = {
    "data": '# @ct.electron(backend=executor2)\ndef compute_system_energy(system):\n    system.calc = EMT()\n    return system.get_potential_energy()\n\n\n',
}
latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].electron[6].electronError = null
latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].electron[6].electronResult = {
    "data": "11.509056283570393"
}
latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].electron[3].electronDetails = {
    "id": 3,
    "node_id": 3,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/fcd385e2-7881-4bcd-862c-2ac99706d2f9/node_4",
    "name": "construct_cu_slab",
    "status": "COMPLETED",
    "started_at": "2022-06-15T10:14:40",
    "ended_at": "2022-06-15T10:14:40",
    "runtime": 50
}
latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].electron[3].electronResult = {
    "data": "Atoms(symbols='Cu32N2', pbc=[True, True, False], cell=[[10.210621920333747, 0.0, 0.0], [5.105310960166873, 8.842657971447272, 0.0], [0.0, 0.0, 22.08423447177455]], tags=..., constraint=FixAtoms(indices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]), calculator=EMT(...))"
}
latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].electron[3].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].electron[3].electronFunctionString = {
    "data": '# @ct.electron(backend=executor1)\ndef construct_cu_slab(\n    unit_cell=(4, 4, 2), vacuum=10.0,\n):\n    slab = fcc111("Cu", size=unit_cell, vacuum=vacuum)\n    return slab\n\n\n',
}
latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].electron[3].electronError = null
latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].electron[3].electronInput = {
    "data": "unit_cell=(4, 4, 2), vacuum=10.0"
}

latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].electron[2].electronDetails = {
    "id": 2,
    "node_id": 2,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/fcd385e2-7881-4bcd-862c-2ac99706d2f9/node_4",
    "name": "compute_system_energy",
    "status": "COMPLETED",
    "started_at": "2022-06-15T10:14:40",
    "ended_at": "2022-06-15T10:14:40",
    "runtime": 50
}
latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].electron[2].electronResult = {
    "data": "0.44034357303561467"
}
latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].electron[2].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].electron[2].electronFunctionString = {
    "data": '# @ct.electron(backend=executor2)\ndef compute_system_energy(system):\n    system.calc = EMT()\n    return system.get_potential_energy()\n\n\n',
}
latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].electron[2].electronError = null
latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].electron[2].electronInput = {
    "data": "system=Atoms(symbols='N2', pbc=False, calculator=EMT(...))"
}
latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].electron[7].electronDetails = {
    "id": 7,
    "node_id": 7,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/fcd385e2-7881-4bcd-862c-2ac99706d2f9/node_4",
    "name": "get_relaxed_slab",
    "status": "COMPLETED",
    "started_at": "2022-06-15T10:14:40",
    "ended_at": "2022-06-15T10:14:40",
    "runtime": 50
}
latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].electron[7].electronResult = {
    "data": "Atoms(symbols='Cu32N2', pbc=[True, True, False], cell=[[10.210621920333747, 0.0, 0.0], [5.105310960166873, 8.842657971447272, 0.0], [0.0, 0.0, 22.08423447177455]], tags=..., constraint=FixAtoms(indices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]), calculator=EMT(...))"
}
latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].electron[7].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].electron[7].electronFunctionString = {
    "data": '# @ct.electron\ndef get_relaxed_slab(slab, molecule, height=1.85):\n    slab.calc = EMT()\n    add_adsorbate(slab, molecule, height, "ontop")\n    constraint = FixAtoms(mask=[a.symbol != "N" for a in slab])\n    slab.set_constraint(constraint)\n    dyn = QuasiNewton(slab, trajectory="/tmp/N2Cu.traj", logfile="/tmp/temp")\n    dyn.run(fmax=0.01)\n    return slab\n\n\n',
}
latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].electron[7].electronError = null
latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].electron[7].electronInput = {
    "data": "slab=Atoms(symbols='Cu32N2', pbc=[True, True, False], cell=[[10.210621920333747, 0.0, 0.0], [5.105310960166873, 8.842657971447272, 0.0], [0.0, 0.0, 22.08423447177455]], tags=..., constraint=FixAtoms(indices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]), calculator=EMT(...)), molecule=Atoms(symbols='N2', pbc=False, calculator=EMT(...)), height=3"
}
latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].electron[9].electronDetails = {
    "id": 9,
    "node_id": 9,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/fcd385e2-7881-4bcd-862c-2ac99706d2f9/node_4",
    "name": "compute_system_energy",
    "status": "COMPLETED",
    "started_at": "2022-06-15T10:14:40",
    "ended_at": "2022-06-15T10:14:40",
    "runtime": 50
}
latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].electron[9].electronInput = {
    "data": "system=Atoms(symbols='Cu32N2', pbc=[True, True, False], cell=[[10.210621920333747, 0.0, 0.0], [5.105310960166873, 8.842657971447272, 0.0], [0.0, 0.0, 22.08423447177455]], tags=..., constraint=FixAtoms(indices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]), calculator=EMT(...))"
}
latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].electron[9].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].electron[9].electronFunctionString = {
    "data": '# @ct.electron(backend=executor2)\ndef compute_system_energy(system):\n    system.calc = EMT()\n    return system.get_potential_energy()\n\n\n',
}
latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].electron[9].electronError = null
latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].electron[9].electronResult = {
    "data": "11.625212574435581"
}
latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].electron[10].electronDetails = {
    "id": 10,
    "node_id": 10,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/fcd385e2-7881-4bcd-862c-2ac99706d2f9/node_4",
    "name": "compute_system_energy_+_compute_system_energy",
    "status": "COMPLETED",
    "started_at": "2022-06-15T10:14:40",
    "ended_at": "2022-06-15T10:14:40",
    "runtime": 50
}
latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].electron[10].electronResult = {
    "data": "11.949399856606007"
}
latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].electron[10].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].electron[10].electronFunctionString = {
    "data": '# compute_system_energy_+_compute_system_energy was not inspectable\n\n',
}
latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].electron[10].electronError = null
latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].electron[10].electronInput = {
    "data": "arg_1=11.509056283570393, arg_2=0.44034357303561467"
}
latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].electron[11].electronDetails = {
    "id": 11,
    "node_id": 11,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/fcd385e2-7881-4bcd-862c-2ac99706d2f9/node_4",
    "name": "compute_system_energy_+_compute_system_energy_-_compute_system_energy",
    "status": "COMPLETED",
    "started_at": "2022-06-15T10:14:40",
    "ended_at": "2022-06-15T10:14:40",
    "runtime": 50
}
latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].electron[11].electronResult = {
    "data": "0.3241872821704259"
}
latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].electron[11].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].electron[11].electronFunctionString = {
    "data": '# compute_system_energy_+_compute_system_energy_-_compute_system_energy was not inspectable',
}
latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].electron[11].electronError = null
latticeDetailsDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"].electron[11].electronInput = {
    "data": "arg_1=11.949399856606007, arg_2=11.625212574435581"
}


//   Dispatch b199afa5-301f-47d8-a8dc-fd78e1f5d08a
latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"] = {}
latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].latticeDetails =
{
    "dispatch_id": "b199afa5-301f-47d8-a8dc-fd78e1f5d08a",
    "lattice_name": "compute_energy",
    "runtime": 13000,
    "total_electrons": 8,
    "total_electrons_completed": 8,
    "started_at": "2022-06-11T08:14:10",
    "ended_at": "2022-06-11T08:14:23",
    "status": "COMPLETED",
    "updated_at": "2022-08-11T12:14:40",
    "directory": "/home/covalent/Desktop/workflows/results/b199afa5-301f-47d8-a8dc-fd78e1f5d08a",
};
latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].latticeError = null;
latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].latticeResult = {
    "data": "0.3241872821704259"
};
latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].latticeInput = {
    "data": "{ initial_height: '3', distance: '1.1' }"
};
latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].latticeFunctionString = {
    "data": '# @ct.lattice(backend=executor1)\ndef compute_energy(initial_height=3, distance=1.10):\n    N2 = construct_n_molecule(d=distance)\n    e_N2 = compute_system_energy(system=N2)\n\n    slab = construct_cu_slab(unit_cell=(4, 4, 2), vacuum=10.0)\n    e_slab = compute_system_energy(system=slab)\n\n    relaxed_slab = get_relaxed_slab(slab=slab, molecule=N2, height=initial_height)\n    e_relaxed_slab = compute_system_energy(system=relaxed_slab)\n    final_result = e_slab + e_N2 - e_relaxed_slab\n\n    return final_result\n\n\n'
};
latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].latticeExecutor = {
    "executor_name": "dask",
    "executor_details": "log_stdout: stdout.log\n    log_stderr: stderr.log\n   cache_dir: /tmp/covalent\n    current_env_on_conda_fail: False"
};
// electron data initilisation
latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].electron = []
latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].electron[0] = {}
latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].electron[2] = {}
latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].electron[3] = {}
latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].electron[6] = {}
latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].electron[7] = {}
latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].electron[9] = {}
latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].electron[10] = {}
latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].electron[11] = {}

latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].electron[0].electronDetails = {
    "id": 0,
    "node_id": 0,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/b199afa5-301f-47d8-a8dc-fd78e1f5d08a/node_4",
    "name": "construct_n_molecule",
    "status": "COMPLETED",
    "started_at": "2022-06-11T08:14:10",
    "ended_at": "2022-06-11T08:14:10",
    "runtime": 50
}
latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].electron[0].electronResult = {
    "data": "Atoms(symbols='N2', pbc=False, calculator=EMT(...))"
}
latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].electron[0].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].electron[0].electronFunctionString = {
    "data": '# @ct.electron\ndef construct_n_molecule(d=0):\n    return Atoms("2N", positions=[(0.0, 0.0, 0.0), (0.0, 0.0, d)])\n\n\n'
}
latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].electron[0].electronError = null
latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].electron[0].electronInput = {
    "data": "d=1.1"
}

latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].electron[6].electronDetails = {
    "id": 6,
    "node_id": 6,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/b199afa5-301f-47d8-a8dc-fd78e1f5d08a/node_4",
    "name": "compute_system_energy",
    "status": "COMPLETED",
    "started_at": "2022-06-11T08:14:10",
    "ended_at": "2022-06-11T08:14:10",
    "runtime": 50
}
latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].electron[6].electronInput = {
    "data": "system=Atoms(symbols='Cu32N2', pbc=[True, True, False], cell=[[10.210621920333747, 0.0, 0.0], [5.105310960166873, 8.842657971447272, 0.0], [0.0, 0.0, 22.08423447177455]], tags=..., constraint=FixAtoms(indices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]), calculator=EMT(...))"
}
latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].electron[6].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].electron[6].electronFunctionString = {
    "data": '# @ct.electron(backend=executor2)\ndef compute_system_energy(system):\n    system.calc = EMT()\n    return system.get_potential_energy()\n\n\n',
}
latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].electron[6].electronError = null
latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].electron[6].electronResult = {
    "data": "11.509056283570393"
}
latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].electron[3].electronDetails = {
    "id": 3,
    "node_id": 3,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/b199afa5-301f-47d8-a8dc-fd78e1f5d08a/node_4",
    "name": "construct_cu_slab",
    "status": "COMPLETED",
    "started_at": "2022-06-11T08:14:10",
    "ended_at": "2022-06-11T08:14:10",
    "runtime": 50
}
latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].electron[3].electronResult = {
    "data": "Atoms(symbols='Cu32N2', pbc=[True, True, False], cell=[[10.210621920333747, 0.0, 0.0], [5.105310960166873, 8.842657971447272, 0.0], [0.0, 0.0, 22.08423447177455]], tags=..., constraint=FixAtoms(indices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]), calculator=EMT(...))"
}
latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].electron[3].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].electron[3].electronFunctionString = {
    "data": '# @ct.electron(backend=executor1)\ndef construct_cu_slab(\n    unit_cell=(4, 4, 2), vacuum=10.0,\n):\n    slab = fcc111("Cu", size=unit_cell, vacuum=vacuum)\n    return slab\n\n\n',
}
latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].electron[3].electronError = null
latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].electron[3].electronInput = {
    "data": "unit_cell=(4, 4, 2), vacuum=10.0"
}

latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].electron[2].electronDetails = {
    "id": 2,
    "node_id": 2,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/b199afa5-301f-47d8-a8dc-fd78e1f5d08a/node_4",
    "name": "compute_system_energy",
    "status": "COMPLETED",
    "started_at": "2022-06-11T08:14:10",
    "ended_at": "2022-06-11T08:14:10",
    "runtime": 50
}
latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].electron[2].electronResult = {
    "data": "0.44034357303561467"
}
latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].electron[2].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].electron[2].electronFunctionString = {
    "data": '# @ct.electron(backend=executor2)\ndef compute_system_energy(system):\n    system.calc = EMT()\n    return system.get_potential_energy()\n\n\n',
}
latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].electron[2].electronError = null
latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].electron[2].electronInput = {
    "data": "system=Atoms(symbols='N2', pbc=False, calculator=EMT(...))"
}
latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].electron[7].electronDetails = {
    "id": 7,
    "node_id": 7,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/b199afa5-301f-47d8-a8dc-fd78e1f5d08a/node_4",
    "name": "get_relaxed_slab",
    "status": "COMPLETED",
    "started_at": "2022-06-11T08:14:10",
    "ended_at": "2022-06-11T08:14:10",
    "runtime": 50
}
latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].electron[7].electronResult = {
    "data": "Atoms(symbols='Cu32N2', pbc=[True, True, False], cell=[[10.210621920333747, 0.0, 0.0], [5.105310960166873, 8.842657971447272, 0.0], [0.0, 0.0, 22.08423447177455]], tags=..., constraint=FixAtoms(indices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]), calculator=EMT(...))"
}
latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].electron[7].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].electron[7].electronFunctionString = {
    "data": '# @ct.electron\ndef get_relaxed_slab(slab, molecule, height=1.85):\n    slab.calc = EMT()\n    add_adsorbate(slab, molecule, height, "ontop")\n    constraint = FixAtoms(mask=[a.symbol != "N" for a in slab])\n    slab.set_constraint(constraint)\n    dyn = QuasiNewton(slab, trajectory="/tmp/N2Cu.traj", logfile="/tmp/temp")\n    dyn.run(fmax=0.01)\n    return slab\n\n\n',
}
latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].electron[7].electronError = null
latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].electron[7].electronInput = {
    "data": "slab=Atoms(symbols='Cu32N2', pbc=[True, True, False], cell=[[10.210621920333747, 0.0, 0.0], [5.105310960166873, 8.842657971447272, 0.0], [0.0, 0.0, 22.08423447177455]], tags=..., constraint=FixAtoms(indices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]), calculator=EMT(...)), molecule=Atoms(symbols='N2', pbc=False, calculator=EMT(...)), height=3"
}
latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].electron[9].electronDetails = {
    "id": 9,
    "node_id": 9,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/b199afa5-301f-47d8-a8dc-fd78e1f5d08a/node_4",
    "name": "compute_system_energy",
    "status": "COMPLETED",
    "started_at": "2022-06-11T08:14:10",
    "ended_at": "2022-06-11T08:14:10",
    "runtime": 50
}
latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].electron[9].electronInput = {
    "data": "system=Atoms(symbols='Cu32N2', pbc=[True, True, False], cell=[[10.210621920333747, 0.0, 0.0], [5.105310960166873, 8.842657971447272, 0.0], [0.0, 0.0, 22.08423447177455]], tags=..., constraint=FixAtoms(indices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]), calculator=EMT(...))"
}
latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].electron[9].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].electron[9].electronFunctionString = {
    "data": '# @ct.electron(backend=executor2)\ndef compute_system_energy(system):\n    system.calc = EMT()\n    return system.get_potential_energy()\n\n\n',
}
latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].electron[9].electronError = null
latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].electron[9].electronResult = {
    "data": "11.625212574435581"
}
latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].electron[10].electronDetails = {
    "id": 10,
    "node_id": 10,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/b199afa5-301f-47d8-a8dc-fd78e1f5d08a/node_4",
    "name": "compute_system_energy_+_compute_system_energy",
    "status": "COMPLETED",
    "started_at": "2022-06-11T08:14:10",
    "ended_at": "2022-06-11T08:14:10",
    "runtime": 50
}
latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].electron[10].electronResult = {
    "data": "11.949399856606007"
}
latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].electron[10].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].electron[10].electronFunctionString = {
    "data": '# compute_system_energy_+_compute_system_energy was not inspectable\n\n',
}
latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].electron[10].electronError = null
latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].electron[10].electronInput = {
    "data": "arg_1=11.509056283570393, arg_2=0.44034357303561467"
}
latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].electron[11].electronDetails = {
    "id": 11,
    "node_id": 11,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/b199afa5-301f-47d8-a8dc-fd78e1f5d08a/node_4",
    "name": "compute_system_energy_+_compute_system_energy_-_compute_system_energy",
    "status": "COMPLETED",
    "started_at": "2022-06-11T08:14:10",
    "ended_at": "2022-06-11T08:14:10",
    "runtime": 50
}
latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].electron[11].electronResult = {
    "data": "0.3241872821704259"
}
latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].electron[11].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].electron[11].electronFunctionString = {
    "data": '# compute_system_energy_+_compute_system_energy_-_compute_system_energy was not inspectable',
}
latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].electron[11].electronError = null
latticeDetailsDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"].electron[11].electronInput = {
    "data": "arg_1=11.949399856606007, arg_2=11.625212574435581"
}

//   Dispatch df4601e7-7658-4a14-a860-f91a35a1b453
latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"] = {}
latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].latticeDetails =
{
    "dispatch_id": "df4601e7-7658-4a14-a860-f91a35a1b453",
    "lattice_name": "compute_energy",
    "runtime": 13000,
    "total_electrons": 8,
    "total_electrons_completed": 8,
    "started_at": "2022-06-13T12:14:30",
    "ended_at": "2022-06-13T12:14:43",
    "status": "COMPLETED",
    "updated_at": "2022-08-11T12:14:40",
    "directory": "/home/covalent/Desktop/workflows/results/df4601e7-7658-4a14-a860-f91a35a1b453",
};
latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].latticeError = null;
latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].latticeResult = {
    "data": "0.3241872821704259"
};
latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].latticeInput = {
    "data": "{ initial_height: '3', distance: '1.1' }"
};
latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].latticeFunctionString = {
    "data": '# @ct.lattice(backend=executor1)\ndef compute_energy(initial_height=3, distance=1.10):\n    N2 = construct_n_molecule(d=distance)\n    e_N2 = compute_system_energy(system=N2)\n\n    slab = construct_cu_slab(unit_cell=(4, 4, 2), vacuum=10.0)\n    e_slab = compute_system_energy(system=slab)\n\n    relaxed_slab = get_relaxed_slab(slab=slab, molecule=N2, height=initial_height)\n    e_relaxed_slab = compute_system_energy(system=relaxed_slab)\n    final_result = e_slab + e_N2 - e_relaxed_slab\n\n    return final_result\n\n\n'
};
latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].latticeExecutor = {
    "executor_name": "dask",
    "executor_details": "log_stdout: stdout.log\n    log_stderr: stderr.log\n   cache_dir: /tmp/covalent\n    current_env_on_conda_fail: False"
};
// electron data initilisation
latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].electron = []
latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].electron[0] = {}
latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].electron[2] = {}
latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].electron[3] = {}
latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].electron[6] = {}
latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].electron[7] = {}
latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].electron[9] = {}
latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].electron[10] = {}
latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].electron[11] = {}

latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].electron[0].electronDetails = {
    "id": 0,
    "node_id": 0,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/df4601e7-7658-4a14-a860-f91a35a1b453/node_4",
    "name": "construct_n_molecule",
    "status": "COMPLETED",
    "started_at": "2022-06-13T12:14:30",
    "ended_at": "2022-06-13T12:14:30",
    "runtime": 50
}
latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].electron[0].electronResult = {
    "data": "Atoms(symbols='N2', pbc=False, calculator=EMT(...))"
}
latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].electron[0].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].electron[0].electronFunctionString = {
    "data": '# @ct.electron\ndef construct_n_molecule(d=0):\n    return Atoms("2N", positions=[(0.0, 0.0, 0.0), (0.0, 0.0, d)])\n\n\n'
}
latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].electron[0].electronError = null
latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].electron[0].electronInput = {
    "data": "d=1.1"
}

latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].electron[6].electronDetails = {
    "id": 6,
    "node_id": 6,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/df4601e7-7658-4a14-a860-f91a35a1b453/node_4",
    "name": "compute_system_energy",
    "status": "COMPLETED",
    "started_at": "2022-06-13T12:14:30",
    "ended_at": "2022-06-13T12:14:30",
    "runtime": 50
}
latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].electron[6].electronInput = {
    "data": "system=Atoms(symbols='Cu32N2', pbc=[True, True, False], cell=[[10.210621920333747, 0.0, 0.0], [5.105310960166873, 8.842657971447272, 0.0], [0.0, 0.0, 22.08423447177455]], tags=..., constraint=FixAtoms(indices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]), calculator=EMT(...))"
}
latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].electron[6].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].electron[6].electronFunctionString = {
    "data": '# @ct.electron(backend=executor2)\ndef compute_system_energy(system):\n    system.calc = EMT()\n    return system.get_potential_energy()\n\n\n',
}
latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].electron[6].electronError = null
latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].electron[6].electronResult = {
    "data": "11.509056283570393"
}
latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].electron[3].electronDetails = {
    "id": 3,
    "node_id": 3,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/df4601e7-7658-4a14-a860-f91a35a1b453/node_4",
    "name": "construct_cu_slab",
    "status": "COMPLETED",
    "started_at": "2022-06-13T12:14:30",
    "ended_at": "2022-06-13T12:14:30",
    "runtime": 50
}
latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].electron[3].electronResult = {
    "data": "Atoms(symbols='Cu32N2', pbc=[True, True, False], cell=[[10.210621920333747, 0.0, 0.0], [5.105310960166873, 8.842657971447272, 0.0], [0.0, 0.0, 22.08423447177455]], tags=..., constraint=FixAtoms(indices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]), calculator=EMT(...))"
}
latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].electron[3].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].electron[3].electronFunctionString = {
    "data": '# @ct.electron(backend=executor1)\ndef construct_cu_slab(\n    unit_cell=(4, 4, 2), vacuum=10.0,\n):\n    slab = fcc111("Cu", size=unit_cell, vacuum=vacuum)\n    return slab\n\n\n',
}
latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].electron[3].electronError = null
latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].electron[3].electronInput = {
    "data": "unit_cell=(4, 4, 2), vacuum=10.0"
}

latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].electron[2].electronDetails = {
    "id": 2,
    "node_id": 2,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/df4601e7-7658-4a14-a860-f91a35a1b453/node_4",
    "name": "compute_system_energy",
    "status": "COMPLETED",
    "started_at": "2022-06-13T12:14:30",
    "ended_at": "2022-06-13T12:14:30",
    "runtime": 50
}
latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].electron[2].electronResult = {
    "data": "0.44034357303561467"
}
latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].electron[2].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].electron[2].electronFunctionString = {
    "data": '# @ct.electron(backend=executor2)\ndef compute_system_energy(system):\n    system.calc = EMT()\n    return system.get_potential_energy()\n\n\n',
}
latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].electron[2].electronError = null
latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].electron[2].electronInput = {
    "data": "system=Atoms(symbols='N2', pbc=False, calculator=EMT(...))"
}
latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].electron[7].electronDetails = {
    "id": 7,
    "node_id": 7,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/df4601e7-7658-4a14-a860-f91a35a1b453/node_4",
    "name": "get_relaxed_slab",
    "status": "COMPLETED",
    "started_at": "2022-06-13T12:14:30",
    "ended_at": "2022-06-13T12:14:30",
    "runtime": 50
}
latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].electron[7].electronResult = {
    "data": "Atoms(symbols='Cu32N2', pbc=[True, True, False], cell=[[10.210621920333747, 0.0, 0.0], [5.105310960166873, 8.842657971447272, 0.0], [0.0, 0.0, 22.08423447177455]], tags=..., constraint=FixAtoms(indices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]), calculator=EMT(...))"
}
latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].electron[7].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].electron[7].electronFunctionString = {
    "data": '# @ct.electron\ndef get_relaxed_slab(slab, molecule, height=1.85):\n    slab.calc = EMT()\n    add_adsorbate(slab, molecule, height, "ontop")\n    constraint = FixAtoms(mask=[a.symbol != "N" for a in slab])\n    slab.set_constraint(constraint)\n    dyn = QuasiNewton(slab, trajectory="/tmp/N2Cu.traj", logfile="/tmp/temp")\n    dyn.run(fmax=0.01)\n    return slab\n\n\n',
}
latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].electron[7].electronError = null
latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].electron[7].electronInput = {
    "data": "slab=Atoms(symbols='Cu32N2', pbc=[True, True, False], cell=[[10.210621920333747, 0.0, 0.0], [5.105310960166873, 8.842657971447272, 0.0], [0.0, 0.0, 22.08423447177455]], tags=..., constraint=FixAtoms(indices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]), calculator=EMT(...)), molecule=Atoms(symbols='N2', pbc=False, calculator=EMT(...)), height=3"
}
latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].electron[9].electronDetails = {
    "id": 9,
    "node_id": 9,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/df4601e7-7658-4a14-a860-f91a35a1b453/node_4",
    "name": "compute_system_energy",
    "status": "COMPLETED",
    "started_at": "2022-06-13T12:14:30",
    "ended_at": "2022-06-13T12:14:30",
    "runtime": 50
}
latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].electron[9].electronInput = {
    "data": "system=Atoms(symbols='Cu32N2', pbc=[True, True, False], cell=[[10.210621920333747, 0.0, 0.0], [5.105310960166873, 8.842657971447272, 0.0], [0.0, 0.0, 22.08423447177455]], tags=..., constraint=FixAtoms(indices=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]), calculator=EMT(...))"
}
latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].electron[9].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].electron[9].electronFunctionString = {
    "data": '# @ct.electron(backend=executor2)\ndef compute_system_energy(system):\n    system.calc = EMT()\n    return system.get_potential_energy()\n\n\n',
}
latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].electron[9].electronError = null
latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].electron[9].electronResult = {
    "data": "11.625212574435581"
}
latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].electron[10].electronDetails = {
    "id": 10,
    "node_id": 10,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/df4601e7-7658-4a14-a860-f91a35a1b453/node_4",
    "name": "compute_system_energy_+_compute_system_energy",
    "status": "COMPLETED",
    "started_at": "2022-06-13T12:14:30",
    "ended_at": "2022-06-13T12:14:30",
    "runtime": 50
}
latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].electron[10].electronResult = {
    "data": "11.949399856606007"
}
latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].electron[10].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].electron[10].electronFunctionString = {
    "data": '# compute_system_energy_+_compute_system_energy was not inspectable\n\n',
}
latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].electron[10].electronError = null
latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].electron[10].electronInput = {
    "data": "arg_1=11.509056283570393, arg_2=0.44034357303561467"
}
latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].electron[11].electronDetails = {
    "id": 11,
    "node_id": 11,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/df4601e7-7658-4a14-a860-f91a35a1b453/node_4",
    "name": "compute_system_energy_+_compute_system_energy_-_compute_system_energy",
    "status": "COMPLETED",
    "started_at": "2022-06-13T12:14:30",
    "ended_at": "2022-06-13T12:14:30",
    "runtime": 50
}
latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].electron[11].electronResult = {
    "data": "0.3241872821704259"
}
latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].electron[11].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].electron[11].electronFunctionString = {
    "data": '# compute_system_energy_+_compute_system_energy_-_compute_system_energy was not inspectable',
}
latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].electron[11].electronError = null
latticeDetailsDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"].electron[11].electronInput = {
    "data": "arg_1=11.949399856606007, arg_2=11.625212574435581"
}



//   Dispatch ba3c238c-cb92-48e8-b7b2-debeebe2e81a
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"] = {}
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].latticeDetails =
{
    "dispatch_id": "ba3c238c-cb92-48e8-b7b2-debeebe2e81a",
    "lattice_name": "final_calc",
    "runtime": 1000,
    "total_electrons": 10,
    "total_electrons_completed": 6,
    "started_at": "2022-08-11T12:14:39",
    "ended_at": "2022-08-11T12:14:40",
    "status": "FAILED",
    "updated_at": "2022-08-11T12:14:40",
    "directory": "/home/covalent/Desktop/workflows/results/ba3c238c-cb92-48e8-b7b2-debeebe2e81a",
};
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].latticeError = "get_RA: substring not found";
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].latticeResult = {
    "data": "\"[19.30560599 19.22910799 19.1520599  ... 19.14461197 19.0669631218.98876836],[-35.96235506 -36.07771597 -36.1925922  ... -36.20362793 -36.31796856 -36.43181675],[209.39040932 209.61808842 209.84549899 ... 209.86738212 210.09449597 210.32133708],[312.26474717 312.52275968 312.78145573 ... 312.80640174 313.06584912 313.32598355]\""
};
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].latticeInput = null;
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].latticeFunctionString = {
    "data": '# @ct.lattice\ndef final_calc(\n    target_list=["sirius", "trappist-1"],\n    region="America/Los_Angeles",\n    latitude=49.2827,\n    longitude=-123.1207,\n):\n    RA = get_RA(target_list=target_list)\n    dec = get_dec(target_list=target_list)\n    T = convert_to_utc(time_zone=region)\n    d = days_since_J2000(region=region)\n    lst = local_sidereal_time(d=d, long=longitude, T=T)\n    ha = hour_angle(LST=lst, RA=RA)\n    alt = altitude_of_target(dec=dec, lat=latitude, ha=ha)\n    az = get_azimuth(dec=dec, lat=latitude, ha=ha, alt=alt)\n    return alt, az\n\n\n',
};
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].latticeExecutor = {
    "executor_name": "dask",
    "executor_details": "log_stdout: stdout.log\n    log_stderr: stderr.log\n   cache_dir: /tmp/covalent\n    current_env_on_conda_fail: False"
};
// electron data initilisation
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron = []
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[0] = {}
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[1] = {}
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[4] = {}
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[5] = {}
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[8] = {}
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[10] = {}
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[12] = {}
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[14] = {}
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[15] = {}
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[17] = {}

latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[0].electronDetails = {
    "id": 0,
    "node_id": 0,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/ba3c238c-cb92-48e8-b7b2-debeebe2e81a/node_4",
    "name": "get_RA",
    "status": "FAILED",
    "started_at": "2022-08-10T12:14:39",
    "ended_at": "2022-08-11T12:14:40",
    "runtime": 50
}
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[0].electronResult = null
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[0].electronExecutor = {
    "executor_name": "dask",
    "executor_details": null
}
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[0].electronFunctionString = {
    "data": '# @ct.electron\ndef get_RA(target_list):\n    RA = []\n    for target_name in target_list:\n        response = requests.get(\n            "http://simbad.u-strasbg.fr/simbad/sim-id?output.format=votable&Ident=%s&output.params=ra,dec"\n            % target_name\n        )\n        star_info = response.text\n        RA.append(\n            star_info[star_info.index("<TR><TD>") + 8 : star_info.index("</TD><TD>")]\n        )\n    RA_degs = []\n    for source in RA:\n        hour = float(source.split(" ")[0])\n        minute = float(source.split(" ")[1])\n        second = float(source.split(" ")[2])\n        RA_degs.append(((hour + minute / 60 + second / 3600) * 15))\n    return RA_degs\n\n\n'
}
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[0].electronError = {
    "data": "substring not found"
}
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[0].electronInput = {
    "data": "{'args': (), 'kwargs': {'target_list': \"['sirius', 'trappist-1']\"}}",
    "python_object": "import pickle\npickle.loads(b\"\\x80\\x05\\x95B\\x00\\x00\\x00\\x00\\x00\\x00\\x00}\\x94(\\x8c\\x04args\\x94)\\x8c\\x06kwargs\\x94}\\x94\\x8c\\x0btarget_list\\x94\\x8c\\x18['sirius', 'trappist-1']\\x94su.\")"
}

latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[1].electronDetails = {
    "id": 1,
    "node_id": 1,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/ba3c238c-cb92-48e8-b7b2-debeebe2e81a/node_4",
    "name": ":electron_list:",
    "status": "COMPLETED",
    "started_at": "2022-08-10T12:14:39",
    "ended_at": "2022-08-11T12:14:40",
    "runtime": 50
}
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[1].electronResult = {
    "data": "\"['sirius', 'trappist-1']\"",
    "python_object": "import pickle\npickle.loads(b'\\x80\\x05\\x95\\x1b\\x00\\x00\\x00\\x00\\x00\\x00\\x00]\\x94(\\x8c\\x06sirius\\x94\\x8c\\ntrappist-1\\x94e.')"
}
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[1].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[1].electronFunctionString = {
    "data": '# to_electron_collection was not inspectable\n\n',
}
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[1].electronError = null
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[1].electronInput = {
    "data": "{'args': (), 'kwargs': {'x': '[<covalent.TransportableObject object at 0x7fbbdb2a4850>, <covalent.TransportableObject object at 0x7fbbdb24af70>]'}}",
    "python_object": "import pickle\npickle.loads(b'\\x80\\x05\\x95\\x92\\x00\\x00\\x00\\x00\\x00\\x00\\x00}\\x94(\\x8c\\x04args\\x94)\\x8c\\x06kwargs\\x94}\\x94\\x8c\\x01x\\x94\\x8cr[<covalent.TransportableObject object at 0x7fbbdb2a4850>, <covalent.TransportableObject object at 0x7fbbdb24af70>]\\x94su.')"
}
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[4].electronDetails = {
    "id": 4,
    "node_id": 4,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/ba3c238c-cb92-48e8-b7b2-debeebe2e81a/node_4",
    "name": "get_dec",
    "status": "COMPLETED",
    "started_at": "2022-08-10T12:14:39",
    "ended_at": "2022-08-11T12:14:40",
    "runtime": 50
}
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[4].electronResult = {
    "data": "\"[-16.71611586111111, -5.041399250518333]\"",
    "python_object": "import pickle\npickle.loads(b'\\x80\\x05\\x95\\x17\\x00\\x00\\x00\\x00\\x00\\x00\\x00]\\x94(G\\xc00\\xb7S^{\\x9e}G\\xc0\\x14*d\\x90\\xac8ze.')"
}
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[4].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[4].electronFunctionString = {
    "data": '# @ct.electron\ndef get_dec(target_list):\n    dec = []\n    for target_name in target_list:\n        response = requests.get(\n            "http://simbad.u-strasbg.fr/simbad/sim-id?output.format=votable&Ident=%s&output.params=ra,dec"\n            % target_name\n        )\n        star_info = response.text\n        dec.append(\n            star_info[star_info.index("</TD><TD>") + 9 : star_info.index("</TD></TR>")]\n        )\n    dec_degs = []\n    for source in dec:\n        degree = float(source.split(" ")[0])\n        arcmin = float(source.split(" ")[1])\n        arcsec = float(source.split(" ")[2])\n        if degree < 0:\n            dec_degs.append(degree - arcmin / 60 - arcsec / 3600)\n        else:\n            dec_degs.append(degree + arcmin / 60 + arcsec / 3600)\n    return dec_degs\n\n\n',
}
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[4].electronError = null
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[4].electronInput = {
    "data": "{'args': (), 'kwargs': {'target_list': \"['sirius', 'trappist-1']\"}}",
    "python_object": "import pickle\npickle.loads(b\"\\x80\\x05\\x95B\\x00\\x00\\x00\\x00\\x00\\x00\\x00}\\x94(\\x8c\\x04args\\x94)\\x8c\\x06kwargs\\x94}\\x94\\x8c\\x0btarget_list\\x94\\x8c\\x18['sirius', 'trappist-1']\\x94su.\")"
}
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[5].electronDetails = {
    "id": 5,
    "node_id": 5,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/ba3c238c-cb92-48e8-b7b2-debeebe2e81a/node_4",
    "name": ":electron_list:",
    "status": "COMPLETED",
    "started_at": "2022-08-10T12:14:39",
    "ended_at": "2022-08-11T12:14:40",
    "runtime": 50
}
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[5].electronResult = {
    "data": "\"['sirius', 'trappist-1']\"",
    "python_object": "import pickle\npickle.loads(b'\\x80\\x05\\x95\\x1b\\x00\\x00\\x00\\x00\\x00\\x00\\x00]\\x94(\\x8c\\x06sirius\\x94\\x8c\\ntrappist-1\\x94e.')"
}
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[5].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[5].electronFunctionString = {
    "data": '# to_electron_collection was not inspectable\n\n',
}
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[5].electronError = null
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[5].electronInput = {
    "data": "{'args': (), 'kwargs': {'x': '[<covalent.TransportableObject object at 0x7fbbdb2a4850>, <covalent.TransportableObject object at 0x7fbbdb24af70>]'}}",
    "python_object": "import pickle\npickle.loads(b'\\x80\\x05\\x95\\x92\\x00\\x00\\x00\\x00\\x00\\x00\\x00}\\x94(\\x8c\\x04args\\x94)\\x8c\\x06kwargs\\x94}\\x94\\x8c\\x01x\\x94\\x8cr[<covalent.TransportableObject object at 0x7fbbdb2a4850>, <covalent.TransportableObject object at 0x7fbbdb24af70>]\\x94su.')"
}
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[8].electronDetails = {
    "id": 8,
    "node_id": 8,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/ba3c238c-cb92-48e8-b7b2-debeebe2e81a/node_4",
    "name": "convert_to_utc",
    "status": "COMPLETED",
    "started_at": "2022-08-10T12:14:39",
    "ended_at": "2022-08-11T12:14:40",
    "runtime": 50
}
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[8].electronResult = {
    "data": "\"[ 7.     7.016  7.032 ... 30.968 30.984 31.   ]\"",
    "python_object": "import pickle\npickle.loads(b'\\x80\\x05\\x95^/\\x00\\x00\\x00\\x00\\x00\\x00\\x8c\\x12numpy.core.numeric\\x94\\x8c\\x0b_frombuffer\\x94\\x93\\x94(\\x96\\xe8.\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x1c@\\xaa\\xf1\\xd2Mb\\x10\\x1c@T\\xe3\\xa5\\x9b\\xc4 \\x1c@\\xfe\\xd4x\\xe9&1\\x1c@\\xa8\\xc6K7\\x89A\\x1c@R\\xb8\\x1e\\x85\\xebQ\\x1c@\\xfc\\xa9\\xf1\\xd2Mb\\x1c@\\xa6\\x9b\\xc4 \\xb0r\\x1c@P\\x8d\\x97n\\x12\\x83\\x1c@\\xfa~j\\xbct\\x93\\x1c@\\xa4p=\\n\\xd7\\xa3\\x1c@Nb\\x10X9\\xb4\\x1c@\\xf8S\\xe3\\xa5\\x9b\\xc4\\x1c@\\xa2E\\xb6\\xf3\\xfd\\xd4\\x1c@L7\\x89A`\\xe5\\x1c@\\xf6(\\\\\\x8f\\xc2\\xf5\\x1c@\\xa0\\x1a/\\xdd$\\x06\\x1d@J\\x0c\\x02+\\x87\\x16\\x1d@\\xf4\\xfd\\xd4x\\xe9&\\x1d@\\x9e\\xef\\xa7\\xc6K7\\x1d@H\\xe1z\\x14\\xaeG\\x1d@\\xf2\\xd2Mb\\x10X\\x1d@\\x9c\\xc4 \\xb0rh\\x1d@F\\xb6\\xf3\\xfd\\xd4x\\x1d@\\xf0\\xa7\\xc6K7\\x89\\x1d@\\x9a\\x99\\x99\\x99\\x99\\x99\\x1d@D\\x8bl\\xe7\\xfb\\xa9\\x1d@\\xee|?5^\\xba\\x1d@\\x98n\\x12\\x83\\xc0\\xca\\x1d@B`\\xe5\\xd0\"\\xdb\\x1d@\\xecQ\\xb8\\x1e\\x85\\xeb\\x1d@\\x96C\\x8bl\\xe7\\xfb\\x1d@@5^\\xbaI\\x0c\\x1e@\\xea&1\\x08\\xac\\x1c\\x1e@\\x94\\x18\\x04V\\x0e-\\x1e@>\\n\\xd7\\xa3p=\\x1e@\\xe8\\xfb\\xa9\\xf1\\xd2M\\x1e@\\x92\\xed|?5^\\x1e@<\\xdfO\\x8d\\x97n\\x1e@\\xe6\\xd0\"\\xdb\\xf9~\\x1e@\\x90\\xc2\\xf5(\\\\\\x8f\\x1e@:\\xb4\\xc8v\\xbe\\x9f\\x1e@\\xe4\\xa5\\x9b\\xc4 \\xb0\\x1e@\\x8e\\x97n\\x12\\x83\\xc0\\x1e@8\\x89A`\\xe5\\xd0\\x1e@\\xe2z\\x14\\xaeG\\xe1\\x1e@\\x8cl\\xe7\\xfb\\xa9\\xf1\\x1e@6^\\xbaI\\x0c\\x02\\x1f@\\xe0O\\x8d\\x97n\\x12\\x1f@\\x8aA`\\xe5\\xd0\"\\x1f@433333\\x1f@\\xde$\\x06\\x81\\x95C\\x1f@\\x88\\x16\\xd9\\xce\\xf7S\\x1f@2\\x08\\xac\\x1cZd\\x1f@\\xdc\\xf9~j\\xbct\\x1f@\\x86\\xebQ\\xb8\\x1e\\x85\\x1f@0\\xdd$\\x06\\x81\\x95\\x1f@\\xda\\xce\\xf7S\\xe3\\xa5\\x1f@\\x84\\xc0\\xca\\xa1E\\xb6\\x1f@.\\xb2\\x9d\\xef\\xa7\\xc6\\x1f@\\xd8\\xa3p=\\n\\xd7\\x1f@\\x82\\x95C\\x8bl\\xe7\\x1f@,\\x87\\x16\\xd9\\xce\\xf7\\x1f@k\\xbct\\x93\\x18\\x04 @@5^\\xbaI\\x0c @\\x15\\xaeG\\xe1z\\x14 @\\xea&1\\x08\\xac\\x1c @\\xbf\\x9f\\x1a/\\xdd$ @\\x94\\x18\\x04V\\x0e- @i\\x91\\xed|?5 @>\\n\\xd7\\xa3p= @\\x13\\x83\\xc0\\xca\\xa1E @\\xe8\\xfb\\xa9\\xf1\\xd2M @\\xbdt\\x93\\x18\\x04V @\\x92\\xed|?5^ @gfffff @<\\xdfO\\x8d\\x97n @\\x11X9\\xb4\\xc8v @\\xe6\\xd0\"\\xdb\\xf9~ @\\xbbI\\x0c\\x02+\\x87 @\\x90\\xc2\\xf5(\\\\\\x8f @e;\\xdfO\\x8d\\x97 @:\\xb4\\xc8v\\xbe\\x9f @\\x0f-\\xb2\\x9d\\xef\\xa7 @\\xe4\\xa5\\x9b\\xc4 \\xb0 @\\xb9\\x1e\\x85\\xebQ\\xb8 @\\x8e\\x97n\\x12\\x83\\xc0 @c\\x10X9\\xb4\\xc8 @8\\x89A`\\xe5\\xd0 @\\r\\x02+\\x87\\x16\\xd9 @\\xe2z\\x14\\xaeG\\xe1 @\\xb7\\xf3\\xfd\\xd4x\\xe9 @\\x8cl\\xe7\\xfb\\xa9\\xf1 @a\\xe5\\xd0\"\\xdb\\xf9 @6^\\xbaI\\x0c\\x02!@\\x0b\\xd7\\xa3p=\\n!@\\xe0O\\x8d\\x97n\\x12!@\\xb5\\xc8v\\xbe\\x9f\\x1a!@\\x8aA`\\xe5\\xd0\"!@_\\xbaI\\x0c\\x02+!@433333!@\\t\\xac\\x1cZd;!@\\xde$\\x06\\x81\\x95C!@\\xb3\\x9d\\xef\\xa7\\xc6K!@\\x88\\x16\\xd9\\xce\\xf7S!@]\\x8f\\xc2\\xf5(\\\\!@2\\x08\\xac\\x1cZd!@\\x07\\x81\\x95C\\x8bl!@\\xdc\\xf9~j\\xbct!@\\xb1rh\\x91\\xed|!@\\x86\\xebQ\\xb8\\x1e\\x85!@[d;\\xdfO\\x8d!@0\\xdd$\\x06\\x81\\x95!@\\x05V\\x0e-\\xb2\\x9d!@\\xda\\xce\\xf7S\\xe3\\xa5!@\\xafG\\xe1z\\x14\\xae!@\\x84\\xc0\\xca\\xa1E\\xb6!@Y9\\xb4\\xc8v\\xbe!@.\\xb2\\x9d\\xef\\xa7\\xc6!@\\x03+\\x87\\x16\\xd9\\xce!@\\xd8\\xa3p=\\n\\xd7!@\\xad\\x1cZd;\\xdf!@\\x82\\x95C\\x8bl\\xe7!@W\\x0e-\\xb2\\x9d\\xef!@,\\x87\\x16\\xd9\\xce\\xf7!@\\x01\\x00\\x00\\x00\\x00\\x00\"@\\xd6x\\xe9&1\\x08\"@\\xab\\xf1\\xd2Mb\\x10\"@\\x80j\\xbct\\x93\\x18\"@U\\xe3\\xa5\\x9b\\xc4 \"@*\\\\\\x8f\\xc2\\xf5(\"@\\xff\\xd4x\\xe9&1\"@\\xd4Mb\\x10X9\"@\\xa9\\xc6K7\\x89A\"@~?5^\\xbaI\"@S\\xb8\\x1e\\x85\\xebQ\"@(1\\x08\\xac\\x1cZ\"@\\xfd\\xa9\\xf1\\xd2Mb\"@\\xd2\"\\xdb\\xf9~j\"@\\xa7\\x9b\\xc4 \\xb0r\"@|\\x14\\xaeG\\xe1z\"@Q\\x8d\\x97n\\x12\\x83\"@&\\x06\\x81\\x95C\\x8b\"@\\xfb~j\\xbct\\x93\"@\\xd0\\xf7S\\xe3\\xa5\\x9b\"@\\xa5p=\\n\\xd7\\xa3\"@z\\xe9&1\\x08\\xac\"@Ob\\x10X9\\xb4\"@$\\xdb\\xf9~j\\xbc\"@\\xf9S\\xe3\\xa5\\x9b\\xc4\"@\\xce\\xcc\\xcc\\xcc\\xcc\\xcc\"@\\xa3E\\xb6\\xf3\\xfd\\xd4\"@x\\xbe\\x9f\\x1a/\\xdd\"@M7\\x89A`\\xe5\"@\"\\xb0rh\\x91\\xed\"@\\xf7(\\\\\\x8f\\xc2\\xf5\"@\\xcc\\xa1E\\xb6\\xf3\\xfd\"@\\xa1\\x1a/\\xdd$\\x06#@v\\x93\\x18\\x04V\\x0e#@K\\x0c\\x02+\\x87\\x16#@ \\x85\\xebQ\\xb8\\x1e#@\\xf5\\xfd\\xd4x\\xe9&#@\\xcav\\xbe\\x9f\\x1a/#@\\x9f\\xef\\xa7\\xc6K7#@th\\x91\\xed|?#@I\\xe1z\\x14\\xaeG#@\\x1eZd;\\xdfO#@\\xf3\\xd2Mb\\x10X#@\\xc8K7\\x89A`#@\\x9d\\xc4 \\xb0rh#@r=\\n\\xd7\\xa3p#@G\\xb6\\xf3\\xfd\\xd4x#@\\x1c/\\xdd$\\x06\\x81#@\\xf1\\xa7\\xc6K7\\x89#@\\xc6 \\xb0rh\\x91#@\\x9b\\x99\\x99\\x99\\x99\\x99#@p\\x12\\x83\\xc0\\xca\\xa1#@E\\x8bl\\xe7\\xfb\\xa9#@\\x1a\\x04V\\x0e-\\xb2#@\\xef|?5^\\xba#@\\xc4\\xf5(\\\\\\x8f\\xc2#@\\x99n\\x12\\x83\\xc0\\xca#@n\\xe7\\xfb\\xa9\\xf1\\xd2#@C`\\xe5\\xd0\"\\xdb#@\\x18\\xd9\\xce\\xf7S\\xe3#@\\xedQ\\xb8\\x1e\\x85\\xeb#@\\xc2\\xca\\xa1E\\xb6\\xf3#@\\x97C\\x8bl\\xe7\\xfb#@l\\xbct\\x93\\x18\\x04$@A5^\\xbaI\\x0c$@\\x16\\xaeG\\xe1z\\x14$@\\xeb&1\\x08\\xac\\x1c$@\\xc0\\x9f\\x1a/\\xdd$$@\\x95\\x18\\x04V\\x0e-$@j\\x91\\xed|?5$@?\\n\\xd7\\xa3p=$@\\x14\\x83\\xc0\\xca\\xa1E$@\\xe9\\xfb\\xa9\\xf1\\xd2M$@\\xbet\\x93\\x18\\x04V$@\\x93\\xed|?5^$@hfffff$@=\\xdfO\\x8d\\x97n$@\\x12X9\\xb4\\xc8v$@\\xe7\\xd0\"\\xdb\\xf9~$@\\xbcI\\x0c\\x02+\\x87$@\\x91\\xc2\\xf5(\\\\\\x8f$@f;\\xdfO\\x8d\\x97$@;\\xb4\\xc8v\\xbe\\x9f$@\\x10-\\xb2\\x9d\\xef\\xa7$@\\xe5\\xa5\\x9b\\xc4 \\xb0$@\\xba\\x1e\\x85\\xebQ\\xb8$@\\x8f\\x97n\\x12\\x83\\xc0$@d\\x10X9\\xb4\\xc8$@9\\x89A`\\xe5\\xd0$@\\x0e\\x02+\\x87\\x16\\xd9$@\\xe3z\\x14\\xaeG\\xe1$@\\xb8\\xf3\\xfd\\xd4x\\xe9$@\\x8dl\\xe7\\xfb\\xa9\\xf1$@b\\xe5\\xd0\"\\xdb\\xf9$@7^\\xbaI\\x0c\\x02%@\\x0c\\xd7\\xa3p=\\n%@\\xe1O\\x8d\\x97n\\x12%@\\xb6\\xc8v\\xbe\\x9f\\x1a%@\\x8bA`\\xe5\\xd0\"%@`\\xbaI\\x0c\\x02+%@533333%@\\n\\xac\\x1cZd;%@\\xdf$\\x06\\x81\\x95C%@\\xb4\\x9d\\xef\\xa7\\xc6K%@\\x89\\x16\\xd9\\xce\\xf7S%@^\\x8f\\xc2\\xf5(\\\\%@3\\x08\\xac\\x1cZd%@\\x08\\x81\\x95C\\x8bl%@\\xdd\\xf9~j\\xbct%@\\xb2rh\\x91\\xed|%@\\x87\\xebQ\\xb8\\x1e\\x85%@\\\\d;\\xdfO\\x8d%@1\\xdd$\\x06\\x81\\x95%@\\x06V\\x0e-\\xb2\\x9d%@\\xdb\\xce\\xf7S\\xe3\\xa5%@\\xb0G\\xe1z\\x14\\xae%@\\x85\\xc0\\xca\\xa1E\\xb6%@Z9\\xb4\\xc8v\\xbe%@/\\xb2\\x9d\\xef\\xa7\\xc6%@\\x04+\\x87\\x16\\xd9\\xce%@\\xd9\\xa3p=\\n\\xd7%@\\xae\\x1cZd;\\xdf%@\\x83\\x95C\\x8bl\\xe7%@X\\x0e-\\xb2\\x9d\\xef%@-\\x87\\x16\\xd9\\xce\\xf7%@\\x02\\x00\\x00\\x00\\x00\\x00&@\\xd7x\\xe9&1\\x08&@\\xac\\xf1\\xd2Mb\\x10&@\\x81j\\xbct\\x93\\x18&@V\\xe3\\xa5\\x9b\\xc4 &@+\\\\\\x8f\\xc2\\xf5(&@\\x00\\xd5x\\xe9&1&@\\xd5Mb\\x10X9&@\\xaa\\xc6K7\\x89A&@\\x7f?5^\\xbaI&@T\\xb8\\x1e\\x85\\xebQ&@)1\\x08\\xac\\x1cZ&@\\xfe\\xa9\\xf1\\xd2Mb&@\\xd3\"\\xdb\\xf9~j&@\\xa8\\x9b\\xc4 \\xb0r&@}\\x14\\xaeG\\xe1z&@R\\x8d\\x97n\\x12\\x83&@\\'\\x06\\x81\\x95C\\x8b&@\\xfc~j\\xbct\\x93&@\\xd1\\xf7S\\xe3\\xa5\\x9b&@\\xa6p=\\n\\xd7\\xa3&@{\\xe9&1\\x08\\xac&@Pb\\x10X9\\xb4&@%\\xdb\\xf9~j\\xbc&@\\xfaS\\xe3\\xa5\\x9b\\xc4&@\\xcf\\xcc\\xcc\\xcc\\xcc\\xcc&@\\xa4E\\xb6\\xf3\\xfd\\xd4&@y\\xbe\\x9f\\x1a/\\xdd&@N7\\x89A`\\xe5&@#\\xb0rh\\x91\\xed&@\\xf8(\\\\\\x8f\\xc2\\xf5&@\\xcd\\xa1E\\xb6\\xf3\\xfd&@\\xa2\\x1a/\\xdd$\\x06\\'@w\\x93\\x18\\x04V\\x0e\\'@L\\x0c\\x02+\\x87\\x16\\'@!\\x85\\xebQ\\xb8\\x1e\\'@\\xf6\\xfd\\xd4x\\xe9&\\'@\\xcbv\\xbe\\x9f\\x1a/\\'@\\xa0\\xef\\xa7\\xc6K7\\'@uh\\x91\\xed|?\\'@J\\xe1z\\x14\\xaeG\\'@\\x1fZd;\\xdfO\\'@\\xf4\\xd2Mb\\x10X\\'@\\xc9K7\\x89A`\\'@\\x9e\\xc4 \\xb0rh\\'@s=\\n\\xd7\\xa3p\\'@H\\xb6\\xf3\\xfd\\xd4x\\'@\\x1d/\\xdd$\\x06\\x81\\'@\\xf2\\xa7\\xc6K7\\x89\\'@\\xc7 \\xb0rh\\x91\\'@\\x9c\\x99\\x99\\x99\\x99\\x99\\'@q\\x12\\x83\\xc0\\xca\\xa1\\'@F\\x8bl\\xe7\\xfb\\xa9\\'@\\x1b\\x04V\\x0e-\\xb2\\'@\\xf0|?5^\\xba\\'@\\xc5\\xf5(\\\\\\x8f\\xc2\\'@\\x9an\\x12\\x83\\xc0\\xca\\'@o\\xe7\\xfb\\xa9\\xf1\\xd2\\'@D`\\xe5\\xd0\"\\xdb\\'@\\x19\\xd9\\xce\\xf7S\\xe3\\'@\\xeeQ\\xb8\\x1e\\x85\\xeb\\'@\\xc3\\xca\\xa1E\\xb6\\xf3\\'@\\x98C\\x8bl\\xe7\\xfb\\'@m\\xbct\\x93\\x18\\x04(@B5^\\xbaI\\x0c(@\\x17\\xaeG\\xe1z\\x14(@\\xec&1\\x08\\xac\\x1c(@\\xc1\\x9f\\x1a/\\xdd$(@\\x96\\x18\\x04V\\x0e-(@k\\x91\\xed|?5(@@\\n\\xd7\\xa3p=(@\\x15\\x83\\xc0\\xca\\xa1E(@\\xea\\xfb\\xa9\\xf1\\xd2M(@\\xbft\\x93\\x18\\x04V(@\\x94\\xed|?5^(@ifffff(@>\\xdfO\\x8d\\x97n(@\\x13X9\\xb4\\xc8v(@\\xe8\\xd0\"\\xdb\\xf9~(@\\xbdI\\x0c\\x02+\\x87(@\\x92\\xc2\\xf5(\\\\\\x8f(@g;\\xdfO\\x8d\\x97(@<\\xb4\\xc8v\\xbe\\x9f(@\\x11-\\xb2\\x9d\\xef\\xa7(@\\xe6\\xa5\\x9b\\xc4 \\xb0(@\\xbb\\x1e\\x85\\xebQ\\xb8(@\\x90\\x97n\\x12\\x83\\xc0(@e\\x10X9\\xb4\\xc8(@:\\x89A`\\xe5\\xd0(@\\x0f\\x02+\\x87\\x16\\xd9(@\\xe4z\\x14\\xaeG\\xe1(@\\xb9\\xf3\\xfd\\xd4x\\xe9(@\\x8el\\xe7\\xfb\\xa9\\xf1(@c\\xe5\\xd0\"\\xdb\\xf9(@8^\\xbaI\\x0c\\x02)@\\r\\xd7\\xa3p=\\n)@\\xe2O\\x8d\\x97n\\x12)@\\xb7\\xc8v\\xbe\\x9f\\x1a)@\\x8cA`\\xe5\\xd0\")@a\\xbaI\\x0c\\x02+)@633333)@\\x0b\\xac\\x1cZd;)@\\xe0$\\x06\\x81\\x95C)@\\xb5\\x9d\\xef\\xa7\\xc6K)@\\x8a\\x16\\xd9\\xce\\xf7S)@_\\x8f\\xc2\\xf5(\\\\)@4\\x08\\xac\\x1cZd)@\\t\\x81\\x95C\\x8bl)@\\xde\\xf9~j\\xbct)@\\xb3rh\\x91\\xed|)@\\x88\\xebQ\\xb8\\x1e\\x85)@]d;\\xdfO\\x8d)@2\\xdd$\\x06\\x81\\x95)@\\x07V\\x0e-\\xb2\\x9d)@\\xdc\\xce\\xf7S\\xe3\\xa5)@\\xb1G\\xe1z\\x14\\xae)@\\x86\\xc0\\xca\\xa1E\\xb6)@[9\\xb4\\xc8v\\xbe)@0\\xb2\\x9d\\xef\\xa7\\xc6)@\\x05+\\x87\\x16\\xd9\\xce)@\\xda\\xa3p=\\n\\xd7)@\\xaf\\x1cZd;\\xdf)@\\x84\\x95C\\x8bl\\xe7)@Y\\x0e-\\xb2\\x9d\\xef)@.\\x87\\x16\\xd9\\xce\\xf7)@\\x03\\x00\\x00\\x00\\x00\\x00*@\\xd8x\\xe9&1\\x08*@\\xad\\xf1\\xd2Mb\\x10*@\\x82j\\xbct\\x93\\x18*@W\\xe3\\xa5\\x9b\\xc4 *@,\\\\\\x8f\\xc2\\xf5(*@\\x01\\xd5x\\xe9&1*@\\xd6Mb\\x10X9*@\\xab\\xc6K7\\x89A*@\\x80?5^\\xbaI*@U\\xb8\\x1e\\x85\\xebQ*@*1\\x08\\xac\\x1cZ*@\\xff\\xa9\\xf1\\xd2Mb*@\\xd4\"\\xdb\\xf9~j*@\\xa9\\x9b\\xc4 \\xb0r*@~\\x14\\xaeG\\xe1z*@S\\x8d\\x97n\\x12\\x83*@(\\x06\\x81\\x95C\\x8b*@\\xfd~j\\xbct\\x93*@\\xd2\\xf7S\\xe3\\xa5\\x9b*@\\xa7p=\\n\\xd7\\xa3*@|\\xe9&1\\x08\\xac*@Qb\\x10X9\\xb4*@&\\xdb\\xf9~j\\xbc*@\\xfbS\\xe3\\xa5\\x9b\\xc4*@\\xd0\\xcc\\xcc\\xcc\\xcc\\xcc*@\\xa5E\\xb6\\xf3\\xfd\\xd4*@z\\xbe\\x9f\\x1a/\\xdd*@O7\\x89A`\\xe5*@$\\xb0rh\\x91\\xed*@\\xf9(\\\\\\x8f\\xc2\\xf5*@\\xce\\xa1E\\xb6\\xf3\\xfd*@\\xa3\\x1a/\\xdd$\\x06+@x\\x93\\x18\\x04V\\x0e+@M\\x0c\\x02+\\x87\\x16+@\"\\x85\\xebQ\\xb8\\x1e+@\\xf7\\xfd\\xd4x\\xe9&+@\\xccv\\xbe\\x9f\\x1a/+@\\xa1\\xef\\xa7\\xc6K7+@vh\\x91\\xed|?+@K\\xe1z\\x14\\xaeG+@ Zd;\\xdfO+@\\xf5\\xd2Mb\\x10X+@\\xcaK7\\x89A`+@\\x9f\\xc4 \\xb0rh+@t=\\n\\xd7\\xa3p+@I\\xb6\\xf3\\xfd\\xd4x+@\\x1e/\\xdd$\\x06\\x81+@\\xf3\\xa7\\xc6K7\\x89+@\\xc8 \\xb0rh\\x91+@\\x9d\\x99\\x99\\x99\\x99\\x99+@r\\x12\\x83\\xc0\\xca\\xa1+@G\\x8bl\\xe7\\xfb\\xa9+@\\x1c\\x04V\\x0e-\\xb2+@\\xf1|?5^\\xba+@\\xc6\\xf5(\\\\\\x8f\\xc2+@\\x9bn\\x12\\x83\\xc0\\xca+@p\\xe7\\xfb\\xa9\\xf1\\xd2+@E`\\xe5\\xd0\"\\xdb+@\\x1a\\xd9\\xce\\xf7S\\xe3+@\\xefQ\\xb8\\x1e\\x85\\xeb+@\\xc4\\xca\\xa1E\\xb6\\xf3+@\\x99C\\x8bl\\xe7\\xfb+@n\\xbct\\x93\\x18\\x04,@C5^\\xbaI\\x0c,@\\x18\\xaeG\\xe1z\\x14,@\\xed&1\\x08\\xac\\x1c,@\\xc2\\x9f\\x1a/\\xdd$,@\\x97\\x18\\x04V\\x0e-,@l\\x91\\xed|?5,@A\\n\\xd7\\xa3p=,@\\x16\\x83\\xc0\\xca\\xa1E,@\\xeb\\xfb\\xa9\\xf1\\xd2M,@\\xc0t\\x93\\x18\\x04V,@\\x95\\xed|?5^,@jfffff,@?\\xdfO\\x8d\\x97n,@\\x14X9\\xb4\\xc8v,@\\xe9\\xd0\"\\xdb\\xf9~,@\\xbeI\\x0c\\x02+\\x87,@\\x93\\xc2\\xf5(\\\\\\x8f,@h;\\xdfO\\x8d\\x97,@=\\xb4\\xc8v\\xbe\\x9f,@\\x12-\\xb2\\x9d\\xef\\xa7,@\\xe7\\xa5\\x9b\\xc4 \\xb0,@\\xbc\\x1e\\x85\\xebQ\\xb8,@\\x91\\x97n\\x12\\x83\\xc0,@f\\x10X9\\xb4\\xc8,@;\\x89A`\\xe5\\xd0,@\\x10\\x02+\\x87\\x16\\xd9,@\\xe5z\\x14\\xaeG\\xe1,@\\xba\\xf3\\xfd\\xd4x\\xe9,@\\x8fl\\xe7\\xfb\\xa9\\xf1,@d\\xe5\\xd0\"\\xdb\\xf9,@9^\\xbaI\\x0c\\x02-@\\x0e\\xd7\\xa3p=\\n-@\\xe3O\\x8d\\x97n\\x12-@\\xb8\\xc8v\\xbe\\x9f\\x1a-@\\x8dA`\\xe5\\xd0\"-@b\\xbaI\\x0c\\x02+-@733333-@\\x0c\\xac\\x1cZd;-@\\xe1$\\x06\\x81\\x95C-@\\xb6\\x9d\\xef\\xa7\\xc6K-@\\x8b\\x16\\xd9\\xce\\xf7S-@`\\x8f\\xc2\\xf5(\\\\-@5\\x08\\xac\\x1cZd-@\\n\\x81\\x95C\\x8bl-@\\xdf\\xf9~j\\xbct-@\\xb4rh\\x91\\xed|-@\\x89\\xebQ\\xb8\\x1e\\x85-@^d;\\xdfO\\x8d-@3\\xdd$\\x06\\x81\\x95-@\\x08V\\x0e-\\xb2\\x9d-@\\xdd\\xce\\xf7S\\xe3\\xa5-@\\xb2G\\xe1z\\x14\\xae-@\\x87\\xc0\\xca\\xa1E\\xb6-@\\\\9\\xb4\\xc8v\\xbe-@1\\xb2\\x9d\\xef\\xa7\\xc6-@\\x06+\\x87\\x16\\xd9\\xce-@\\xdb\\xa3p=\\n\\xd7-@\\xb0\\x1cZd;\\xdf-@\\x85\\x95C\\x8bl\\xe7-@Z\\x0e-\\xb2\\x9d\\xef-@/\\x87\\x16\\xd9\\xce\\xf7-@\\x04\\x00\\x00\\x00\\x00\\x00.@\\xd9x\\xe9&1\\x08.@\\xae\\xf1\\xd2Mb\\x10.@\\x83j\\xbct\\x93\\x18.@X\\xe3\\xa5\\x9b\\xc4 .@-\\\\\\x8f\\xc2\\xf5(.@\\x02\\xd5x\\xe9&1.@\\xd7Mb\\x10X9.@\\xac\\xc6K7\\x89A.@\\x81?5^\\xbaI.@V\\xb8\\x1e\\x85\\xebQ.@+1\\x08\\xac\\x1cZ.@\\x00\\xaa\\xf1\\xd2Mb.@\\xd5\"\\xdb\\xf9~j.@\\xaa\\x9b\\xc4 \\xb0r.@\\x7f\\x14\\xaeG\\xe1z.@T\\x8d\\x97n\\x12\\x83.@)\\x06\\x81\\x95C\\x8b.@\\xfe~j\\xbct\\x93.@\\xd3\\xf7S\\xe3\\xa5\\x9b.@\\xa8p=\\n\\xd7\\xa3.@}\\xe9&1\\x08\\xac.@Rb\\x10X9\\xb4.@\\'\\xdb\\xf9~j\\xbc.@\\xfcS\\xe3\\xa5\\x9b\\xc4.@\\xd1\\xcc\\xcc\\xcc\\xcc\\xcc.@\\xa6E\\xb6\\xf3\\xfd\\xd4.@{\\xbe\\x9f\\x1a/\\xdd.@P7\\x89A`\\xe5.@%\\xb0rh\\x91\\xed.@\\xfa(\\\\\\x8f\\xc2\\xf5.@\\xcf\\xa1E\\xb6\\xf3\\xfd.@\\xa4\\x1a/\\xdd$\\x06/@y\\x93\\x18\\x04V\\x0e/@N\\x0c\\x02+\\x87\\x16/@#\\x85\\xebQ\\xb8\\x1e/@\\xf8\\xfd\\xd4x\\xe9&/@\\xcdv\\xbe\\x9f\\x1a//@\\xa2\\xef\\xa7\\xc6K7/@wh\\x91\\xed|?/@L\\xe1z\\x14\\xaeG/@!Zd;\\xdfO/@\\xf6\\xd2Mb\\x10X/@\\xcbK7\\x89A`/@\\xa0\\xc4 \\xb0rh/@u=\\n\\xd7\\xa3p/@J\\xb6\\xf3\\xfd\\xd4x/@\\x1f/\\xdd$\\x06\\x81/@\\xf4\\xa7\\xc6K7\\x89/@\\xc9 \\xb0rh\\x91/@\\x9e\\x99\\x99\\x99\\x99\\x99/@s\\x12\\x83\\xc0\\xca\\xa1/@H\\x8bl\\xe7\\xfb\\xa9/@\\x1d\\x04V\\x0e-\\xb2/@\\xf2|?5^\\xba/@\\xc7\\xf5(\\\\\\x8f\\xc2/@\\x9cn\\x12\\x83\\xc0\\xca/@q\\xe7\\xfb\\xa9\\xf1\\xd2/@F`\\xe5\\xd0\"\\xdb/@\\x1b\\xd9\\xce\\xf7S\\xe3/@\\xf0Q\\xb8\\x1e\\x85\\xeb/@\\xc5\\xca\\xa1E\\xb6\\xf3/@\\x9aC\\x8bl\\xe7\\xfb/@8^\\xbaI\\x0c\\x020@\\xa2\\x1a/\\xdd$\\x060@\\x0c\\xd7\\xa3p=\\n0@w\\x93\\x18\\x04V\\x0e0@\\xe2O\\x8d\\x97n\\x120@L\\x0c\\x02+\\x87\\x160@\\xb6\\xc8v\\xbe\\x9f\\x1a0@!\\x85\\xebQ\\xb8\\x1e0@\\x8cA`\\xe5\\xd0\"0@\\xf6\\xfd\\xd4x\\xe9&0@`\\xbaI\\x0c\\x02+0@\\xcbv\\xbe\\x9f\\x1a/0@6333330@\\xa0\\xef\\xa7\\xc6K70@\\n\\xac\\x1cZd;0@uh\\x91\\xed|?0@\\xe0$\\x06\\x81\\x95C0@J\\xe1z\\x14\\xaeG0@\\xb4\\x9d\\xef\\xa7\\xc6K0@\\x1fZd;\\xdfO0@\\x8a\\x16\\xd9\\xce\\xf7S0@\\xf4\\xd2Mb\\x10X0@^\\x8f\\xc2\\xf5(\\\\0@\\xc9K7\\x89A`0@4\\x08\\xac\\x1cZd0@\\x9e\\xc4 \\xb0rh0@\\x08\\x81\\x95C\\x8bl0@s=\\n\\xd7\\xa3p0@\\xde\\xf9~j\\xbct0@H\\xb6\\xf3\\xfd\\xd4x0@\\xb2rh\\x91\\xed|0@\\x1d/\\xdd$\\x06\\x810@\\x88\\xebQ\\xb8\\x1e\\x850@\\xf2\\xa7\\xc6K7\\x890@\\\\d;\\xdfO\\x8d0@\\xc7 \\xb0rh\\x910@2\\xdd$\\x06\\x81\\x950@\\x9c\\x99\\x99\\x99\\x99\\x990@\\x06V\\x0e-\\xb2\\x9d0@q\\x12\\x83\\xc0\\xca\\xa10@\\xdc\\xce\\xf7S\\xe3\\xa50@F\\x8bl\\xe7\\xfb\\xa90@\\xb0G\\xe1z\\x14\\xae0@\\x1b\\x04V\\x0e-\\xb20@\\x86\\xc0\\xca\\xa1E\\xb60@\\xf0|?5^\\xba0@Z9\\xb4\\xc8v\\xbe0@\\xc5\\xf5(\\\\\\x8f\\xc20@0\\xb2\\x9d\\xef\\xa7\\xc60@\\x9an\\x12\\x83\\xc0\\xca0@\\x04+\\x87\\x16\\xd9\\xce0@o\\xe7\\xfb\\xa9\\xf1\\xd20@\\xda\\xa3p=\\n\\xd70@D`\\xe5\\xd0\"\\xdb0@\\xae\\x1cZd;\\xdf0@\\x19\\xd9\\xce\\xf7S\\xe30@\\x84\\x95C\\x8bl\\xe70@\\xeeQ\\xb8\\x1e\\x85\\xeb0@X\\x0e-\\xb2\\x9d\\xef0@\\xc3\\xca\\xa1E\\xb6\\xf30@.\\x87\\x16\\xd9\\xce\\xf70@\\x98C\\x8bl\\xe7\\xfb0@\\x02\\x00\\x00\\x00\\x00\\x001@m\\xbct\\x93\\x18\\x041@\\xd8x\\xe9&1\\x081@B5^\\xbaI\\x0c1@\\xac\\xf1\\xd2Mb\\x101@\\x17\\xaeG\\xe1z\\x141@\\x82j\\xbct\\x93\\x181@\\xec&1\\x08\\xac\\x1c1@V\\xe3\\xa5\\x9b\\xc4 1@\\xc1\\x9f\\x1a/\\xdd$1@,\\\\\\x8f\\xc2\\xf5(1@\\x96\\x18\\x04V\\x0e-1@\\x00\\xd5x\\xe9&11@k\\x91\\xed|?51@\\xd6Mb\\x10X91@@\\n\\xd7\\xa3p=1@\\xaa\\xc6K7\\x89A1@\\x15\\x83\\xc0\\xca\\xa1E1@\\x80?5^\\xbaI1@\\xea\\xfb\\xa9\\xf1\\xd2M1@T\\xb8\\x1e\\x85\\xebQ1@\\xbft\\x93\\x18\\x04V1@*1\\x08\\xac\\x1cZ1@\\x94\\xed|?5^1@\\xfe\\xa9\\xf1\\xd2Mb1@ifffff1@\\xd4\"\\xdb\\xf9~j1@>\\xdfO\\x8d\\x97n1@\\xa8\\x9b\\xc4 \\xb0r1@\\x13X9\\xb4\\xc8v1@~\\x14\\xaeG\\xe1z1@\\xe8\\xd0\"\\xdb\\xf9~1@R\\x8d\\x97n\\x12\\x831@\\xbdI\\x0c\\x02+\\x871@(\\x06\\x81\\x95C\\x8b1@\\x92\\xc2\\xf5(\\\\\\x8f1@\\xfc~j\\xbct\\x931@g;\\xdfO\\x8d\\x971@\\xd2\\xf7S\\xe3\\xa5\\x9b1@<\\xb4\\xc8v\\xbe\\x9f1@\\xa6p=\\n\\xd7\\xa31@\\x11-\\xb2\\x9d\\xef\\xa71@|\\xe9&1\\x08\\xac1@\\xe6\\xa5\\x9b\\xc4 \\xb01@Pb\\x10X9\\xb41@\\xbb\\x1e\\x85\\xebQ\\xb81@&\\xdb\\xf9~j\\xbc1@\\x90\\x97n\\x12\\x83\\xc01@\\xfaS\\xe3\\xa5\\x9b\\xc41@e\\x10X9\\xb4\\xc81@\\xd0\\xcc\\xcc\\xcc\\xcc\\xcc1@:\\x89A`\\xe5\\xd01@\\xa4E\\xb6\\xf3\\xfd\\xd41@\\x0f\\x02+\\x87\\x16\\xd91@z\\xbe\\x9f\\x1a/\\xdd1@\\xe4z\\x14\\xaeG\\xe11@N7\\x89A`\\xe51@\\xb9\\xf3\\xfd\\xd4x\\xe91@$\\xb0rh\\x91\\xed1@\\x8el\\xe7\\xfb\\xa9\\xf11@\\xf8(\\\\\\x8f\\xc2\\xf51@c\\xe5\\xd0\"\\xdb\\xf91@\\xce\\xa1E\\xb6\\xf3\\xfd1@8^\\xbaI\\x0c\\x022@\\xa2\\x1a/\\xdd$\\x062@\\r\\xd7\\xa3p=\\n2@x\\x93\\x18\\x04V\\x0e2@\\xe2O\\x8d\\x97n\\x122@L\\x0c\\x02+\\x87\\x162@\\xb7\\xc8v\\xbe\\x9f\\x1a2@\"\\x85\\xebQ\\xb8\\x1e2@\\x8cA`\\xe5\\xd0\"2@\\xf6\\xfd\\xd4x\\xe9&2@a\\xbaI\\x0c\\x02+2@\\xccv\\xbe\\x9f\\x1a/2@6333332@\\xa0\\xef\\xa7\\xc6K72@\\x0b\\xac\\x1cZd;2@vh\\x91\\xed|?2@\\xe0$\\x06\\x81\\x95C2@J\\xe1z\\x14\\xaeG2@\\xb5\\x9d\\xef\\xa7\\xc6K2@ Zd;\\xdfO2@\\x8a\\x16\\xd9\\xce\\xf7S2@\\xf4\\xd2Mb\\x10X2@_\\x8f\\xc2\\xf5(\\\\2@\\xcaK7\\x89A`2@4\\x08\\xac\\x1cZd2@\\x9e\\xc4 \\xb0rh2@\\t\\x81\\x95C\\x8bl2@t=\\n\\xd7\\xa3p2@\\xde\\xf9~j\\xbct2@H\\xb6\\xf3\\xfd\\xd4x2@\\xb3rh\\x91\\xed|2@\\x1e/\\xdd$\\x06\\x812@\\x88\\xebQ\\xb8\\x1e\\x852@\\xf2\\xa7\\xc6K7\\x892@]d;\\xdfO\\x8d2@\\xc8 \\xb0rh\\x912@2\\xdd$\\x06\\x81\\x952@\\x9c\\x99\\x99\\x99\\x99\\x992@\\x07V\\x0e-\\xb2\\x9d2@r\\x12\\x83\\xc0\\xca\\xa12@\\xdc\\xce\\xf7S\\xe3\\xa52@F\\x8bl\\xe7\\xfb\\xa92@\\xb1G\\xe1z\\x14\\xae2@\\x1c\\x04V\\x0e-\\xb22@\\x86\\xc0\\xca\\xa1E\\xb62@\\xf0|?5^\\xba2@[9\\xb4\\xc8v\\xbe2@\\xc6\\xf5(\\\\\\x8f\\xc22@0\\xb2\\x9d\\xef\\xa7\\xc62@\\x9an\\x12\\x83\\xc0\\xca2@\\x05+\\x87\\x16\\xd9\\xce2@p\\xe7\\xfb\\xa9\\xf1\\xd22@\\xda\\xa3p=\\n\\xd72@D`\\xe5\\xd0\"\\xdb2@\\xaf\\x1cZd;\\xdf2@\\x1a\\xd9\\xce\\xf7S\\xe32@\\x84\\x95C\\x8bl\\xe72@\\xeeQ\\xb8\\x1e\\x85\\xeb2@Y\\x0e-\\xb2\\x9d\\xef2@\\xc4\\xca\\xa1E\\xb6\\xf32@.\\x87\\x16\\xd9\\xce\\xf72@\\x98C\\x8bl\\xe7\\xfb2@\\x03\\x00\\x00\\x00\\x00\\x003@n\\xbct\\x93\\x18\\x043@\\xd8x\\xe9&1\\x083@B5^\\xbaI\\x0c3@\\xad\\xf1\\xd2Mb\\x103@\\x18\\xaeG\\xe1z\\x143@\\x82j\\xbct\\x93\\x183@\\xec&1\\x08\\xac\\x1c3@W\\xe3\\xa5\\x9b\\xc4 3@\\xc2\\x9f\\x1a/\\xdd$3@,\\\\\\x8f\\xc2\\xf5(3@\\x96\\x18\\x04V\\x0e-3@\\x01\\xd5x\\xe9&13@l\\x91\\xed|?53@\\xd6Mb\\x10X93@@\\n\\xd7\\xa3p=3@\\xab\\xc6K7\\x89A3@\\x16\\x83\\xc0\\xca\\xa1E3@\\x80?5^\\xbaI3@\\xea\\xfb\\xa9\\xf1\\xd2M3@U\\xb8\\x1e\\x85\\xebQ3@\\xc0t\\x93\\x18\\x04V3@*1\\x08\\xac\\x1cZ3@\\x94\\xed|?5^3@\\xff\\xa9\\xf1\\xd2Mb3@jfffff3@\\xd4\"\\xdb\\xf9~j3@>\\xdfO\\x8d\\x97n3@\\xa9\\x9b\\xc4 \\xb0r3@\\x14X9\\xb4\\xc8v3@~\\x14\\xaeG\\xe1z3@\\xe8\\xd0\"\\xdb\\xf9~3@S\\x8d\\x97n\\x12\\x833@\\xbeI\\x0c\\x02+\\x873@(\\x06\\x81\\x95C\\x8b3@\\x92\\xc2\\xf5(\\\\\\x8f3@\\xfd~j\\xbct\\x933@h;\\xdfO\\x8d\\x973@\\xd2\\xf7S\\xe3\\xa5\\x9b3@<\\xb4\\xc8v\\xbe\\x9f3@\\xa7p=\\n\\xd7\\xa33@\\x12-\\xb2\\x9d\\xef\\xa73@|\\xe9&1\\x08\\xac3@\\xe6\\xa5\\x9b\\xc4 \\xb03@Qb\\x10X9\\xb43@\\xbc\\x1e\\x85\\xebQ\\xb83@&\\xdb\\xf9~j\\xbc3@\\x90\\x97n\\x12\\x83\\xc03@\\xfbS\\xe3\\xa5\\x9b\\xc43@f\\x10X9\\xb4\\xc83@\\xd0\\xcc\\xcc\\xcc\\xcc\\xcc3@:\\x89A`\\xe5\\xd03@\\xa5E\\xb6\\xf3\\xfd\\xd43@\\x10\\x02+\\x87\\x16\\xd93@z\\xbe\\x9f\\x1a/\\xdd3@\\xe4z\\x14\\xaeG\\xe13@O7\\x89A`\\xe53@\\xba\\xf3\\xfd\\xd4x\\xe93@$\\xb0rh\\x91\\xed3@\\x8el\\xe7\\xfb\\xa9\\xf13@\\xf9(\\\\\\x8f\\xc2\\xf53@d\\xe5\\xd0\"\\xdb\\xf93@\\xce\\xa1E\\xb6\\xf3\\xfd3@8^\\xbaI\\x0c\\x024@\\xa3\\x1a/\\xdd$\\x064@\\x0e\\xd7\\xa3p=\\n4@x\\x93\\x18\\x04V\\x0e4@\\xe2O\\x8d\\x97n\\x124@M\\x0c\\x02+\\x87\\x164@\\xb8\\xc8v\\xbe\\x9f\\x1a4@\"\\x85\\xebQ\\xb8\\x1e4@\\x8cA`\\xe5\\xd0\"4@\\xf7\\xfd\\xd4x\\xe9&4@b\\xbaI\\x0c\\x02+4@\\xccv\\xbe\\x9f\\x1a/4@6333334@\\xa1\\xef\\xa7\\xc6K74@\\x0c\\xac\\x1cZd;4@vh\\x91\\xed|?4@\\xe0$\\x06\\x81\\x95C4@K\\xe1z\\x14\\xaeG4@\\xb6\\x9d\\xef\\xa7\\xc6K4@ Zd;\\xdfO4@\\x8a\\x16\\xd9\\xce\\xf7S4@\\xf5\\xd2Mb\\x10X4@`\\x8f\\xc2\\xf5(\\\\4@\\xcaK7\\x89A`4@4\\x08\\xac\\x1cZd4@\\x9f\\xc4 \\xb0rh4@\\n\\x81\\x95C\\x8bl4@t=\\n\\xd7\\xa3p4@\\xde\\xf9~j\\xbct4@I\\xb6\\xf3\\xfd\\xd4x4@\\xb4rh\\x91\\xed|4@\\x1e/\\xdd$\\x06\\x814@\\x88\\xebQ\\xb8\\x1e\\x854@\\xf3\\xa7\\xc6K7\\x894@^d;\\xdfO\\x8d4@\\xc8 \\xb0rh\\x914@2\\xdd$\\x06\\x81\\x954@\\x9d\\x99\\x99\\x99\\x99\\x994@\\x08V\\x0e-\\xb2\\x9d4@r\\x12\\x83\\xc0\\xca\\xa14@\\xdc\\xce\\xf7S\\xe3\\xa54@G\\x8bl\\xe7\\xfb\\xa94@\\xb2G\\xe1z\\x14\\xae4@\\x1c\\x04V\\x0e-\\xb24@\\x86\\xc0\\xca\\xa1E\\xb64@\\xf1|?5^\\xba4@\\\\9\\xb4\\xc8v\\xbe4@\\xc6\\xf5(\\\\\\x8f\\xc24@0\\xb2\\x9d\\xef\\xa7\\xc64@\\x9bn\\x12\\x83\\xc0\\xca4@\\x06+\\x87\\x16\\xd9\\xce4@p\\xe7\\xfb\\xa9\\xf1\\xd24@\\xda\\xa3p=\\n\\xd74@E`\\xe5\\xd0\"\\xdb4@\\xb0\\x1cZd;\\xdf4@\\x1a\\xd9\\xce\\xf7S\\xe34@\\x84\\x95C\\x8bl\\xe74@\\xefQ\\xb8\\x1e\\x85\\xeb4@Z\\x0e-\\xb2\\x9d\\xef4@\\xc4\\xca\\xa1E\\xb6\\xf34@.\\x87\\x16\\xd9\\xce\\xf74@\\x99C\\x8bl\\xe7\\xfb4@\\x04\\x00\\x00\\x00\\x00\\x005@n\\xbct\\x93\\x18\\x045@\\xd8x\\xe9&1\\x085@C5^\\xbaI\\x0c5@\\xae\\xf1\\xd2Mb\\x105@\\x18\\xaeG\\xe1z\\x145@\\x82j\\xbct\\x93\\x185@\\xed&1\\x08\\xac\\x1c5@X\\xe3\\xa5\\x9b\\xc4 5@\\xc2\\x9f\\x1a/\\xdd$5@,\\\\\\x8f\\xc2\\xf5(5@\\x97\\x18\\x04V\\x0e-5@\\x02\\xd5x\\xe9&15@l\\x91\\xed|?55@\\xd6Mb\\x10X95@A\\n\\xd7\\xa3p=5@\\xac\\xc6K7\\x89A5@\\x16\\x83\\xc0\\xca\\xa1E5@\\x80?5^\\xbaI5@\\xeb\\xfb\\xa9\\xf1\\xd2M5@V\\xb8\\x1e\\x85\\xebQ5@\\xc0t\\x93\\x18\\x04V5@*1\\x08\\xac\\x1cZ5@\\x95\\xed|?5^5@\\x00\\xaa\\xf1\\xd2Mb5@jfffff5@\\xd4\"\\xdb\\xf9~j5@?\\xdfO\\x8d\\x97n5@\\xaa\\x9b\\xc4 \\xb0r5@\\x14X9\\xb4\\xc8v5@~\\x14\\xaeG\\xe1z5@\\xe9\\xd0\"\\xdb\\xf9~5@T\\x8d\\x97n\\x12\\x835@\\xbeI\\x0c\\x02+\\x875@(\\x06\\x81\\x95C\\x8b5@\\x93\\xc2\\xf5(\\\\\\x8f5@\\xfe~j\\xbct\\x935@h;\\xdfO\\x8d\\x975@\\xd2\\xf7S\\xe3\\xa5\\x9b5@=\\xb4\\xc8v\\xbe\\x9f5@\\xa8p=\\n\\xd7\\xa35@\\x12-\\xb2\\x9d\\xef\\xa75@|\\xe9&1\\x08\\xac5@\\xe7\\xa5\\x9b\\xc4 \\xb05@Rb\\x10X9\\xb45@\\xbc\\x1e\\x85\\xebQ\\xb85@&\\xdb\\xf9~j\\xbc5@\\x91\\x97n\\x12\\x83\\xc05@\\xfcS\\xe3\\xa5\\x9b\\xc45@f\\x10X9\\xb4\\xc85@\\xd0\\xcc\\xcc\\xcc\\xcc\\xcc5@;\\x89A`\\xe5\\xd05@\\xa6E\\xb6\\xf3\\xfd\\xd45@\\x10\\x02+\\x87\\x16\\xd95@z\\xbe\\x9f\\x1a/\\xdd5@\\xe5z\\x14\\xaeG\\xe15@P7\\x89A`\\xe55@\\xba\\xf3\\xfd\\xd4x\\xe95@$\\xb0rh\\x91\\xed5@\\x8fl\\xe7\\xfb\\xa9\\xf15@\\xfa(\\\\\\x8f\\xc2\\xf55@d\\xe5\\xd0\"\\xdb\\xf95@\\xce\\xa1E\\xb6\\xf3\\xfd5@9^\\xbaI\\x0c\\x026@\\xa4\\x1a/\\xdd$\\x066@\\x0e\\xd7\\xa3p=\\n6@x\\x93\\x18\\x04V\\x0e6@\\xe3O\\x8d\\x97n\\x126@N\\x0c\\x02+\\x87\\x166@\\xb8\\xc8v\\xbe\\x9f\\x1a6@\"\\x85\\xebQ\\xb8\\x1e6@\\x8dA`\\xe5\\xd0\"6@\\xf8\\xfd\\xd4x\\xe9&6@b\\xbaI\\x0c\\x02+6@\\xccv\\xbe\\x9f\\x1a/6@7333336@\\xa2\\xef\\xa7\\xc6K76@\\x0c\\xac\\x1cZd;6@vh\\x91\\xed|?6@\\xe1$\\x06\\x81\\x95C6@L\\xe1z\\x14\\xaeG6@\\xb6\\x9d\\xef\\xa7\\xc6K6@ Zd;\\xdfO6@\\x8b\\x16\\xd9\\xce\\xf7S6@\\xf6\\xd2Mb\\x10X6@`\\x8f\\xc2\\xf5(\\\\6@\\xcaK7\\x89A`6@5\\x08\\xac\\x1cZd6@\\xa0\\xc4 \\xb0rh6@\\n\\x81\\x95C\\x8bl6@t=\\n\\xd7\\xa3p6@\\xdf\\xf9~j\\xbct6@J\\xb6\\xf3\\xfd\\xd4x6@\\xb4rh\\x91\\xed|6@\\x1e/\\xdd$\\x06\\x816@\\x89\\xebQ\\xb8\\x1e\\x856@\\xf4\\xa7\\xc6K7\\x896@^d;\\xdfO\\x8d6@\\xc8 \\xb0rh\\x916@3\\xdd$\\x06\\x81\\x956@\\x9e\\x99\\x99\\x99\\x99\\x996@\\x08V\\x0e-\\xb2\\x9d6@r\\x12\\x83\\xc0\\xca\\xa16@\\xdd\\xce\\xf7S\\xe3\\xa56@H\\x8bl\\xe7\\xfb\\xa96@\\xb2G\\xe1z\\x14\\xae6@\\x1c\\x04V\\x0e-\\xb26@\\x87\\xc0\\xca\\xa1E\\xb66@\\xf2|?5^\\xba6@\\\\9\\xb4\\xc8v\\xbe6@\\xc6\\xf5(\\\\\\x8f\\xc26@1\\xb2\\x9d\\xef\\xa7\\xc66@\\x9cn\\x12\\x83\\xc0\\xca6@\\x06+\\x87\\x16\\xd9\\xce6@p\\xe7\\xfb\\xa9\\xf1\\xd26@\\xdb\\xa3p=\\n\\xd76@F`\\xe5\\xd0\"\\xdb6@\\xb0\\x1cZd;\\xdf6@\\x1a\\xd9\\xce\\xf7S\\xe36@\\x85\\x95C\\x8bl\\xe76@\\xf0Q\\xb8\\x1e\\x85\\xeb6@Z\\x0e-\\xb2\\x9d\\xef6@\\xc4\\xca\\xa1E\\xb6\\xf36@/\\x87\\x16\\xd9\\xce\\xf76@\\x9aC\\x8bl\\xe7\\xfb6@\\x04\\x00\\x00\\x00\\x00\\x007@n\\xbct\\x93\\x18\\x047@\\xd9x\\xe9&1\\x087@D5^\\xbaI\\x0c7@\\xae\\xf1\\xd2Mb\\x107@\\x18\\xaeG\\xe1z\\x147@\\x83j\\xbct\\x93\\x187@\\xee&1\\x08\\xac\\x1c7@X\\xe3\\xa5\\x9b\\xc4 7@\\xc2\\x9f\\x1a/\\xdd$7@-\\\\\\x8f\\xc2\\xf5(7@\\x98\\x18\\x04V\\x0e-7@\\x02\\xd5x\\xe9&17@l\\x91\\xed|?57@\\xd7Mb\\x10X97@B\\n\\xd7\\xa3p=7@\\xac\\xc6K7\\x89A7@\\x16\\x83\\xc0\\xca\\xa1E7@\\x81?5^\\xbaI7@\\xec\\xfb\\xa9\\xf1\\xd2M7@V\\xb8\\x1e\\x85\\xebQ7@\\xc0t\\x93\\x18\\x04V7@+1\\x08\\xac\\x1cZ7@\\x96\\xed|?5^7@\\x00\\xaa\\xf1\\xd2Mb7@jfffff7@\\xd5\"\\xdb\\xf9~j7@@\\xdfO\\x8d\\x97n7@\\xaa\\x9b\\xc4 \\xb0r7@\\x14X9\\xb4\\xc8v7@\\x7f\\x14\\xaeG\\xe1z7@\\xea\\xd0\"\\xdb\\xf9~7@T\\x8d\\x97n\\x12\\x837@\\xbeI\\x0c\\x02+\\x877@)\\x06\\x81\\x95C\\x8b7@\\x94\\xc2\\xf5(\\\\\\x8f7@\\xfe~j\\xbct\\x937@h;\\xdfO\\x8d\\x977@\\xd3\\xf7S\\xe3\\xa5\\x9b7@>\\xb4\\xc8v\\xbe\\x9f7@\\xa8p=\\n\\xd7\\xa37@\\x12-\\xb2\\x9d\\xef\\xa77@}\\xe9&1\\x08\\xac7@\\xe8\\xa5\\x9b\\xc4 \\xb07@Rb\\x10X9\\xb47@\\xbc\\x1e\\x85\\xebQ\\xb87@\\'\\xdb\\xf9~j\\xbc7@\\x92\\x97n\\x12\\x83\\xc07@\\xfcS\\xe3\\xa5\\x9b\\xc47@f\\x10X9\\xb4\\xc87@\\xd1\\xcc\\xcc\\xcc\\xcc\\xcc7@<\\x89A`\\xe5\\xd07@\\xa6E\\xb6\\xf3\\xfd\\xd47@\\x10\\x02+\\x87\\x16\\xd97@{\\xbe\\x9f\\x1a/\\xdd7@\\xe6z\\x14\\xaeG\\xe17@P7\\x89A`\\xe57@\\xba\\xf3\\xfd\\xd4x\\xe97@%\\xb0rh\\x91\\xed7@\\x90l\\xe7\\xfb\\xa9\\xf17@\\xfa(\\\\\\x8f\\xc2\\xf57@d\\xe5\\xd0\"\\xdb\\xf97@\\xcf\\xa1E\\xb6\\xf3\\xfd7@:^\\xbaI\\x0c\\x028@\\xa4\\x1a/\\xdd$\\x068@\\x0e\\xd7\\xa3p=\\n8@y\\x93\\x18\\x04V\\x0e8@\\xe4O\\x8d\\x97n\\x128@N\\x0c\\x02+\\x87\\x168@\\xb8\\xc8v\\xbe\\x9f\\x1a8@#\\x85\\xebQ\\xb8\\x1e8@\\x8eA`\\xe5\\xd0\"8@\\xf8\\xfd\\xd4x\\xe9&8@b\\xbaI\\x0c\\x02+8@\\xcdv\\xbe\\x9f\\x1a/8@8333338@\\xa2\\xef\\xa7\\xc6K78@\\x0c\\xac\\x1cZd;8@wh\\x91\\xed|?8@\\xe2$\\x06\\x81\\x95C8@L\\xe1z\\x14\\xaeG8@\\xb6\\x9d\\xef\\xa7\\xc6K8@!Zd;\\xdfO8@\\x8c\\x16\\xd9\\xce\\xf7S8@\\xf6\\xd2Mb\\x10X8@`\\x8f\\xc2\\xf5(\\\\8@\\xcbK7\\x89A`8@6\\x08\\xac\\x1cZd8@\\xa0\\xc4 \\xb0rh8@\\n\\x81\\x95C\\x8bl8@u=\\n\\xd7\\xa3p8@\\xe0\\xf9~j\\xbct8@J\\xb6\\xf3\\xfd\\xd4x8@\\xb4rh\\x91\\xed|8@\\x1f/\\xdd$\\x06\\x818@\\x8a\\xebQ\\xb8\\x1e\\x858@\\xf4\\xa7\\xc6K7\\x898@^d;\\xdfO\\x8d8@\\xc9 \\xb0rh\\x918@4\\xdd$\\x06\\x81\\x958@\\x9e\\x99\\x99\\x99\\x99\\x998@\\x08V\\x0e-\\xb2\\x9d8@s\\x12\\x83\\xc0\\xca\\xa18@\\xde\\xce\\xf7S\\xe3\\xa58@H\\x8bl\\xe7\\xfb\\xa98@\\xb2G\\xe1z\\x14\\xae8@\\x1d\\x04V\\x0e-\\xb28@\\x88\\xc0\\xca\\xa1E\\xb68@\\xf2|?5^\\xba8@\\\\9\\xb4\\xc8v\\xbe8@\\xc7\\xf5(\\\\\\x8f\\xc28@2\\xb2\\x9d\\xef\\xa7\\xc68@\\x9cn\\x12\\x83\\xc0\\xca8@\\x06+\\x87\\x16\\xd9\\xce8@q\\xe7\\xfb\\xa9\\xf1\\xd28@\\xdc\\xa3p=\\n\\xd78@F`\\xe5\\xd0\"\\xdb8@\\xb0\\x1cZd;\\xdf8@\\x1b\\xd9\\xce\\xf7S\\xe38@\\x86\\x95C\\x8bl\\xe78@\\xf0Q\\xb8\\x1e\\x85\\xeb8@Z\\x0e-\\xb2\\x9d\\xef8@\\xc5\\xca\\xa1E\\xb6\\xf38@0\\x87\\x16\\xd9\\xce\\xf78@\\x9aC\\x8bl\\xe7\\xfb8@\\x04\\x00\\x00\\x00\\x00\\x009@o\\xbct\\x93\\x18\\x049@\\xdax\\xe9&1\\x089@D5^\\xbaI\\x0c9@\\xae\\xf1\\xd2Mb\\x109@\\x19\\xaeG\\xe1z\\x149@\\x84j\\xbct\\x93\\x189@\\xee&1\\x08\\xac\\x1c9@X\\xe3\\xa5\\x9b\\xc4 9@\\xc3\\x9f\\x1a/\\xdd$9@.\\\\\\x8f\\xc2\\xf5(9@\\x98\\x18\\x04V\\x0e-9@\\x02\\xd5x\\xe9&19@m\\x91\\xed|?59@\\xd8Mb\\x10X99@B\\n\\xd7\\xa3p=9@\\xac\\xc6K7\\x89A9@\\x17\\x83\\xc0\\xca\\xa1E9@\\x82?5^\\xbaI9@\\xec\\xfb\\xa9\\xf1\\xd2M9@V\\xb8\\x1e\\x85\\xebQ9@\\xc1t\\x93\\x18\\x04V9@,1\\x08\\xac\\x1cZ9@\\x96\\xed|?5^9@\\x00\\xaa\\xf1\\xd2Mb9@kfffff9@\\xd6\"\\xdb\\xf9~j9@@\\xdfO\\x8d\\x97n9@\\xaa\\x9b\\xc4 \\xb0r9@\\x15X9\\xb4\\xc8v9@\\x80\\x14\\xaeG\\xe1z9@\\xea\\xd0\"\\xdb\\xf9~9@T\\x8d\\x97n\\x12\\x839@\\xbfI\\x0c\\x02+\\x879@*\\x06\\x81\\x95C\\x8b9@\\x94\\xc2\\xf5(\\\\\\x8f9@\\xfe~j\\xbct\\x939@i;\\xdfO\\x8d\\x979@\\xd4\\xf7S\\xe3\\xa5\\x9b9@>\\xb4\\xc8v\\xbe\\x9f9@\\xa8p=\\n\\xd7\\xa39@\\x13-\\xb2\\x9d\\xef\\xa79@~\\xe9&1\\x08\\xac9@\\xe8\\xa5\\x9b\\xc4 \\xb09@Rb\\x10X9\\xb49@\\xbd\\x1e\\x85\\xebQ\\xb89@(\\xdb\\xf9~j\\xbc9@\\x92\\x97n\\x12\\x83\\xc09@\\xfcS\\xe3\\xa5\\x9b\\xc49@g\\x10X9\\xb4\\xc89@\\xd2\\xcc\\xcc\\xcc\\xcc\\xcc9@<\\x89A`\\xe5\\xd09@\\xa6E\\xb6\\xf3\\xfd\\xd49@\\x11\\x02+\\x87\\x16\\xd99@|\\xbe\\x9f\\x1a/\\xdd9@\\xe6z\\x14\\xaeG\\xe19@P7\\x89A`\\xe59@\\xbb\\xf3\\xfd\\xd4x\\xe99@&\\xb0rh\\x91\\xed9@\\x90l\\xe7\\xfb\\xa9\\xf19@\\xfa(\\\\\\x8f\\xc2\\xf59@e\\xe5\\xd0\"\\xdb\\xf99@\\xd0\\xa1E\\xb6\\xf3\\xfd9@:^\\xbaI\\x0c\\x02:@\\xa4\\x1a/\\xdd$\\x06:@\\x0f\\xd7\\xa3p=\\n:@z\\x93\\x18\\x04V\\x0e:@\\xe4O\\x8d\\x97n\\x12:@N\\x0c\\x02+\\x87\\x16:@\\xb9\\xc8v\\xbe\\x9f\\x1a:@$\\x85\\xebQ\\xb8\\x1e:@\\x8eA`\\xe5\\xd0\":@\\xf8\\xfd\\xd4x\\xe9&:@c\\xbaI\\x0c\\x02+:@\\xcev\\xbe\\x9f\\x1a/:@833333:@\\xa2\\xef\\xa7\\xc6K7:@\\r\\xac\\x1cZd;:@xh\\x91\\xed|?:@\\xe2$\\x06\\x81\\x95C:@L\\xe1z\\x14\\xaeG:@\\xb7\\x9d\\xef\\xa7\\xc6K:@\"Zd;\\xdfO:@\\x8c\\x16\\xd9\\xce\\xf7S:@\\xf6\\xd2Mb\\x10X:@a\\x8f\\xc2\\xf5(\\\\:@\\xccK7\\x89A`:@6\\x08\\xac\\x1cZd:@\\xa0\\xc4 \\xb0rh:@\\x0b\\x81\\x95C\\x8bl:@v=\\n\\xd7\\xa3p:@\\xe0\\xf9~j\\xbct:@J\\xb6\\xf3\\xfd\\xd4x:@\\xb5rh\\x91\\xed|:@ /\\xdd$\\x06\\x81:@\\x8a\\xebQ\\xb8\\x1e\\x85:@\\xf4\\xa7\\xc6K7\\x89:@_d;\\xdfO\\x8d:@\\xca \\xb0rh\\x91:@4\\xdd$\\x06\\x81\\x95:@\\x9e\\x99\\x99\\x99\\x99\\x99:@\\tV\\x0e-\\xb2\\x9d:@t\\x12\\x83\\xc0\\xca\\xa1:@\\xde\\xce\\xf7S\\xe3\\xa5:@H\\x8bl\\xe7\\xfb\\xa9:@\\xb3G\\xe1z\\x14\\xae:@\\x1e\\x04V\\x0e-\\xb2:@\\x88\\xc0\\xca\\xa1E\\xb6:@\\xf2|?5^\\xba:@]9\\xb4\\xc8v\\xbe:@\\xc8\\xf5(\\\\\\x8f\\xc2:@2\\xb2\\x9d\\xef\\xa7\\xc6:@\\x9cn\\x12\\x83\\xc0\\xca:@\\x07+\\x87\\x16\\xd9\\xce:@r\\xe7\\xfb\\xa9\\xf1\\xd2:@\\xdc\\xa3p=\\n\\xd7:@F`\\xe5\\xd0\"\\xdb:@\\xb1\\x1cZd;\\xdf:@\\x1c\\xd9\\xce\\xf7S\\xe3:@\\x86\\x95C\\x8bl\\xe7:@\\xf0Q\\xb8\\x1e\\x85\\xeb:@[\\x0e-\\xb2\\x9d\\xef:@\\xc6\\xca\\xa1E\\xb6\\xf3:@0\\x87\\x16\\xd9\\xce\\xf7:@\\x9aC\\x8bl\\xe7\\xfb:@\\x05\\x00\\x00\\x00\\x00\\x00;@p\\xbct\\x93\\x18\\x04;@\\xdax\\xe9&1\\x08;@D5^\\xbaI\\x0c;@\\xaf\\xf1\\xd2Mb\\x10;@\\x1a\\xaeG\\xe1z\\x14;@\\x84j\\xbct\\x93\\x18;@\\xee&1\\x08\\xac\\x1c;@Y\\xe3\\xa5\\x9b\\xc4 ;@\\xc4\\x9f\\x1a/\\xdd$;@.\\\\\\x8f\\xc2\\xf5(;@\\x98\\x18\\x04V\\x0e-;@\\x03\\xd5x\\xe9&1;@n\\x91\\xed|?5;@\\xd8Mb\\x10X9;@B\\n\\xd7\\xa3p=;@\\xad\\xc6K7\\x89A;@\\x18\\x83\\xc0\\xca\\xa1E;@\\x82?5^\\xbaI;@\\xec\\xfb\\xa9\\xf1\\xd2M;@W\\xb8\\x1e\\x85\\xebQ;@\\xc2t\\x93\\x18\\x04V;@,1\\x08\\xac\\x1cZ;@\\x96\\xed|?5^;@\\x01\\xaa\\xf1\\xd2Mb;@lfffff;@\\xd6\"\\xdb\\xf9~j;@@\\xdfO\\x8d\\x97n;@\\xab\\x9b\\xc4 \\xb0r;@\\x16X9\\xb4\\xc8v;@\\x80\\x14\\xaeG\\xe1z;@\\xea\\xd0\"\\xdb\\xf9~;@U\\x8d\\x97n\\x12\\x83;@\\xc0I\\x0c\\x02+\\x87;@*\\x06\\x81\\x95C\\x8b;@\\x94\\xc2\\xf5(\\\\\\x8f;@\\xff~j\\xbct\\x93;@j;\\xdfO\\x8d\\x97;@\\xd4\\xf7S\\xe3\\xa5\\x9b;@>\\xb4\\xc8v\\xbe\\x9f;@\\xa9p=\\n\\xd7\\xa3;@\\x14-\\xb2\\x9d\\xef\\xa7;@~\\xe9&1\\x08\\xac;@\\xe8\\xa5\\x9b\\xc4 \\xb0;@Sb\\x10X9\\xb4;@\\xbe\\x1e\\x85\\xebQ\\xb8;@(\\xdb\\xf9~j\\xbc;@\\x92\\x97n\\x12\\x83\\xc0;@\\xfdS\\xe3\\xa5\\x9b\\xc4;@h\\x10X9\\xb4\\xc8;@\\xd2\\xcc\\xcc\\xcc\\xcc\\xcc;@<\\x89A`\\xe5\\xd0;@\\xa7E\\xb6\\xf3\\xfd\\xd4;@\\x12\\x02+\\x87\\x16\\xd9;@|\\xbe\\x9f\\x1a/\\xdd;@\\xe6z\\x14\\xaeG\\xe1;@Q7\\x89A`\\xe5;@\\xbc\\xf3\\xfd\\xd4x\\xe9;@&\\xb0rh\\x91\\xed;@\\x90l\\xe7\\xfb\\xa9\\xf1;@\\xfb(\\\\\\x8f\\xc2\\xf5;@f\\xe5\\xd0\"\\xdb\\xf9;@\\xd0\\xa1E\\xb6\\xf3\\xfd;@:^\\xbaI\\x0c\\x02<@\\xa5\\x1a/\\xdd$\\x06<@\\x10\\xd7\\xa3p=\\n<@z\\x93\\x18\\x04V\\x0e<@\\xe4O\\x8d\\x97n\\x12<@O\\x0c\\x02+\\x87\\x16<@\\xba\\xc8v\\xbe\\x9f\\x1a<@$\\x85\\xebQ\\xb8\\x1e<@\\x8eA`\\xe5\\xd0\"<@\\xf9\\xfd\\xd4x\\xe9&<@d\\xbaI\\x0c\\x02+<@\\xcev\\xbe\\x9f\\x1a/<@833333<@\\xa3\\xef\\xa7\\xc6K7<@\\x0e\\xac\\x1cZd;<@xh\\x91\\xed|?<@\\xe2$\\x06\\x81\\x95C<@M\\xe1z\\x14\\xaeG<@\\xb8\\x9d\\xef\\xa7\\xc6K<@\"Zd;\\xdfO<@\\x8c\\x16\\xd9\\xce\\xf7S<@\\xf7\\xd2Mb\\x10X<@b\\x8f\\xc2\\xf5(\\\\<@\\xccK7\\x89A`<@6\\x08\\xac\\x1cZd<@\\xa1\\xc4 \\xb0rh<@\\x0c\\x81\\x95C\\x8bl<@v=\\n\\xd7\\xa3p<@\\xe0\\xf9~j\\xbct<@K\\xb6\\xf3\\xfd\\xd4x<@\\xb6rh\\x91\\xed|<@ /\\xdd$\\x06\\x81<@\\x8a\\xebQ\\xb8\\x1e\\x85<@\\xf5\\xa7\\xc6K7\\x89<@`d;\\xdfO\\x8d<@\\xca \\xb0rh\\x91<@4\\xdd$\\x06\\x81\\x95<@\\x9f\\x99\\x99\\x99\\x99\\x99<@\\nV\\x0e-\\xb2\\x9d<@t\\x12\\x83\\xc0\\xca\\xa1<@\\xde\\xce\\xf7S\\xe3\\xa5<@I\\x8bl\\xe7\\xfb\\xa9<@\\xb4G\\xe1z\\x14\\xae<@\\x1e\\x04V\\x0e-\\xb2<@\\x88\\xc0\\xca\\xa1E\\xb6<@\\xf3|?5^\\xba<@^9\\xb4\\xc8v\\xbe<@\\xc8\\xf5(\\\\\\x8f\\xc2<@2\\xb2\\x9d\\xef\\xa7\\xc6<@\\x9dn\\x12\\x83\\xc0\\xca<@\\x08+\\x87\\x16\\xd9\\xce<@r\\xe7\\xfb\\xa9\\xf1\\xd2<@\\xdc\\xa3p=\\n\\xd7<@G`\\xe5\\xd0\"\\xdb<@\\xb2\\x1cZd;\\xdf<@\\x1c\\xd9\\xce\\xf7S\\xe3<@\\x86\\x95C\\x8bl\\xe7<@\\xf1Q\\xb8\\x1e\\x85\\xeb<@\\\\\\x0e-\\xb2\\x9d\\xef<@\\xc6\\xca\\xa1E\\xb6\\xf3<@0\\x87\\x16\\xd9\\xce\\xf7<@\\x9bC\\x8bl\\xe7\\xfb<@\\x06\\x00\\x00\\x00\\x00\\x00=@p\\xbct\\x93\\x18\\x04=@\\xdax\\xe9&1\\x08=@E5^\\xbaI\\x0c=@\\xb0\\xf1\\xd2Mb\\x10=@\\x1a\\xaeG\\xe1z\\x14=@\\x84j\\xbct\\x93\\x18=@\\xef&1\\x08\\xac\\x1c=@Z\\xe3\\xa5\\x9b\\xc4 =@\\xc4\\x9f\\x1a/\\xdd$=@.\\\\\\x8f\\xc2\\xf5(=@\\x99\\x18\\x04V\\x0e-=@\\x04\\xd5x\\xe9&1=@n\\x91\\xed|?5=@\\xd8Mb\\x10X9=@C\\n\\xd7\\xa3p==@\\xae\\xc6K7\\x89A=@\\x18\\x83\\xc0\\xca\\xa1E=@\\x82?5^\\xbaI=@\\xed\\xfb\\xa9\\xf1\\xd2M=@X\\xb8\\x1e\\x85\\xebQ=@\\xc2t\\x93\\x18\\x04V=@,1\\x08\\xac\\x1cZ=@\\x97\\xed|?5^=@\\x02\\xaa\\xf1\\xd2Mb=@lfffff=@\\xd6\"\\xdb\\xf9~j=@A\\xdfO\\x8d\\x97n=@\\xac\\x9b\\xc4 \\xb0r=@\\x16X9\\xb4\\xc8v=@\\x80\\x14\\xaeG\\xe1z=@\\xeb\\xd0\"\\xdb\\xf9~=@V\\x8d\\x97n\\x12\\x83=@\\xc0I\\x0c\\x02+\\x87=@*\\x06\\x81\\x95C\\x8b=@\\x95\\xc2\\xf5(\\\\\\x8f=@\\x00\\x7fj\\xbct\\x93=@j;\\xdfO\\x8d\\x97=@\\xd4\\xf7S\\xe3\\xa5\\x9b=@?\\xb4\\xc8v\\xbe\\x9f=@\\xaap=\\n\\xd7\\xa3=@\\x14-\\xb2\\x9d\\xef\\xa7=@~\\xe9&1\\x08\\xac=@\\xe9\\xa5\\x9b\\xc4 \\xb0=@Tb\\x10X9\\xb4=@\\xbe\\x1e\\x85\\xebQ\\xb8=@(\\xdb\\xf9~j\\xbc=@\\x93\\x97n\\x12\\x83\\xc0=@\\xfeS\\xe3\\xa5\\x9b\\xc4=@h\\x10X9\\xb4\\xc8=@\\xd2\\xcc\\xcc\\xcc\\xcc\\xcc=@=\\x89A`\\xe5\\xd0=@\\xa8E\\xb6\\xf3\\xfd\\xd4=@\\x12\\x02+\\x87\\x16\\xd9=@|\\xbe\\x9f\\x1a/\\xdd=@\\xe7z\\x14\\xaeG\\xe1=@R7\\x89A`\\xe5=@\\xbc\\xf3\\xfd\\xd4x\\xe9=@&\\xb0rh\\x91\\xed=@\\x91l\\xe7\\xfb\\xa9\\xf1=@\\xfc(\\\\\\x8f\\xc2\\xf5=@f\\xe5\\xd0\"\\xdb\\xf9=@\\xd0\\xa1E\\xb6\\xf3\\xfd=@;^\\xbaI\\x0c\\x02>@\\xa6\\x1a/\\xdd$\\x06>@\\x10\\xd7\\xa3p=\\n>@z\\x93\\x18\\x04V\\x0e>@\\xe5O\\x8d\\x97n\\x12>@P\\x0c\\x02+\\x87\\x16>@\\xba\\xc8v\\xbe\\x9f\\x1a>@$\\x85\\xebQ\\xb8\\x1e>@\\x8fA`\\xe5\\xd0\">@\\xfa\\xfd\\xd4x\\xe9&>@d\\xbaI\\x0c\\x02+>@\\xcev\\xbe\\x9f\\x1a/>@933333>@\\xa4\\xef\\xa7\\xc6K7>@\\x0e\\xac\\x1cZd;>@xh\\x91\\xed|?>@\\xe3$\\x06\\x81\\x95C>@N\\xe1z\\x14\\xaeG>@\\xb8\\x9d\\xef\\xa7\\xc6K>@\"Zd;\\xdfO>@\\x8d\\x16\\xd9\\xce\\xf7S>@\\xf8\\xd2Mb\\x10X>@b\\x8f\\xc2\\xf5(\\\\>@\\xccK7\\x89A`>@7\\x08\\xac\\x1cZd>@\\xa2\\xc4 \\xb0rh>@\\x0c\\x81\\x95C\\x8bl>@v=\\n\\xd7\\xa3p>@\\xe1\\xf9~j\\xbct>@L\\xb6\\xf3\\xfd\\xd4x>@\\xb6rh\\x91\\xed|>@ /\\xdd$\\x06\\x81>@\\x8b\\xebQ\\xb8\\x1e\\x85>@\\xf6\\xa7\\xc6K7\\x89>@`d;\\xdfO\\x8d>@\\xca \\xb0rh\\x91>@5\\xdd$\\x06\\x81\\x95>@\\xa0\\x99\\x99\\x99\\x99\\x99>@\\nV\\x0e-\\xb2\\x9d>@t\\x12\\x83\\xc0\\xca\\xa1>@\\xdf\\xce\\xf7S\\xe3\\xa5>@J\\x8bl\\xe7\\xfb\\xa9>@\\xb4G\\xe1z\\x14\\xae>@\\x1e\\x04V\\x0e-\\xb2>@\\x89\\xc0\\xca\\xa1E\\xb6>@\\xf4|?5^\\xba>@^9\\xb4\\xc8v\\xbe>@\\xc8\\xf5(\\\\\\x8f\\xc2>@3\\xb2\\x9d\\xef\\xa7\\xc6>@\\x9en\\x12\\x83\\xc0\\xca>@\\x08+\\x87\\x16\\xd9\\xce>@r\\xe7\\xfb\\xa9\\xf1\\xd2>@\\xdd\\xa3p=\\n\\xd7>@H`\\xe5\\xd0\"\\xdb>@\\xb2\\x1cZd;\\xdf>@\\x1c\\xd9\\xce\\xf7S\\xe3>@\\x87\\x95C\\x8bl\\xe7>@\\xf2Q\\xb8\\x1e\\x85\\xeb>@\\\\\\x0e-\\xb2\\x9d\\xef>@\\xc6\\xca\\xa1E\\xb6\\xf3>@1\\x87\\x16\\xd9\\xce\\xf7>@\\x9cC\\x8bl\\xe7\\xfb>@\\x06\\x00\\x00\\x00\\x00\\x00?@\\x94\\x8c\\x05numpy\\x94\\x8c\\x05dtype\\x94\\x93\\x94\\x8c\\x02f8\\x94K\\x00K\\x01\\x87\\x94R\\x94(K\\x03\\x8c\\x01<\\x94NNNJ\\xff\\xff\\xff\\xffJ\\xff\\xff\\xff\\xffK\\x00t\\x94bM\\xdd\\x05\\x85\\x94\\x8c\\x01C\\x94t\\x94R\\x94.')"
}
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[8].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[8].electronFunctionString = {
    "data": '# @ct.electron\ndef convert_to_utc(time_zone):\n    start_time = 0\n    end_time = 24.016\n    now = datetime.now(pytz.timezone(time_zone))\n    offset = now.utcoffset().total_seconds() / 60 / 60\n    utc_timerange = np.arange(start_time - offset, end_time - offset, 0.016)\n    return utc_timerange\n\n\n',
}
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[8].electronError = null
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[8].electronInput = {
    "data": "{'args': (), 'kwargs': {'time_zone': 'America/Los_Angeles'}}",
    "python_object": "import pickle\npickle.loads(b'\\x80\\x05\\x95;\\x00\\x00\\x00\\x00\\x00\\x00\\x00}\\x94(\\x8c\\x04args\\x94)\\x8c\\x06kwargs\\x94}\\x94\\x8c\\ttime_zone\\x94\\x8c\\x13America/Los_Angeles\\x94su.')"
}
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[10].electronDetails = {
    "id": 10,
    "node_id": 10,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/ba3c238c-cb92-48e8-b7b2-debeebe2e81a/node_4",
    "name": "days_since_J2000",
    "status": "COMPLETED",
    "started_at": "2022-08-10T12:14:39",
    "ended_at": "2022-08-11T12:14:40",
    "runtime": 50
}
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[10].electronResult = {
    "data": "\"8305\"",
    "python_object": "import pickle\npickle.loads(b'\\x80\\x05\\x95\\x04\\x00\\x00\\x00\\x00\\x00\\x00\\x00Mq .')"
}
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[10].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[10].electronFunctionString = {
    "data": '# @ct.electron\ndef days_since_J2000(region):\n    f_date = date(2000, 1, 1)\n    year = get_date(time_zone=region)[0]\n    month = get_date(time_zone=region)[1]\n    day = get_date(time_zone=region)[2]\n    l_date = date(year, month, day)\n    delta = l_date - f_date\n    return delta.days\n\n\n'
}
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[10].electronError = null
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[10].electronInput = {
    "data": "{'args': (), 'kwargs': {'region': 'America/Los_Angeles'}}",
    "python_object": "import pickle\npickle.loads(b'\\x80\\x05\\x958\\x00\\x00\\x00\\x00\\x00\\x00\\x00}\\x94(\\x8c\\x04args\\x94)\\x8c\\x06kwargs\\x94}\\x94\\x8c\\x06region\\x94\\x8c\\x13America/Los_Angeles\\x94su.')"
}
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[12].electronDetails = {
    "id": 12,
    "node_id": 12,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/ba3c238c-cb92-48e8-b7b2-debeebe2e81a/node_4",
    "name": "local_sidereal_time",
    "status": "COMPLETED",
    "started_at": "2022-08-10T12:14:39",
    "ended_at": "2022-08-11T12:14:40",
    "runtime": 50
}
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[12].electronResult = {
    "data": "\"[8268.42511537 8268.66577247 8268.90642957 ... 8628.92944818 8629.17010528\\n 8629.41076238]\"",
    "python_object": "import pickle\npickle.loads(b'\\x80\\x05\\x95^/\\x00\\x00\\x00\\x00\\x00\\x00\\x8c\\x12numpy.core.numeric\\x94\\x8c\\x0b_frombuffer\\x94\\x93\\x94(\\x96\\xe8.\\x00\\x00\\x00\\x00\\x00\\x00R<.j6&\\xc0@\\x0eK\\x088U&\\xc0@\\xc9Y\\xe2\\x05t&\\xc0@\\x84h\\xbc\\xd3\\x92&\\xc0@?w\\x96\\xa1\\xb1&\\xc0@\\xfa\\x85po\\xd0&\\xc0@\\xb5\\x94J=\\xef&\\xc0@o\\xa3$\\x0b\\x0e\\'\\xc0@*\\xb2\\xfe\\xd8,\\'\\xc0@\\xe6\\xc0\\xd8\\xa6K\\'\\xc0@\\xa1\\xcf\\xb2tj\\'\\xc0@\\\\\\xde\\x8cB\\x89\\'\\xc0@\\x16\\xedf\\x10\\xa8\\'\\xc0@\\xd1\\xfb@\\xde\\xc6\\'\\xc0@\\x8c\\n\\x1b\\xac\\xe5\\'\\xc0@F\\x19\\xf5y\\x04(\\xc0@\\x01(\\xcfG#(\\xc0@\\xbd6\\xa9\\x15B(\\xc0@xE\\x83\\xe3`(\\xc0@3T]\\xb1\\x7f(\\xc0@\\xeeb7\\x7f\\x9e(\\xc0@\\xa9q\\x11M\\xbd(\\xc0@c\\x80\\xeb\\x1a\\xdc(\\xc0@\\x1e\\x8f\\xc5\\xe8\\xfa(\\xc0@\\xd9\\x9d\\x9f\\xb6\\x19)\\xc0@\\x94\\xacy\\x848)\\xc0@O\\xbbSRW)\\xc0@\\n\\xca- v)\\xc0@\\xc5\\xd8\\x07\\xee\\x94)\\xc0@\\x80\\xe7\\xe1\\xbb\\xb3)\\xc0@:\\xf6\\xbb\\x89\\xd2)\\xc0@\\xf5\\x04\\x96W\\xf1)\\xc0@\\xb0\\x13p%\\x10*\\xc0@k\"J\\xf3.*\\xc0@\\'1$\\xc1M*\\xc0@\\xe2?\\xfe\\x8el*\\xc0@\\x9dN\\xd8\\\\\\x8b*\\xc0@X]\\xb2*\\xaa*\\xc0@\\x11l\\x8c\\xf8\\xc8*\\xc0@\\xcczf\\xc6\\xe7*\\xc0@\\x87\\x89@\\x94\\x06+\\xc0@B\\x98\\x1ab%+\\xc0@\\xfe\\xa6\\xf4/D+\\xc0@\\xb9\\xb5\\xce\\xfdb+\\xc0@t\\xc4\\xa8\\xcb\\x81+\\xc0@.\\xd3\\x82\\x99\\xa0+\\xc0@\\xe9\\xe1\\\\g\\xbf+\\xc0@\\xa4\\xf065\\xde+\\xc0@_\\xff\\x10\\x03\\xfd+\\xc0@\\x1a\\x0e\\xeb\\xd0\\x1b,\\xc0@\\xd6\\x1c\\xc5\\x9e:,\\xc0@\\x91+\\x9flY,\\xc0@K:y:x,\\xc0@\\x05IS\\x08\\x97,\\xc0@\\xc0W-\\xd6\\xb5,\\xc0@{f\\x07\\xa4\\xd4,\\xc0@6u\\xe1q\\xf3,\\xc0@\\xf1\\x83\\xbb?\\x12-\\xc0@\\xac\\x92\\x95\\r1-\\xc0@h\\xa1o\\xdbO-\\xc0@#\\xb0I\\xa9n-\\xc0@\\xdd\\xbe#w\\x8d-\\xc0@\\x98\\xcd\\xfdD\\xac-\\xc0@S\\xdc\\xd7\\x12\\xcb-\\xc0@\\x0e\\xeb\\xb1\\xe0\\xe9-\\xc0@\\xc8\\xf9\\x8b\\xae\\x08.\\xc0@\\x83\\x08f|\\'.\\xc0@?\\x17@JF.\\xc0@\\xf9%\\x1a\\x18e.\\xc0@\\xb44\\xf4\\xe5\\x83.\\xc0@oC\\xce\\xb3\\xa2.\\xc0@*R\\xa8\\x81\\xc1.\\xc0@\\xe5`\\x82O\\xe0.\\xc0@\\xa0o\\\\\\x1d\\xff.\\xc0@[~6\\xeb\\x1d/\\xc0@\\x17\\x8d\\x10\\xb9</\\xc0@\\xd1\\x9b\\xea\\x86[/\\xc0@\\x8c\\xaa\\xc4Tz/\\xc0@G\\xb9\\x9e\"\\x99/\\xc0@\\x01\\xc8x\\xf0\\xb7/\\xc0@\\xbc\\xd6R\\xbe\\xd6/\\xc0@w\\xe5,\\x8c\\xf5/\\xc0@2\\xf4\\x06Z\\x140\\xc0@\\xec\\x02\\xe1\\'30\\xc0@\\xa8\\x11\\xbb\\xf5Q0\\xc0@c \\x95\\xc3p0\\xc0@\\x1e/o\\x91\\x8f0\\xc0@\\xd9=I_\\xae0\\xc0@\\x94L#-\\xcd0\\xc0@O[\\xfd\\xfa\\xeb0\\xc0@\\nj\\xd7\\xc8\\n1\\xc0@\\xc4x\\xb1\\x96)1\\xc0@\\x7f\\x87\\x8bdH1\\xc0@:\\x96e2g1\\xc0@\\xf5\\xa4?\\x00\\x861\\xc0@\\xb0\\xb3\\x19\\xce\\xa41\\xc0@k\\xc2\\xf3\\x9b\\xc31\\xc0@&\\xd1\\xcdi\\xe21\\xc0@\\xe1\\xdf\\xa77\\x012\\xc0@\\x9b\\xee\\x81\\x05 2\\xc0@W\\xfd[\\xd3>2\\xc0@\\x12\\x0c6\\xa1]2\\xc0@\\xcd\\x1a\\x10o|2\\xc0@\\x88)\\xea<\\x9b2\\xc0@C8\\xc4\\n\\xba2\\xc0@\\xfdF\\x9e\\xd8\\xd82\\xc0@\\xb7Ux\\xa6\\xf72\\xc0@rdRt\\x163\\xc0@-s,B53\\xc0@\\xe9\\x81\\x06\\x10T3\\xc0@\\xa4\\x90\\xe0\\xddr3\\xc0@_\\x9f\\xba\\xab\\x913\\xc0@\\x1a\\xae\\x94y\\xb03\\xc0@\\xd5\\xbcnG\\xcf3\\xc0@\\x8f\\xcbH\\x15\\xee3\\xc0@J\\xda\"\\xe3\\x0c4\\xc0@\\x05\\xe9\\xfc\\xb0+4\\xc0@\\xc1\\xf7\\xd6~J4\\xc0@|\\x06\\xb1Li4\\xc0@6\\x15\\x8b\\x1a\\x884\\xc0@\\xf1#e\\xe8\\xa64\\xc0@\\xac2?\\xb6\\xc54\\xc0@fA\\x19\\x84\\xe44\\xc0@!P\\xf3Q\\x035\\xc0@\\xdc^\\xcd\\x1f\"5\\xc0@\\x98m\\xa7\\xed@5\\xc0@S|\\x81\\xbb_5\\xc0@\\x0e\\x8b[\\x89~5\\xc0@\\xc9\\x995W\\x9d5\\xc0@\\x83\\xa8\\x0f%\\xbc5\\xc0@>\\xb7\\xe9\\xf2\\xda5\\xc0@\\xf9\\xc5\\xc3\\xc0\\xf95\\xc0@\\xb3\\xd4\\x9d\\x8e\\x186\\xc0@n\\xe3w\\\\76\\xc0@*\\xf2Q*V6\\xc0@\\xe5\\x00,\\xf8t6\\xc0@\\xa0\\x0f\\x06\\xc6\\x936\\xc0@Z\\x1e\\xe0\\x93\\xb26\\xc0@\\x15-\\xbaa\\xd16\\xc0@\\xd0;\\x94/\\xf06\\xc0@\\x8bJn\\xfd\\x0e7\\xc0@FYH\\xcb-7\\xc0@\\x02h\"\\x99L7\\xc0@\\xbdv\\xfcfk7\\xc0@w\\x85\\xd64\\x8a7\\xc0@2\\x94\\xb0\\x02\\xa97\\xc0@\\xec\\xa2\\x8a\\xd0\\xc77\\xc0@\\xa7\\xb1d\\x9e\\xe67\\xc0@b\\xc0>l\\x058\\xc0@\\x1d\\xcf\\x18:$8\\xc0@\\xd9\\xdd\\xf2\\x07C8\\xc0@\\x94\\xec\\xcc\\xd5a8\\xc0@N\\xfb\\xa6\\xa3\\x808\\xc0@\\t\\n\\x81q\\x9f8\\xc0@\\xc4\\x18[?\\xbe8\\xc0@\\x7f\\'5\\r\\xdd8\\xc0@:6\\x0f\\xdb\\xfb8\\xc0@\\xf5D\\xe9\\xa8\\x1a9\\xc0@\\xb0S\\xc3v99\\xc0@kb\\x9dDX9\\xc0@%qw\\x12w9\\xc0@\\xe0\\x7fQ\\xe0\\x959\\xc0@\\x9b\\x8e+\\xae\\xb49\\xc0@V\\x9d\\x05|\\xd39\\xc0@\\x11\\xac\\xdfI\\xf29\\xc0@\\xcc\\xba\\xb9\\x17\\x11:\\xc0@\\x87\\xc9\\x93\\xe5/:\\xc0@B\\xd8m\\xb3N:\\xc0@\\xfd\\xe6G\\x81m:\\xc0@\\xb8\\xf5!O\\x8c:\\xc0@s\\x04\\xfc\\x1c\\xab:\\xc0@.\\x13\\xd6\\xea\\xc9:\\xc0@\\xe8!\\xb0\\xb8\\xe8:\\xc0@\\xa30\\x8a\\x86\\x07;\\xc0@^?dT&;\\xc0@\\x19N>\"E;\\xc0@\\xd4\\\\\\x18\\xf0c;\\xc0@\\x8fk\\xf2\\xbd\\x82;\\xc0@Jz\\xcc\\x8b\\xa1;\\xc0@\\x05\\x89\\xa6Y\\xc0;\\xc0@\\xc0\\x97\\x80\\'\\xdf;\\xc0@{\\xa6Z\\xf5\\xfd;\\xc0@6\\xb54\\xc3\\x1c<\\xc0@\\xf0\\xc3\\x0e\\x91;<\\xc0@\\xac\\xd2\\xe8^Z<\\xc0@g\\xe1\\xc2,y<\\xc0@!\\xf0\\x9c\\xfa\\x97<\\xc0@\\xdc\\xfev\\xc8\\xb6<\\xc0@\\x97\\rQ\\x96\\xd5<\\xc0@R\\x1c+d\\xf4<\\xc0@\\x0c+\\x052\\x13=\\xc0@\\xc79\\xdf\\xff1=\\xc0@\\x83H\\xb9\\xcdP=\\xc0@>W\\x93\\x9bo=\\xc0@\\xf9emi\\x8e=\\xc0@\\xb4tG7\\xad=\\xc0@o\\x83!\\x05\\xcc=\\xc0@*\\x92\\xfb\\xd2\\xea=\\xc0@\\xe4\\xa0\\xd5\\xa0\\t>\\xc0@\\x9e\\xaf\\xafn(>\\xc0@Z\\xbe\\x89<G>\\xc0@\\x15\\xcdc\\nf>\\xc0@\\xd0\\xdb=\\xd8\\x84>\\xc0@\\x8b\\xea\\x17\\xa6\\xa3>\\xc0@F\\xf9\\xf1s\\xc2>\\xc0@\\x00\\x08\\xccA\\xe1>\\xc0@\\xbb\\x16\\xa6\\x0f\\x00?\\xc0@v%\\x80\\xdd\\x1e?\\xc0@14Z\\xab=?\\xc0@\\xedB4y\\\\?\\xc0@\\xa8Q\\x0eG{?\\xc0@c`\\xe8\\x14\\x9a?\\xc0@\\x1eo\\xc2\\xe2\\xb8?\\xc0@\\xd7}\\x9c\\xb0\\xd7?\\xc0@\\x92\\x8cv~\\xf6?\\xc0@M\\x9bPL\\x15@\\xc0@\\x08\\xaa*\\x1a4@\\xc0@\\xc4\\xb8\\x04\\xe8R@\\xc0@\\x7f\\xc7\\xde\\xb5q@\\xc0@:\\xd6\\xb8\\x83\\x90@\\xc0@\\xf5\\xe4\\x92Q\\xaf@\\xc0@\\xaf\\xf3l\\x1f\\xce@\\xc0@j\\x02G\\xed\\xec@\\xc0@%\\x11!\\xbb\\x0bA\\xc0@\\xe0\\x1f\\xfb\\x88*A\\xc0@\\x9c.\\xd5VIA\\xc0@V=\\xaf$hA\\xc0@\\x11L\\x89\\xf2\\x86A\\xc0@\\xcbZc\\xc0\\xa5A\\xc0@\\x86i=\\x8e\\xc4A\\xc0@Ax\\x17\\\\\\xe3A\\xc0@\\xfc\\x86\\xf1)\\x02B\\xc0@\\xb7\\x95\\xcb\\xf7 B\\xc0@r\\xa4\\xa5\\xc5?B\\xc0@.\\xb3\\x7f\\x93^B\\xc0@\\xe9\\xc1Ya}B\\xc0@\\xa3\\xd03/\\x9cB\\xc0@^\\xdf\\r\\xfd\\xbaB\\xc0@\\x19\\xee\\xe7\\xca\\xd9B\\xc0@\\xd3\\xfc\\xc1\\x98\\xf8B\\xc0@\\x8e\\x0b\\x9cf\\x17C\\xc0@I\\x1av46C\\xc0@\\x05)P\\x02UC\\xc0@\\xc07*\\xd0sC\\xc0@zF\\x04\\x9e\\x92C\\xc0@5U\\xdek\\xb1C\\xc0@\\xf0c\\xb89\\xd0C\\xc0@\\xabr\\x92\\x07\\xefC\\xc0@f\\x81l\\xd5\\rD\\xc0@!\\x90F\\xa3,D\\xc0@\\xdd\\x9e qKD\\xc0@\\x97\\xad\\xfa>jD\\xc0@R\\xbc\\xd4\\x0c\\x89D\\xc0@\\x0c\\xcb\\xae\\xda\\xa7D\\xc0@\\xc7\\xd9\\x88\\xa8\\xc6D\\xc0@\\x82\\xe8bv\\xe5D\\xc0@=\\xf7<D\\x04E\\xc0@\\xf8\\x05\\x17\\x12#E\\xc0@\\xb3\\x14\\xf1\\xdfAE\\xc0@n#\\xcb\\xad`E\\xc0@)2\\xa5{\\x7fE\\xc0@\\xe4@\\x7fI\\x9eE\\xc0@\\x9fOY\\x17\\xbdE\\xc0@Z^3\\xe5\\xdbE\\xc0@\\x15m\\r\\xb3\\xfaE\\xc0@\\xd0{\\xe7\\x80\\x19F\\xc0@\\x89\\x8a\\xc1N8F\\xc0@E\\x99\\x9b\\x1cWF\\xc0@\\x00\\xa8u\\xeauF\\xc0@\\xbb\\xb6O\\xb8\\x94F\\xc0@v\\xc5)\\x86\\xb3F\\xc0@1\\xd4\\x03T\\xd2F\\xc0@\\xec\\xe2\\xdd!\\xf1F\\xc0@\\xa7\\xf1\\xb7\\xef\\x0fG\\xc0@a\\x00\\x92\\xbd.G\\xc0@\\x1d\\x0fl\\x8bMG\\xc0@\\xd8\\x1dFYlG\\xc0@\\x93, \\'\\x8bG\\xc0@N;\\xfa\\xf4\\xa9G\\xc0@\\tJ\\xd4\\xc2\\xc8G\\xc0@\\xc3X\\xae\\x90\\xe7G\\xc0@~g\\x88^\\x06H\\xc0@8vb,%H\\xc0@\\xf4\\x84<\\xfaCH\\xc0@\\xaf\\x93\\x16\\xc8bH\\xc0@j\\xa2\\xf0\\x95\\x81H\\xc0@%\\xb1\\xcac\\xa0H\\xc0@\\xe0\\xbf\\xa41\\xbfH\\xc0@\\x9b\\xce~\\xff\\xddH\\xc0@U\\xddX\\xcd\\xfcH\\xc0@\\x10\\xec2\\x9b\\x1bI\\xc0@\\xcb\\xfa\\x0ci:I\\xc0@\\x87\\t\\xe76YI\\xc0@A\\x18\\xc1\\x04xI\\xc0@\\xfc&\\x9b\\xd2\\x96I\\xc0@\\xb75u\\xa0\\xb5I\\xc0@rDOn\\xd4I\\xc0@,S)<\\xf3I\\xc0@\\xe7a\\x03\\n\\x12J\\xc0@\\xa2p\\xdd\\xd70J\\xc0@^\\x7f\\xb7\\xa5OJ\\xc0@\\x19\\x8e\\x91snJ\\xc0@\\xd4\\x9ckA\\x8dJ\\xc0@\\x8f\\xabE\\x0f\\xacJ\\xc0@J\\xba\\x1f\\xdd\\xcaJ\\xc0@\\x04\\xc9\\xf9\\xaa\\xe9J\\xc0@\\xbe\\xd7\\xd3x\\x08K\\xc0@y\\xe6\\xadF\\'K\\xc0@4\\xf5\\x87\\x14FK\\xc0@\\xf0\\x03b\\xe2dK\\xc0@\\xab\\x12<\\xb0\\x83K\\xc0@f!\\x16~\\xa2K\\xc0@ 0\\xf0K\\xc1K\\xc0@\\xdb>\\xca\\x19\\xe0K\\xc0@\\x96M\\xa4\\xe7\\xfeK\\xc0@Q\\\\~\\xb5\\x1dL\\xc0@\\x0ckX\\x83<L\\xc0@\\xc8y2Q[L\\xc0@\\x83\\x88\\x0c\\x1fzL\\xc0@>\\x97\\xe6\\xec\\x98L\\xc0@\\xf7\\xa5\\xc0\\xba\\xb7L\\xc0@\\xb2\\xb4\\x9a\\x88\\xd6L\\xc0@m\\xc3tV\\xf5L\\xc0@(\\xd2N$\\x14M\\xc0@\\xe3\\xe0(\\xf22M\\xc0@\\x9f\\xef\\x02\\xc0QM\\xc0@Z\\xfe\\xdc\\x8dpM\\xc0@\\x14\\r\\xb7[\\x8fM\\xc0@\\xcf\\x1b\\x91)\\xaeM\\xc0@\\x8a*k\\xf7\\xccM\\xc0@E9E\\xc5\\xebM\\xc0@\\x00H\\x1f\\x93\\nN\\xc0@\\xbbV\\xf9`)N\\xc0@ve\\xd3.HN\\xc0@1t\\xad\\xfcfN\\xc0@\\xeb\\x82\\x87\\xca\\x85N\\xc0@\\xa6\\x91a\\x98\\xa4N\\xc0@a\\xa0;f\\xc3N\\xc0@\\x1c\\xaf\\x154\\xe2N\\xc0@\\xd7\\xbd\\xef\\x01\\x01O\\xc0@\\x92\\xcc\\xc9\\xcf\\x1fO\\xc0@M\\xdb\\xa3\\x9d>O\\xc0@\\t\\xea}k]O\\xc0@\\xc3\\xf8W9|O\\xc0@~\\x072\\x07\\x9bO\\xc0@9\\x16\\x0c\\xd5\\xb9O\\xc0@\\xf3$\\xe6\\xa2\\xd8O\\xc0@\\xae3\\xc0p\\xf7O\\xc0@iB\\x9a>\\x16P\\xc0@$Qt\\x0c5P\\xc0@\\xdf_N\\xdaSP\\xc0@\\x9an(\\xa8rP\\xc0@U}\\x02v\\x91P\\xc0@\\x10\\x8c\\xdcC\\xb0P\\xc0@\\xcb\\x9a\\xb6\\x11\\xcfP\\xc0@\\x86\\xa9\\x90\\xdf\\xedP\\xc0@A\\xb8j\\xad\\x0cQ\\xc0@\\xfc\\xc6D{+Q\\xc0@\\xb6\\xd5\\x1eIJQ\\xc0@r\\xe4\\xf8\\x16iQ\\xc0@,\\xf3\\xd2\\xe4\\x87Q\\xc0@\\xe7\\x01\\xad\\xb2\\xa6Q\\xc0@\\xa2\\x10\\x87\\x80\\xc5Q\\xc0@]\\x1faN\\xe4Q\\xc0@\\x18.;\\x1c\\x03R\\xc0@\\xd3<\\x15\\xea!R\\xc0@\\x8dK\\xef\\xb7@R\\xc0@IZ\\xc9\\x85_R\\xc0@\\x04i\\xa3S~R\\xc0@\\xbfw}!\\x9dR\\xc0@z\\x86W\\xef\\xbbR\\xc0@5\\x951\\xbd\\xdaR\\xc0@\\xf0\\xa3\\x0b\\x8b\\xf9R\\xc0@\\xa9\\xb2\\xe5X\\x18S\\xc0@d\\xc1\\xbf&7S\\xc0@ \\xd0\\x99\\xf4US\\xc0@\\xdb\\xdes\\xc2tS\\xc0@\\x96\\xedM\\x90\\x93S\\xc0@Q\\xfc\\'^\\xb2S\\xc0@\\x0c\\x0b\\x02,\\xd1S\\xc0@\\xc7\\x19\\xdc\\xf9\\xefS\\xc0@\\x81(\\xb6\\xc7\\x0eT\\xc0@<7\\x90\\x95-T\\xc0@\\xf8EjcLT\\xc0@\\xb3TD1kT\\xc0@nc\\x1e\\xff\\x89T\\xc0@)r\\xf8\\xcc\\xa8T\\xc0@\\xe3\\x80\\xd2\\x9a\\xc7T\\xc0@\\x9d\\x8f\\xach\\xe6T\\xc0@X\\x9e\\x866\\x05U\\xc0@\\x13\\xad`\\x04$U\\xc0@\\xce\\xbb:\\xd2BU\\xc0@\\x8a\\xca\\x14\\xa0aU\\xc0@E\\xd9\\xeem\\x80U\\xc0@\\x00\\xe8\\xc8;\\x9fU\\xc0@\\xbb\\xf6\\xa2\\t\\xbeU\\xc0@u\\x05}\\xd7\\xdcU\\xc0@0\\x14W\\xa5\\xfbU\\xc0@\\xeb\"1s\\x1aV\\xc0@\\xa61\\x0bA9V\\xc0@a@\\xe5\\x0eXV\\xc0@\\x1cO\\xbf\\xdcvV\\xc0@\\xd7]\\x99\\xaa\\x95V\\xc0@\\x92lsx\\xb4V\\xc0@L{MF\\xd3V\\xc0@\\x07\\x8a\\'\\x14\\xf2V\\xc0@\\xc2\\x98\\x01\\xe2\\x10W\\xc0@}\\xa7\\xdb\\xaf/W\\xc0@8\\xb6\\xb5}NW\\xc0@\\xf4\\xc4\\x8fKmW\\xc0@\\xaf\\xd3i\\x19\\x8cW\\xc0@i\\xe2C\\xe7\\xaaW\\xc0@$\\xf1\\x1d\\xb5\\xc9W\\xc0@\\xde\\xff\\xf7\\x82\\xe8W\\xc0@\\x99\\x0e\\xd2P\\x07X\\xc0@T\\x1d\\xac\\x1e&X\\xc0@\\x0f,\\x86\\xecDX\\xc0@\\xcb:`\\xbacX\\xc0@\\x86I:\\x88\\x82X\\xc0@@X\\x14V\\xa1X\\xc0@\\xfbf\\xee#\\xc0X\\xc0@\\xb6u\\xc8\\xf1\\xdeX\\xc0@q\\x84\\xa2\\xbf\\xfdX\\xc0@,\\x93|\\x8d\\x1cY\\xc0@\\xe7\\xa1V[;Y\\xc0@\\xa3\\xb00)ZY\\xc0@]\\xbf\\n\\xf7xY\\xc0@\\x17\\xce\\xe4\\xc4\\x97Y\\xc0@\\xd2\\xdc\\xbe\\x92\\xb6Y\\xc0@\\x8d\\xeb\\x98`\\xd5Y\\xc0@H\\xfar.\\xf4Y\\xc0@\\x03\\tM\\xfc\\x12Z\\xc0@\\xbe\\x17\\'\\xca1Z\\xc0@z&\\x01\\x98PZ\\xc0@45\\xdbeoZ\\xc0@\\xefC\\xb53\\x8eZ\\xc0@\\xaaR\\x8f\\x01\\xadZ\\xc0@eai\\xcf\\xcbZ\\xc0@ pC\\x9d\\xeaZ\\xc0@\\xdb~\\x1dk\\t[\\xc0@\\x95\\x8d\\xf78([\\xc0@P\\x9c\\xd1\\x06G[\\xc0@\\x0b\\xab\\xab\\xd4e[\\xc0@\\xc6\\xb9\\x85\\xa2\\x84[\\xc0@\\x81\\xc8_p\\xa3[\\xc0@<\\xd79>\\xc2[\\xc0@\\xf7\\xe5\\x13\\x0c\\xe1[\\xc0@\\xb2\\xf4\\xed\\xd9\\xff[\\xc0@m\\x03\\xc8\\xa7\\x1e\\\\\\xc0@\\'\\x12\\xa2u=\\\\\\xc0@\\xe3 |C\\\\\\\\\\xc0@\\x9e/V\\x11{\\\\\\xc0@Y>0\\xdf\\x99\\\\\\xc0@\\x14M\\n\\xad\\xb8\\\\\\xc0@\\xce[\\xe4z\\xd7\\\\\\xc0@\\x89j\\xbeH\\xf6\\\\\\xc0@Dy\\x98\\x16\\x15]\\xc0@\\xfe\\x87r\\xe43]\\xc0@\\xba\\x96L\\xb2R]\\xc0@u\\xa5&\\x80q]\\xc0@0\\xb4\\x00N\\x90]\\xc0@\\xeb\\xc2\\xda\\x1b\\xaf]\\xc0@\\xa6\\xd1\\xb4\\xe9\\xcd]\\xc0@a\\xe0\\x8e\\xb7\\xec]\\xc0@\\x1c\\xefh\\x85\\x0b^\\xc0@\\xd6\\xfdBS*^\\xc0@\\x91\\x0c\\x1d!I^\\xc0@L\\x1b\\xf7\\xeeg^\\xc0@\\x07*\\xd1\\xbc\\x86^\\xc0@\\xc28\\xab\\x8a\\xa5^\\xc0@}G\\x85X\\xc4^\\xc0@8V_&\\xe3^\\xc0@\\xf2d9\\xf4\\x01_\\xc0@\\xads\\x13\\xc2 _\\xc0@h\\x82\\xed\\x8f?_\\xc0@$\\x91\\xc7]^_\\xc0@\\xdf\\x9f\\xa1+}_\\xc0@\\x9a\\xae{\\xf9\\x9b_\\xc0@U\\xbdU\\xc7\\xba_\\xc0@\\x10\\xcc/\\x95\\xd9_\\xc0@\\xc9\\xda\\tc\\xf8_\\xc0@\\x84\\xe9\\xe30\\x17`\\xc0@?\\xf8\\xbd\\xfe5`\\xc0@\\xfb\\x06\\x98\\xccT`\\xc0@\\xb6\\x15r\\x9as`\\xc0@q$Lh\\x92`\\xc0@,3&6\\xb1`\\xc0@\\xe7A\\x00\\x04\\xd0`\\xc0@\\xa1P\\xda\\xd1\\xee`\\xc0@\\\\_\\xb4\\x9f\\ra\\xc0@\\x17n\\x8em,a\\xc0@\\xd2|h;Ka\\xc0@\\x8e\\x8bB\\tja\\xc0@I\\x9a\\x1c\\xd7\\x88a\\xc0@\\x03\\xa9\\xf6\\xa4\\xa7a\\xc0@\\xbd\\xb7\\xd0r\\xc6a\\xc0@x\\xc6\\xaa@\\xe5a\\xc0@3\\xd5\\x84\\x0e\\x04b\\xc0@\\xee\\xe3^\\xdc\"b\\xc0@\\xa9\\xf28\\xaaAb\\xc0@e\\x01\\x13x`b\\xc0@ \\x10\\xedE\\x7fb\\xc0@\\xdb\\x1e\\xc7\\x13\\x9eb\\xc0@\\x95-\\xa1\\xe1\\xbcb\\xc0@P<{\\xaf\\xdbb\\xc0@\\x0bKU}\\xfab\\xc0@\\xc6Y/K\\x19c\\xc0@\\x80h\\t\\x198c\\xc0@<w\\xe3\\xe6Vc\\xc0@\\xf7\\x85\\xbd\\xb4uc\\xc0@\\xb1\\x94\\x97\\x82\\x94c\\xc0@l\\xa3qP\\xb3c\\xc0@\\'\\xb2K\\x1e\\xd2c\\xc0@\\xe2\\xc0%\\xec\\xf0c\\xc0@\\x9d\\xcf\\xff\\xb9\\x0fd\\xc0@X\\xde\\xd9\\x87.d\\xc0@\\x13\\xed\\xb3UMd\\xc0@\\xcf\\xfb\\x8d#ld\\xc0@\\x89\\nh\\xf1\\x8ad\\xc0@D\\x19B\\xbf\\xa9d\\xc0@\\xff\\'\\x1c\\x8d\\xc8d\\xc0@\\xb96\\xf6Z\\xe7d\\xc0@tE\\xd0(\\x06e\\xc0@/T\\xaa\\xf6$e\\xc0@\\xeab\\x84\\xc4Ce\\xc0@\\xa6q^\\x92be\\xc0@`\\x808`\\x81e\\xc0@\\x1b\\x8f\\x12.\\xa0e\\xc0@\\xd6\\x9d\\xec\\xfb\\xbee\\xc0@\\x91\\xac\\xc6\\xc9\\xdde\\xc0@L\\xbb\\xa0\\x97\\xfce\\xc0@\\x07\\xcaze\\x1bf\\xc0@\\xc2\\xd8T3:f\\xc0@}\\xe7.\\x01Yf\\xc0@7\\xf6\\x08\\xcfwf\\xc0@\\xf2\\x04\\xe3\\x9c\\x96f\\xc0@\\xad\\x13\\xbdj\\xb5f\\xc0@h\"\\x978\\xd4f\\xc0@#1q\\x06\\xf3f\\xc0@\\xde?K\\xd4\\x11g\\xc0@\\x99N%\\xa20g\\xc0@S]\\xffoOg\\xc0@\\x0fl\\xd9=ng\\xc0@\\xcaz\\xb3\\x0b\\x8dg\\xc0@\\x85\\x89\\x8d\\xd9\\xabg\\xc0@@\\x98g\\xa7\\xcag\\xc0@\\xfb\\xa6Au\\xe9g\\xc0@\\xb5\\xb5\\x1bC\\x08h\\xc0@p\\xc4\\xf5\\x10\\'h\\xc0@*\\xd3\\xcf\\xdeEh\\xc0@\\xe6\\xe1\\xa9\\xacdh\\xc0@\\xa1\\xf0\\x83z\\x83h\\xc0@\\\\\\xff]H\\xa2h\\xc0@\\x17\\x0e8\\x16\\xc1h\\xc0@\\xd2\\x1c\\x12\\xe4\\xdfh\\xc0@\\x8d+\\xec\\xb1\\xfeh\\xc0@G:\\xc6\\x7f\\x1di\\xc0@\\x02I\\xa0M<i\\xc0@\\xbeWz\\x1b[i\\xc0@yfT\\xe9yi\\xc0@4u.\\xb7\\x98i\\xc0@\\xee\\x83\\x08\\x85\\xb7i\\xc0@\\xa9\\x92\\xe2R\\xd6i\\xc0@d\\xa1\\xbc \\xf5i\\xc0@\\x1e\\xb0\\x96\\xee\\x13j\\xc0@\\xd9\\xbep\\xbc2j\\xc0@\\x94\\xcdJ\\x8aQj\\xc0@P\\xdc$Xpj\\xc0@\\x0b\\xeb\\xfe%\\x8fj\\xc0@\\xc6\\xf9\\xd8\\xf3\\xadj\\xc0@\\x81\\x08\\xb3\\xc1\\xccj\\xc0@;\\x17\\x8d\\x8f\\xebj\\xc0@\\xf6%g]\\nk\\xc0@\\xb14A+)k\\xc0@kC\\x1b\\xf9Gk\\xc0@\\'R\\xf5\\xc6fk\\xc0@\\xe2`\\xcf\\x94\\x85k\\xc0@\\x9do\\xa9b\\xa4k\\xc0@X~\\x830\\xc3k\\xc0@\\x12\\x8d]\\xfe\\xe1k\\xc0@\\xcd\\x9b7\\xcc\\x00l\\xc0@\\x88\\xaa\\x11\\x9a\\x1fl\\xc0@C\\xb9\\xebg>l\\xc0@\\xff\\xc7\\xc55]l\\xc0@\\xba\\xd6\\x9f\\x03|l\\xc0@u\\xe5y\\xd1\\x9al\\xc0@0\\xf4S\\x9f\\xb9l\\xc0@\\xea\\x02.m\\xd8l\\xc0@\\xa4\\x11\\x08;\\xf7l\\xc0@_ \\xe2\\x08\\x16m\\xc0@\\x1a/\\xbc\\xd64m\\xc0@\\xd6=\\x96\\xa4Sm\\xc0@\\x91Lprrm\\xc0@L[J@\\x91m\\xc0@\\x06j$\\x0e\\xb0m\\xc0@\\xc1x\\xfe\\xdb\\xcem\\xc0@|\\x87\\xd8\\xa9\\xedm\\xc0@7\\x96\\xb2w\\x0cn\\xc0@\\xf2\\xa4\\x8cE+n\\xc0@\\xad\\xb3f\\x13Jn\\xc0@i\\xc2@\\xe1hn\\xc0@#\\xd1\\x1a\\xaf\\x87n\\xc0@\\xdd\\xdf\\xf4|\\xa6n\\xc0@\\x98\\xee\\xceJ\\xc5n\\xc0@S\\xfd\\xa8\\x18\\xe4n\\xc0@\\x0e\\x0c\\x83\\xe6\\x02o\\xc0@\\xc9\\x1a]\\xb4!o\\xc0@\\x84)7\\x82@o\\xc0@@8\\x11P_o\\xc0@\\xfbF\\xeb\\x1d~o\\xc0@\\xb5U\\xc5\\xeb\\x9co\\xc0@pd\\x9f\\xb9\\xbbo\\xc0@+sy\\x87\\xdao\\xc0@\\xe6\\x81SU\\xf9o\\xc0@\\xa0\\x90-#\\x18p\\xc0@[\\x9f\\x07\\xf16p\\xc0@\\x16\\xae\\xe1\\xbeUp\\xc0@\\xd1\\xbc\\xbb\\x8ctp\\xc0@\\x8c\\xcb\\x95Z\\x93p\\xc0@G\\xdao(\\xb2p\\xc0@\\x02\\xe9I\\xf6\\xd0p\\xc0@\\xbd\\xf7#\\xc4\\xefp\\xc0@x\\x06\\xfe\\x91\\x0eq\\xc0@3\\x15\\xd8_-q\\xc0@\\xee#\\xb2-Lq\\xc0@\\xa92\\x8c\\xfbjq\\xc0@dAf\\xc9\\x89q\\xc0@\\x1fP@\\x97\\xa8q\\xc0@\\xd9^\\x1ae\\xc7q\\xc0@\\x94m\\xf42\\xe6q\\xc0@O|\\xce\\x00\\x05r\\xc0@\\n\\x8b\\xa8\\xce#r\\xc0@\\xc4\\x99\\x82\\x9cBr\\xc0@\\x80\\xa8\\\\jar\\xc0@;\\xb768\\x80r\\xc0@\\xf6\\xc5\\x10\\x06\\x9fr\\xc0@\\xb1\\xd4\\xea\\xd3\\xbdr\\xc0@l\\xe3\\xc4\\xa1\\xdcr\\xc0@\\'\\xf2\\x9eo\\xfbr\\xc0@\\xe2\\x00y=\\x1as\\xc0@\\x9c\\x0fS\\x0b9s\\xc0@V\\x1e-\\xd9Ws\\xc0@\\x12-\\x07\\xa7vs\\xc0@\\xcd;\\xe1t\\x95s\\xc0@\\x88J\\xbbB\\xb4s\\xc0@CY\\x95\\x10\\xd3s\\xc0@\\xfego\\xde\\xf1s\\xc0@\\xb9vI\\xac\\x10t\\xc0@s\\x85#z/t\\xc0@.\\x94\\xfdGNt\\xc0@\\xea\\xa2\\xd7\\x15mt\\xc0@\\xa5\\xb1\\xb1\\xe3\\x8bt\\xc0@`\\xc0\\x8b\\xb1\\xaat\\xc0@\\x1b\\xcfe\\x7f\\xc9t\\xc0@\\xd6\\xdd?M\\xe8t\\xc0@\\x8f\\xec\\x19\\x1b\\x07u\\xc0@J\\xfb\\xf3\\xe8%u\\xc0@\\x05\\n\\xce\\xb6Du\\xc0@\\xc1\\x18\\xa8\\x84cu\\xc0@|\\'\\x82R\\x82u\\xc0@76\\\\ \\xa1u\\xc0@\\xf2D6\\xee\\xbfu\\xc0@\\xadS\\x10\\xbc\\xdeu\\xc0@gb\\xea\\x89\\xfdu\\xc0@\"q\\xc4W\\x1cv\\xc0@\\xdd\\x7f\\x9e%;v\\xc0@\\x98\\x8ex\\xf3Yv\\xc0@T\\x9dR\\xc1xv\\xc0@\\x0e\\xac,\\x8f\\x97v\\xc0@\\xc9\\xba\\x06]\\xb6v\\xc0@\\x84\\xc9\\xe0*\\xd5v\\xc0@>\\xd8\\xba\\xf8\\xf3v\\xc0@\\xf9\\xe6\\x94\\xc6\\x12w\\xc0@\\xb4\\xf5n\\x941w\\xc0@o\\x04IbPw\\xc0@+\\x13#0ow\\xc0@\\xe6!\\xfd\\xfd\\x8dw\\xc0@\\xa10\\xd7\\xcb\\xacw\\xc0@[?\\xb1\\x99\\xcbw\\xc0@\\x16N\\x8bg\\xeaw\\xc0@\\xd1\\\\e5\\tx\\xc0@\\x8bk?\\x03(x\\xc0@Fz\\x19\\xd1Fx\\xc0@\\x02\\x89\\xf3\\x9eex\\xc0@\\xbd\\x97\\xcdl\\x84x\\xc0@x\\xa6\\xa7:\\xa3x\\xc0@2\\xb5\\x81\\x08\\xc2x\\xc0@\\xed\\xc3[\\xd6\\xe0x\\xc0@\\xa8\\xd25\\xa4\\xffx\\xc0@c\\xe1\\x0fr\\x1ey\\xc0@\\x1e\\xf0\\xe9?=y\\xc0@\\xda\\xfe\\xc3\\r\\\\y\\xc0@\\x95\\r\\x9e\\xdbzy\\xc0@O\\x1cx\\xa9\\x99y\\xc0@\\n+Rw\\xb8y\\xc0@\\xc49,E\\xd7y\\xc0@\\x7fH\\x06\\x13\\xf6y\\xc0@:W\\xe0\\xe0\\x14z\\xc0@\\xf5e\\xba\\xae3z\\xc0@\\xb0t\\x94|Rz\\xc0@l\\x83nJqz\\xc0@&\\x92H\\x18\\x90z\\xc0@\\xe1\\xa0\"\\xe6\\xaez\\xc0@\\x9c\\xaf\\xfc\\xb3\\xcdz\\xc0@W\\xbe\\xd6\\x81\\xecz\\xc0@\\x12\\xcd\\xb0O\\x0b{\\xc0@\\xcd\\xdb\\x8a\\x1d*{\\xc0@\\x88\\xead\\xebH{\\xc0@C\\xf9>\\xb9g{\\xc0@\\xfd\\x07\\x19\\x87\\x86{\\xc0@\\xb8\\x16\\xf3T\\xa5{\\xc0@s%\\xcd\"\\xc4{\\xc0@.4\\xa7\\xf0\\xe2{\\xc0@\\xe9B\\x81\\xbe\\x01|\\xc0@\\xa4Q[\\x8c |\\xc0@_`5Z?|\\xc0@\\x1ao\\x0f(^|\\xc0@\\xd5}\\xe9\\xf5||\\xc0@\\x90\\x8c\\xc3\\xc3\\x9b|\\xc0@K\\x9b\\x9d\\x91\\xba|\\xc0@\\x06\\xaaw_\\xd9|\\xc0@\\xc0\\xb8Q-\\xf8|\\xc0@{\\xc7+\\xfb\\x16}\\xc0@6\\xd6\\x05\\xc95}\\xc0@\\xf0\\xe4\\xdf\\x96T}\\xc0@\\xac\\xf3\\xb9ds}\\xc0@g\\x02\\x942\\x92}\\xc0@\"\\x11n\\x00\\xb1}\\xc0@\\xdd\\x1fH\\xce\\xcf}\\xc0@\\x98.\"\\x9c\\xee}\\xc0@S=\\xfci\\r~\\xc0@\\rL\\xd67,~\\xc0@\\xc8Z\\xb0\\x05K~\\xc0@\\x84i\\x8a\\xd3i~\\xc0@?xd\\xa1\\x88~\\xc0@\\xf9\\x86>o\\xa7~\\xc0@\\xb4\\x95\\x18=\\xc6~\\xc0@o\\xa4\\xf2\\n\\xe5~\\xc0@*\\xb3\\xcc\\xd8\\x03\\x7f\\xc0@\\xe4\\xc1\\xa6\\xa6\"\\x7f\\xc0@\\x9f\\xd0\\x80tA\\x7f\\xc0@Z\\xdfZB`\\x7f\\xc0@\\x16\\xee4\\x10\\x7f\\x7f\\xc0@\\xd1\\xfc\\x0e\\xde\\x9d\\x7f\\xc0@\\x8c\\x0b\\xe9\\xab\\xbc\\x7f\\xc0@G\\x1a\\xc3y\\xdb\\x7f\\xc0@\\x02)\\x9dG\\xfa\\x7f\\xc0@\\xbc7w\\x15\\x19\\x80\\xc0@vFQ\\xe37\\x80\\xc0@1U+\\xb1V\\x80\\xc0@\\xedc\\x05\\x7fu\\x80\\xc0@\\xa8r\\xdfL\\x94\\x80\\xc0@c\\x81\\xb9\\x1a\\xb3\\x80\\xc0@\\x1e\\x90\\x93\\xe8\\xd1\\x80\\xc0@\\xd8\\x9em\\xb6\\xf0\\x80\\xc0@\\x93\\xadG\\x84\\x0f\\x81\\xc0@N\\xbc!R.\\x81\\xc0@\\t\\xcb\\xfb\\x1fM\\x81\\xc0@\\xc5\\xd9\\xd5\\xedk\\x81\\xc0@\\x80\\xe8\\xaf\\xbb\\x8a\\x81\\xc0@;\\xf7\\x89\\x89\\xa9\\x81\\xc0@\\xf6\\x05dW\\xc8\\x81\\xc0@\\xaf\\x14>%\\xe7\\x81\\xc0@j#\\x18\\xf3\\x05\\x82\\xc0@%2\\xf2\\xc0$\\x82\\xc0@\\xe0@\\xcc\\x8eC\\x82\\xc0@\\x9cO\\xa6\\\\b\\x82\\xc0@W^\\x80*\\x81\\x82\\xc0@\\x12mZ\\xf8\\x9f\\x82\\xc0@\\xcd{4\\xc6\\xbe\\x82\\xc0@\\x87\\x8a\\x0e\\x94\\xdd\\x82\\xc0@B\\x99\\xe8a\\xfc\\x82\\xc0@\\xfd\\xa7\\xc2/\\x1b\\x83\\xc0@\\xb8\\xb6\\x9c\\xfd9\\x83\\xc0@s\\xc5v\\xcbX\\x83\\xc0@.\\xd4P\\x99w\\x83\\xc0@\\xe9\\xe2*g\\x96\\x83\\xc0@\\xa3\\xf1\\x045\\xb5\\x83\\xc0@^\\x00\\xdf\\x02\\xd4\\x83\\xc0@\\x19\\x0f\\xb9\\xd0\\xf2\\x83\\xc0@\\xd4\\x1d\\x93\\x9e\\x11\\x84\\xc0@\\x8f,ml0\\x84\\xc0@J;G:O\\x84\\xc0@\\x06J!\\x08n\\x84\\xc0@\\xc1X\\xfb\\xd5\\x8c\\x84\\xc0@{g\\xd5\\xa3\\xab\\x84\\xc0@6v\\xafq\\xca\\x84\\xc0@\\xf1\\x84\\x89?\\xe9\\x84\\xc0@\\xab\\x93c\\r\\x08\\x85\\xc0@f\\xa2=\\xdb&\\x85\\xc0@!\\xb1\\x17\\xa9E\\x85\\xc0@\\xdd\\xbf\\xf1vd\\x85\\xc0@\\x98\\xce\\xcbD\\x83\\x85\\xc0@R\\xdd\\xa5\\x12\\xa2\\x85\\xc0@\\r\\xec\\x7f\\xe0\\xc0\\x85\\xc0@\\xc8\\xfaY\\xae\\xdf\\x85\\xc0@\\x83\\t4|\\xfe\\x85\\xc0@>\\x18\\x0eJ\\x1d\\x86\\xc0@\\xf9&\\xe8\\x17<\\x86\\xc0@\\xb45\\xc2\\xe5Z\\x86\\xc0@oD\\x9c\\xb3y\\x86\\xc0@*Sv\\x81\\x98\\x86\\xc0@\\xe4aPO\\xb7\\x86\\xc0@\\x9fp*\\x1d\\xd6\\x86\\xc0@Z\\x7f\\x04\\xeb\\xf4\\x86\\xc0@\\x15\\x8e\\xde\\xb8\\x13\\x87\\xc0@\\xd0\\x9c\\xb8\\x862\\x87\\xc0@\\x8b\\xab\\x92TQ\\x87\\xc0@F\\xbal\"p\\x87\\xc0@\\x01\\xc9F\\xf0\\x8e\\x87\\xc0@\\xbc\\xd7 \\xbe\\xad\\x87\\xc0@w\\xe6\\xfa\\x8b\\xcc\\x87\\xc0@2\\xf5\\xd4Y\\xeb\\x87\\xc0@\\xed\\x03\\xaf\\'\\n\\x88\\xc0@\\xa8\\x12\\x89\\xf5(\\x88\\xc0@a!c\\xc3G\\x88\\xc0@\\x1c0=\\x91f\\x88\\xc0@\\xd8>\\x17_\\x85\\x88\\xc0@\\x93M\\xf1,\\xa4\\x88\\xc0@N\\\\\\xcb\\xfa\\xc2\\x88\\xc0@\\tk\\xa5\\xc8\\xe1\\x88\\xc0@\\xc4y\\x7f\\x96\\x00\\x89\\xc0@\\x7f\\x88Yd\\x1f\\x89\\xc0@9\\x9732>\\x89\\xc0@\\xf4\\xa5\\r\\x00]\\x89\\xc0@\\xb0\\xb4\\xe7\\xcd{\\x89\\xc0@k\\xc3\\xc1\\x9b\\x9a\\x89\\xc0@&\\xd2\\x9bi\\xb9\\x89\\xc0@\\xe1\\xe0u7\\xd8\\x89\\xc0@\\x9b\\xefO\\x05\\xf7\\x89\\xc0@V\\xfe)\\xd3\\x15\\x8a\\xc0@\\x10\\r\\x04\\xa14\\x8a\\xc0@\\xcb\\x1b\\xdenS\\x8a\\xc0@\\x87*\\xb8<r\\x8a\\xc0@B9\\x92\\n\\x91\\x8a\\xc0@\\xfdGl\\xd8\\xaf\\x8a\\xc0@\\xb8VF\\xa6\\xce\\x8a\\xc0@se t\\xed\\x8a\\xc0@-t\\xfaA\\x0c\\x8b\\xc0@\\xe8\\x82\\xd4\\x0f+\\x8b\\xc0@\\xa3\\x91\\xae\\xddI\\x8b\\xc0@^\\xa0\\x88\\xabh\\x8b\\xc0@\\x19\\xafby\\x87\\x8b\\xc0@\\xd4\\xbd<G\\xa6\\x8b\\xc0@\\x8f\\xcc\\x16\\x15\\xc5\\x8b\\xc0@J\\xdb\\xf0\\xe2\\xe3\\x8b\\xc0@\\x04\\xea\\xca\\xb0\\x02\\x8c\\xc0@\\xbf\\xf8\\xa4~!\\x8c\\xc0@z\\x07\\x7fL@\\x8c\\xc0@5\\x16Y\\x1a_\\x8c\\xc0@\\xf1$3\\xe8}\\x8c\\xc0@\\xac3\\r\\xb6\\x9c\\x8c\\xc0@gB\\xe7\\x83\\xbb\\x8c\\xc0@!Q\\xc1Q\\xda\\x8c\\xc0@\\xdc_\\x9b\\x1f\\xf9\\x8c\\xc0@\\x96nu\\xed\\x17\\x8d\\xc0@Q}O\\xbb6\\x8d\\xc0@\\x0c\\x8c)\\x89U\\x8d\\xc0@\\xc8\\x9a\\x03Wt\\x8d\\xc0@\\x83\\xa9\\xdd$\\x93\\x8d\\xc0@>\\xb8\\xb7\\xf2\\xb1\\x8d\\xc0@\\xf8\\xc6\\x91\\xc0\\xd0\\x8d\\xc0@\\xb3\\xd5k\\x8e\\xef\\x8d\\xc0@n\\xe4E\\\\\\x0e\\x8e\\xc0@)\\xf3\\x1f*-\\x8e\\xc0@\\xe4\\x01\\xfa\\xf7K\\x8e\\xc0@\\xa0\\x10\\xd4\\xc5j\\x8e\\xc0@[\\x1f\\xae\\x93\\x89\\x8e\\xc0@\\x16.\\x88a\\xa8\\x8e\\xc0@\\xcf<b/\\xc7\\x8e\\xc0@\\x8aK<\\xfd\\xe5\\x8e\\xc0@EZ\\x16\\xcb\\x04\\x8f\\xc0@\\x00i\\xf0\\x98#\\x8f\\xc0@\\xbbw\\xcafB\\x8f\\xc0@v\\x86\\xa44a\\x8f\\xc0@2\\x95~\\x02\\x80\\x8f\\xc0@\\xec\\xa3X\\xd0\\x9e\\x8f\\xc0@\\xa7\\xb22\\x9e\\xbd\\x8f\\xc0@b\\xc1\\x0cl\\xdc\\x8f\\xc0@\\x1d\\xd0\\xe69\\xfb\\x8f\\xc0@\\xd8\\xde\\xc0\\x07\\x1a\\x90\\xc0@\\x93\\xed\\x9a\\xd58\\x90\\xc0@M\\xfct\\xa3W\\x90\\xc0@\\t\\x0bOqv\\x90\\xc0@\\xc3\\x19)?\\x95\\x90\\xc0@~(\\x03\\r\\xb4\\x90\\xc0@97\\xdd\\xda\\xd2\\x90\\xc0@\\xf4E\\xb7\\xa8\\xf1\\x90\\xc0@\\xafT\\x91v\\x10\\x91\\xc0@jckD/\\x91\\xc0@%rE\\x12N\\x91\\xc0@\\xe1\\x80\\x1f\\xe0l\\x91\\xc0@\\x9b\\x8f\\xf9\\xad\\x8b\\x91\\xc0@V\\x9e\\xd3{\\xaa\\x91\\xc0@\\x11\\xad\\xadI\\xc9\\x91\\xc0@\\xcc\\xbb\\x87\\x17\\xe8\\x91\\xc0@\\x86\\xcaa\\xe5\\x06\\x92\\xc0@A\\xd9;\\xb3%\\x92\\xc0@\\xfc\\xe7\\x15\\x81D\\x92\\xc0@\\xb6\\xf6\\xefNc\\x92\\xc0@r\\x05\\xca\\x1c\\x82\\x92\\xc0@-\\x14\\xa4\\xea\\xa0\\x92\\xc0@\\xe8\"~\\xb8\\xbf\\x92\\xc0@\\xa31X\\x86\\xde\\x92\\xc0@^@2T\\xfd\\x92\\xc0@\\x19O\\x0c\"\\x1c\\x93\\xc0@\\xd4]\\xe6\\xef:\\x93\\xc0@\\x8el\\xc0\\xbdY\\x93\\xc0@J{\\x9a\\x8bx\\x93\\xc0@\\x04\\x8atY\\x97\\x93\\xc0@\\xbf\\x98N\\'\\xb6\\x93\\xc0@z\\xa7(\\xf5\\xd4\\x93\\xc0@5\\xb6\\x02\\xc3\\xf3\\x93\\xc0@\\xf0\\xc4\\xdc\\x90\\x12\\x94\\xc0@\\xab\\xd3\\xb6^1\\x94\\xc0@e\\xe2\\x90,P\\x94\\xc0@!\\xf1j\\xfan\\x94\\xc0@\\xdc\\xffD\\xc8\\x8d\\x94\\xc0@\\x97\\x0e\\x1f\\x96\\xac\\x94\\xc0@R\\x1d\\xf9c\\xcb\\x94\\xc0@\\r,\\xd31\\xea\\x94\\xc0@\\xc8:\\xad\\xff\\x08\\x95\\xc0@\\x81I\\x87\\xcd\\'\\x95\\xc0@<Xa\\x9bF\\x95\\xc0@\\xf8f;ie\\x95\\xc0@\\xb3u\\x157\\x84\\x95\\xc0@n\\x84\\xef\\x04\\xa3\\x95\\xc0@)\\x93\\xc9\\xd2\\xc1\\x95\\xc0@\\xe4\\xa1\\xa3\\xa0\\xe0\\x95\\xc0@\\x9f\\xb0}n\\xff\\x95\\xc0@Y\\xbfW<\\x1e\\x96\\xc0@\\x14\\xce1\\n=\\x96\\xc0@\\xcf\\xdc\\x0b\\xd8[\\x96\\xc0@\\x8b\\xeb\\xe5\\xa5z\\x96\\xc0@F\\xfa\\xbfs\\x99\\x96\\xc0@\\x01\\t\\x9aA\\xb8\\x96\\xc0@\\xbb\\x17t\\x0f\\xd7\\x96\\xc0@u&N\\xdd\\xf5\\x96\\xc0@05(\\xab\\x14\\x97\\xc0@\\xebC\\x02y3\\x97\\xc0@\\xa6R\\xdcFR\\x97\\xc0@ba\\xb6\\x14q\\x97\\xc0@\\x1dp\\x90\\xe2\\x8f\\x97\\xc0@\\xd8~j\\xb0\\xae\\x97\\xc0@\\x93\\x8dD~\\xcd\\x97\\xc0@M\\x9c\\x1eL\\xec\\x97\\xc0@\\x08\\xab\\xf8\\x19\\x0b\\x98\\xc0@\\xc3\\xb9\\xd2\\xe7)\\x98\\xc0@~\\xc8\\xac\\xb5H\\x98\\xc0@8\\xd7\\x86\\x83g\\x98\\xc0@\\xf4\\xe5`Q\\x86\\x98\\xc0@\\xaf\\xf4:\\x1f\\xa5\\x98\\xc0@j\\x03\\x15\\xed\\xc3\\x98\\xc0@$\\x12\\xef\\xba\\xe2\\x98\\xc0@\\xdf \\xc9\\x88\\x01\\x99\\xc0@\\x9a/\\xa3V \\x99\\xc0@U>}$?\\x99\\xc0@\\x10MW\\xf2]\\x99\\xc0@\\xcc[1\\xc0|\\x99\\xc0@\\x87j\\x0b\\x8e\\x9b\\x99\\xc0@Ay\\xe5[\\xba\\x99\\xc0@\\xfc\\x87\\xbf)\\xd9\\x99\\xc0@\\xb7\\x96\\x99\\xf7\\xf7\\x99\\xc0@q\\xa5s\\xc5\\x16\\x9a\\xc0@,\\xb4M\\x935\\x9a\\xc0@\\xe7\\xc2\\'aT\\x9a\\xc0@\\xa3\\xd1\\x01/s\\x9a\\xc0@^\\xe0\\xdb\\xfc\\x91\\x9a\\xc0@\\x18\\xef\\xb5\\xca\\xb0\\x9a\\xc0@\\xd3\\xfd\\x8f\\x98\\xcf\\x9a\\xc0@\\x8e\\x0cjf\\xee\\x9a\\xc0@I\\x1bD4\\r\\x9b\\xc0@\\x04*\\x1e\\x02,\\x9b\\xc0@\\xbf8\\xf8\\xcfJ\\x9b\\xc0@zG\\xd2\\x9di\\x9b\\xc0@5V\\xack\\x88\\x9b\\xc0@\\xefd\\x869\\xa7\\x9b\\xc0@\\xaas`\\x07\\xc6\\x9b\\xc0@e\\x82:\\xd5\\xe4\\x9b\\xc0@ \\x91\\x14\\xa3\\x03\\x9c\\xc0@\\xdb\\x9f\\xeep\"\\x9c\\xc0@\\x96\\xae\\xc8>A\\x9c\\xc0@Q\\xbd\\xa2\\x0c`\\x9c\\xc0@\\x0c\\xcc|\\xda~\\x9c\\xc0@\\xc7\\xdaV\\xa8\\x9d\\x9c\\xc0@\\x82\\xe90v\\xbc\\x9c\\xc0@=\\xf8\\nD\\xdb\\x9c\\xc0@\\xf8\\x06\\xe5\\x11\\xfa\\x9c\\xc0@\\xb3\\x15\\xbf\\xdf\\x18\\x9d\\xc0@m$\\x99\\xad7\\x9d\\xc0@(3s{V\\x9d\\xc0@\\xe3AMIu\\x9d\\xc0@\\x9eP\\'\\x17\\x94\\x9d\\xc0@Y_\\x01\\xe5\\xb2\\x9d\\xc0@\\x14n\\xdb\\xb2\\xd1\\x9d\\xc0@\\xcf|\\xb5\\x80\\xf0\\x9d\\xc0@\\x8a\\x8b\\x8fN\\x0f\\x9e\\xc0@E\\x9ai\\x1c.\\x9e\\xc0@\\xff\\xa8C\\xeaL\\x9e\\xc0@\\xba\\xb7\\x1d\\xb8k\\x9e\\xc0@v\\xc6\\xf7\\x85\\x8a\\x9e\\xc0@1\\xd5\\xd1S\\xa9\\x9e\\xc0@\\xec\\xe3\\xab!\\xc8\\x9e\\xc0@\\xa6\\xf2\\x85\\xef\\xe6\\x9e\\xc0@a\\x01`\\xbd\\x05\\x9f\\xc0@\\x1c\\x10:\\x8b$\\x9f\\xc0@\\xd6\\x1e\\x14YC\\x9f\\xc0@\\x91-\\xee&b\\x9f\\xc0@M<\\xc8\\xf4\\x80\\x9f\\xc0@\\x08K\\xa2\\xc2\\x9f\\x9f\\xc0@\\xc3Y|\\x90\\xbe\\x9f\\xc0@~hV^\\xdd\\x9f\\xc0@9w0,\\xfc\\x9f\\xc0@\\xf4\\x85\\n\\xfa\\x1a\\xa0\\xc0@\\xae\\x94\\xe4\\xc79\\xa0\\xc0@i\\xa3\\xbe\\x95X\\xa0\\xc0@$\\xb2\\x98cw\\xa0\\xc0@\\xdf\\xc0r1\\x96\\xa0\\xc0@\\x9a\\xcfL\\xff\\xb4\\xa0\\xc0@U\\xde&\\xcd\\xd3\\xa0\\xc0@\\x10\\xed\\x00\\x9b\\xf2\\xa0\\xc0@\\xca\\xfb\\xdah\\x11\\xa1\\xc0@\\x85\\n\\xb560\\xa1\\xc0@@\\x19\\x8f\\x04O\\xa1\\xc0@\\xfc\\'i\\xd2m\\xa1\\xc0@\\xb76C\\xa0\\x8c\\xa1\\xc0@rE\\x1dn\\xab\\xa1\\xc0@-T\\xf7;\\xca\\xa1\\xc0@\\xe8b\\xd1\\t\\xe9\\xa1\\xc0@\\xa2q\\xab\\xd7\\x07\\xa2\\xc0@\\\\\\x80\\x85\\xa5&\\xa2\\xc0@\\x17\\x8f_sE\\xa2\\xc0@\\xd2\\x9d9Ad\\xa2\\xc0@\\x8e\\xac\\x13\\x0f\\x83\\xa2\\xc0@I\\xbb\\xed\\xdc\\xa1\\xa2\\xc0@\\x04\\xca\\xc7\\xaa\\xc0\\xa2\\xc0@\\xbe\\xd8\\xa1x\\xdf\\xa2\\xc0@y\\xe7{F\\xfe\\xa2\\xc0@4\\xf6U\\x14\\x1d\\xa3\\xc0@\\xef\\x040\\xe2;\\xa3\\xc0@\\xaa\\x13\\n\\xb0Z\\xa3\\xc0@f\"\\xe4}y\\xa3\\xc0@!1\\xbeK\\x98\\xa3\\xc0@\\xdb?\\x98\\x19\\xb7\\xa3\\xc0@\\x95Nr\\xe7\\xd5\\xa3\\xc0@P]L\\xb5\\xf4\\xa3\\xc0@\\x0bl&\\x83\\x13\\xa4\\xc0@\\xc6z\\x00Q2\\xa4\\xc0@\\x81\\x89\\xda\\x1eQ\\xa4\\xc0@<\\x98\\xb4\\xeco\\xa4\\xc0@\\xf8\\xa6\\x8e\\xba\\x8e\\xa4\\xc0@\\xb3\\xb5h\\x88\\xad\\xa4\\xc0@m\\xc4BV\\xcc\\xa4\\xc0@(\\xd3\\x1c$\\xeb\\xa4\\xc0@\\xe3\\xe1\\xf6\\xf1\\t\\xa5\\xc0@\\x9e\\xf0\\xd0\\xbf(\\xa5\\xc0@X\\xff\\xaa\\x8dG\\xa5\\xc0@\\x13\\x0e\\x85[f\\xa5\\xc0@\\xcf\\x1c_)\\x85\\xa5\\xc0@\\x89+9\\xf7\\xa3\\xa5\\xc0@D:\\x13\\xc5\\xc2\\xa5\\xc0@\\xffH\\xed\\x92\\xe1\\xa5\\xc0@\\xbaW\\xc7`\\x00\\xa6\\xc0@uf\\xa1.\\x1f\\xa6\\xc0@0u{\\xfc=\\xa6\\xc0@\\xeb\\x83U\\xca\\\\\\xa6\\xc0@\\xa7\\x92/\\x98{\\xa6\\xc0@a\\xa1\\tf\\x9a\\xa6\\xc0@\\x1c\\xb0\\xe33\\xb9\\xa6\\xc0@\\xd7\\xbe\\xbd\\x01\\xd8\\xa6\\xc0@\\x91\\xcd\\x97\\xcf\\xf6\\xa6\\xc0@L\\xdcq\\x9d\\x15\\xa7\\xc0@\\x07\\xebKk4\\xa7\\xc0@\\xc2\\xf9%9S\\xa7\\xc0@~\\x08\\x00\\x07r\\xa7\\xc0@8\\x17\\xda\\xd4\\x90\\xa7\\xc0@\\xf3%\\xb4\\xa2\\xaf\\xa7\\xc0@\\xae4\\x8ep\\xce\\xa7\\xc0@iCh>\\xed\\xa7\\xc0@$RB\\x0c\\x0c\\xa8\\xc0@\\xdf`\\x1c\\xda*\\xa8\\xc0@\\x9ao\\xf6\\xa7I\\xa8\\xc0@T~\\xd0uh\\xa8\\xc0@\\x0f\\x8d\\xaaC\\x87\\xa8\\xc0@\\xca\\x9b\\x84\\x11\\xa6\\xa8\\xc0@\\x85\\xaa^\\xdf\\xc4\\xa8\\xc0@@\\xb98\\xad\\xe3\\xa8\\xc0@\\xfb\\xc7\\x12{\\x02\\xa9\\xc0@\\xb6\\xd6\\xecH!\\xa9\\xc0@q\\xe5\\xc6\\x16@\\xa9\\xc0@+\\xf4\\xa0\\xe4^\\xa9\\xc0@\\xe7\\x02{\\xb2}\\xa9\\xc0@\\xa2\\x11U\\x80\\x9c\\xa9\\xc0@] /N\\xbb\\xa9\\xc0@\\x18/\\t\\x1c\\xda\\xa9\\xc0@\\xd3=\\xe3\\xe9\\xf8\\xa9\\xc0@\\x8dL\\xbd\\xb7\\x17\\xaa\\xc0@H[\\x97\\x856\\xaa\\xc0@\\x02jqSU\\xaa\\xc0@\\xbexK!t\\xaa\\xc0@y\\x87%\\xef\\x92\\xaa\\xc0@4\\x96\\xff\\xbc\\xb1\\xaa\\xc0@\\xef\\xa4\\xd9\\x8a\\xd0\\xaa\\xc0@\\xaa\\xb3\\xb3X\\xef\\xaa\\xc0@e\\xc2\\x8d&\\x0e\\xab\\xc0@\\x1f\\xd1g\\xf4,\\xab\\xc0@\\xda\\xdfA\\xc2K\\xab\\xc0@\\x96\\xee\\x1b\\x90j\\xab\\xc0@Q\\xfd\\xf5]\\x89\\xab\\xc0@\\x0c\\x0c\\xd0+\\xa8\\xab\\xc0@\\xc6\\x1a\\xaa\\xf9\\xc6\\xab\\xc0@\\x81)\\x84\\xc7\\xe5\\xab\\xc0@<8^\\x95\\x04\\xac\\xc0@\\xf6F8c#\\xac\\xc0@\\xb1U\\x121B\\xac\\xc0@ld\\xec\\xfe`\\xac\\xc0@(s\\xc6\\xcc\\x7f\\xac\\xc0@\\xe3\\x81\\xa0\\x9a\\x9e\\xac\\xc0@\\x9e\\x90zh\\xbd\\xac\\xc0@Y\\x9fT6\\xdc\\xac\\xc0@\\x13\\xae.\\x04\\xfb\\xac\\xc0@\\xce\\xbc\\x08\\xd2\\x19\\xad\\xc0@\\x89\\xcb\\xe2\\x9f8\\xad\\xc0@C\\xda\\xbcmW\\xad\\xc0@\\xfe\\xe8\\x96;v\\xad\\xc0@\\xba\\xf7p\\t\\x95\\xad\\xc0@u\\x06K\\xd7\\xb3\\xad\\xc0@0\\x15%\\xa5\\xd2\\xad\\xc0@\\xea#\\xffr\\xf1\\xad\\xc0@\\xa52\\xd9@\\x10\\xae\\xc0@`A\\xb3\\x0e/\\xae\\xc0@\\x1bP\\x8d\\xdcM\\xae\\xc0@\\xd6^g\\xaal\\xae\\xc0@\\x92mAx\\x8b\\xae\\xc0@M|\\x1bF\\xaa\\xae\\xc0@\\x08\\x8b\\xf5\\x13\\xc9\\xae\\xc0@\\xc2\\x99\\xcf\\xe1\\xe7\\xae\\xc0@|\\xa8\\xa9\\xaf\\x06\\xaf\\xc0@7\\xb7\\x83}%\\xaf\\xc0@\\xf2\\xc5]KD\\xaf\\xc0@\\xad\\xd47\\x19c\\xaf\\xc0@i\\xe3\\x11\\xe7\\x81\\xaf\\xc0@$\\xf2\\xeb\\xb4\\xa0\\xaf\\xc0@\\xde\\x00\\xc6\\x82\\xbf\\xaf\\xc0@\\x99\\x0f\\xa0P\\xde\\xaf\\xc0@T\\x1ez\\x1e\\xfd\\xaf\\xc0@\\x0f-T\\xec\\x1b\\xb0\\xc0@\\xca;.\\xba:\\xb0\\xc0@\\x85J\\x08\\x88Y\\xb0\\xc0@@Y\\xe2Ux\\xb0\\xc0@\\xfbg\\xbc#\\x97\\xb0\\xc0@\\xb5v\\x96\\xf1\\xb5\\xb0\\xc0@p\\x85p\\xbf\\xd4\\xb0\\xc0@+\\x94J\\x8d\\xf3\\xb0\\xc0@\\xe6\\xa2$[\\x12\\xb1\\xc0@\\xa1\\xb1\\xfe(1\\xb1\\xc0@\\\\\\xc0\\xd8\\xf6O\\xb1\\xc0@\\x17\\xcf\\xb2\\xc4n\\xb1\\xc0@\\xd2\\xdd\\x8c\\x92\\x8d\\xb1\\xc0@\\x8d\\xecf`\\xac\\xb1\\xc0@H\\xfb@.\\xcb\\xb1\\xc0@\\x03\\n\\x1b\\xfc\\xe9\\xb1\\xc0@\\xbe\\x18\\xf5\\xc9\\x08\\xb2\\xc0@x\\'\\xcf\\x97\\'\\xb2\\xc0@36\\xa9eF\\xb2\\xc0@\\xeeD\\x833e\\xb2\\xc0@\\xa9S]\\x01\\x84\\xb2\\xc0@db7\\xcf\\xa2\\xb2\\xc0@\\x1fq\\x11\\x9d\\xc1\\xb2\\xc0@\\xda\\x7f\\xebj\\xe0\\xb2\\xc0@\\x95\\x8e\\xc58\\xff\\xb2\\xc0@P\\x9d\\x9f\\x06\\x1e\\xb3\\xc0@\\x0b\\xacy\\xd4<\\xb3\\xc0@\\xc6\\xbaS\\xa2[\\xb3\\xc0@\\x81\\xc9-pz\\xb3\\xc0@<\\xd8\\x07>\\x99\\xb3\\xc0@\\xf7\\xe6\\xe1\\x0b\\xb8\\xb3\\xc0@\\xb1\\xf5\\xbb\\xd9\\xd6\\xb3\\xc0@l\\x04\\x96\\xa7\\xf5\\xb3\\xc0@\\'\\x13pu\\x14\\xb4\\xc0@\\xe2!JC3\\xb4\\xc0@\\x9c0$\\x11R\\xb4\\xc0@W?\\xfe\\xdep\\xb4\\xc0@\\x13N\\xd8\\xac\\x8f\\xb4\\xc0@\\xce\\\\\\xb2z\\xae\\xb4\\xc0@\\x89k\\x8cH\\xcd\\xb4\\xc0@Dzf\\x16\\xec\\xb4\\xc0@\\xff\\x88@\\xe4\\n\\xb5\\xc0@\\xba\\x97\\x1a\\xb2)\\xb5\\xc0@t\\xa6\\xf4\\x7fH\\xb5\\xc0@.\\xb5\\xceMg\\xb5\\xc0@\\xea\\xc3\\xa8\\x1b\\x86\\xb5\\xc0@\\xa5\\xd2\\x82\\xe9\\xa4\\xb5\\xc0@`\\xe1\\\\\\xb7\\xc3\\xb5\\xc0@\\x1b\\xf06\\x85\\xe2\\xb5\\xc0@\\xd6\\xfe\\x10S\\x01\\xb6\\xc0@\\x91\\r\\xeb  \\xb6\\xc0@K\\x1c\\xc5\\xee>\\xb6\\xc0@\\x06+\\x9f\\xbc]\\xb6\\xc0@\\xc29y\\x8a|\\xb6\\xc0@}HSX\\x9b\\xb6\\xc0@8W-&\\xba\\xb6\\xc0@\\xf3e\\x07\\xf4\\xd8\\xb6\\xc0@\\xaet\\xe1\\xc1\\xf7\\xb6\\xc0@g\\x83\\xbb\\x8f\\x16\\xb7\\xc0@\"\\x92\\x95]5\\xb7\\xc0@\\xdd\\xa0o+T\\xb7\\xc0@\\x98\\xafI\\xf9r\\xb7\\xc0@T\\xbe#\\xc7\\x91\\xb7\\xc0@\\x0f\\xcd\\xfd\\x94\\xb0\\xb7\\xc0@\\xca\\xdb\\xd7b\\xcf\\xb7\\xc0@\\x85\\xea\\xb10\\xee\\xb7\\xc0@?\\xf9\\x8b\\xfe\\x0c\\xb8\\xc0@\\xfa\\x07f\\xcc+\\xb8\\xc0@\\xb5\\x16@\\x9aJ\\xb8\\xc0@p%\\x1ahi\\xb8\\xc0@,4\\xf45\\x88\\xb8\\xc0@\\xe6B\\xce\\x03\\xa7\\xb8\\xc0@\\xa1Q\\xa8\\xd1\\xc5\\xb8\\xc0@\\\\`\\x82\\x9f\\xe4\\xb8\\xc0@\\x16o\\\\m\\x03\\xb9\\xc0@\\xd1}6;\"\\xb9\\xc0@\\x8c\\x8c\\x10\\tA\\xb9\\xc0@G\\x9b\\xea\\xd6_\\xb9\\xc0@\\x03\\xaa\\xc4\\xa4~\\xb9\\xc0@\\xbe\\xb8\\x9er\\x9d\\xb9\\xc0@y\\xc7x@\\xbc\\xb9\\xc0@3\\xd6R\\x0e\\xdb\\xb9\\xc0@\\xee\\xe4,\\xdc\\xf9\\xb9\\xc0@\\xa9\\xf3\\x06\\xaa\\x18\\xba\\xc0@c\\x02\\xe1w7\\xba\\xc0@\\x1e\\x11\\xbbEV\\xba\\xc0@\\xda\\x1f\\x95\\x13u\\xba\\xc0@\\x95.o\\xe1\\x93\\xba\\xc0@P=I\\xaf\\xb2\\xba\\xc0@\\nL#}\\xd1\\xba\\xc0@\\xc5Z\\xfdJ\\xf0\\xba\\xc0@\\x80i\\xd7\\x18\\x0f\\xbb\\xc0@;x\\xb1\\xe6-\\xbb\\xc0@\\xf6\\x86\\x8b\\xb4L\\xbb\\xc0@\\xb1\\x95e\\x82k\\xbb\\xc0@m\\xa4?P\\x8a\\xbb\\xc0@\\'\\xb3\\x19\\x1e\\xa9\\xbb\\xc0@\\xe2\\xc1\\xf3\\xeb\\xc7\\xbb\\xc0@\\x9c\\xd0\\xcd\\xb9\\xe6\\xbb\\xc0@W\\xdf\\xa7\\x87\\x05\\xbc\\xc0@\\x12\\xee\\x81U$\\xbc\\xc0@\\xcd\\xfc[#C\\xbc\\xc0@\\x88\\x0b6\\xf1a\\xbc\\xc0@D\\x1a\\x10\\xbf\\x80\\xbc\\xc0@\\xfe(\\xea\\x8c\\x9f\\xbc\\xc0@\\xb97\\xc4Z\\xbe\\xbc\\xc0@tF\\x9e(\\xdd\\xbc\\xc0@/Ux\\xf6\\xfb\\xbc\\xc0@\\xeacR\\xc4\\x1a\\xbd\\xc0@\\xa5r,\\x929\\xbd\\xc0@`\\x81\\x06`X\\xbd\\xc0@\\x1a\\x90\\xe0-w\\xbd\\xc0@\\xd5\\x9e\\xba\\xfb\\x95\\xbd\\xc0@\\x90\\xad\\x94\\xc9\\xb4\\xbd\\xc0@K\\xbcn\\x97\\xd3\\xbd\\xc0@\\x06\\xcbHe\\xf2\\xbd\\xc0@\\xc1\\xd9\"3\\x11\\xbe\\xc0@|\\xe8\\xfc\\x000\\xbe\\xc0@7\\xf7\\xd6\\xceN\\xbe\\xc0@\\xf1\\x05\\xb1\\x9cm\\xbe\\xc0@\\xad\\x14\\x8bj\\x8c\\xbe\\xc0@h#e8\\xab\\xbe\\xc0@#2?\\x06\\xca\\xbe\\xc0@\\xde@\\x19\\xd4\\xe8\\xbe\\xc0@\\x99O\\xf3\\xa1\\x07\\xbf\\xc0@S^\\xcdo&\\xbf\\xc0@\\x0em\\xa7=E\\xbf\\xc0@\\xc8{\\x81\\x0bd\\xbf\\xc0@\\x84\\x8a[\\xd9\\x82\\xbf\\xc0@?\\x995\\xa7\\xa1\\xbf\\xc0@\\xfa\\xa7\\x0fu\\xc0\\xbf\\xc0@\\xb5\\xb6\\xe9B\\xdf\\xbf\\xc0@p\\xc5\\xc3\\x10\\xfe\\xbf\\xc0@+\\xd4\\x9d\\xde\\x1c\\xc0\\xc0@\\xe5\\xe2w\\xac;\\xc0\\xc0@\\xa0\\xf1QzZ\\xc0\\xc0@\\\\\\x00,Hy\\xc0\\xc0@\\x17\\x0f\\x06\\x16\\x98\\xc0\\xc0@\\xd1\\x1d\\xe0\\xe3\\xb6\\xc0\\xc0@\\x8c,\\xba\\xb1\\xd5\\xc0\\xc0@G;\\x94\\x7f\\xf4\\xc0\\xc0@\\x02JnM\\x13\\xc1\\xc0@\\xbcXH\\x1b2\\xc1\\xc0@wg\"\\xe9P\\xc1\\xc0@2v\\xfc\\xb6o\\xc1\\xc0@\\xee\\x84\\xd6\\x84\\x8e\\xc1\\xc0@\\xa9\\x93\\xb0R\\xad\\xc1\\xc0@d\\xa2\\x8a \\xcc\\xc1\\xc0@\\x1f\\xb1d\\xee\\xea\\xc1\\xc0@\\xda\\xbf>\\xbc\\t\\xc2\\xc0@\\x94\\xce\\x18\\x8a(\\xc2\\xc0@N\\xdd\\xf2WG\\xc2\\xc0@\\t\\xec\\xcc%f\\xc2\\xc0@\\xc5\\xfa\\xa6\\xf3\\x84\\xc2\\xc0@\\x80\\t\\x81\\xc1\\xa3\\xc2\\xc0@;\\x18[\\x8f\\xc2\\xc2\\xc0@\\xf6&5]\\xe1\\xc2\\xc0@\\xb05\\x0f+\\x00\\xc3\\xc0@kD\\xe9\\xf8\\x1e\\xc3\\xc0@&S\\xc3\\xc6=\\xc3\\xc0@\\xe1a\\x9d\\x94\\\\\\xc3\\xc0@\\x9cpwb{\\xc3\\xc0@X\\x7fQ0\\x9a\\xc3\\xc0@\\x13\\x8e+\\xfe\\xb8\\xc3\\xc0@\\xce\\x9c\\x05\\xcc\\xd7\\xc3\\xc0@\\x87\\xab\\xdf\\x99\\xf6\\xc3\\xc0@B\\xba\\xb9g\\x15\\xc4\\xc0@\\xfd\\xc8\\x9354\\xc4\\xc0@\\xb8\\xd7m\\x03S\\xc4\\xc0@s\\xe6G\\xd1q\\xc4\\xc0@/\\xf5!\\x9f\\x90\\xc4\\xc0@\\xea\\x03\\xfcl\\xaf\\xc4\\xc0@\\xa5\\x12\\xd6:\\xce\\xc4\\xc0@_!\\xb0\\x08\\xed\\xc4\\xc0@\\x1a0\\x8a\\xd6\\x0b\\xc5\\xc0@\\xd5>d\\xa4*\\xc5\\xc0@\\x90M>rI\\xc5\\xc0@K\\\\\\x18@h\\xc5\\xc0@\\x06k\\xf2\\r\\x87\\xc5\\xc0@\\xc1y\\xcc\\xdb\\xa5\\xc5\\xc0@{\\x88\\xa6\\xa9\\xc4\\xc5\\xc0@6\\x97\\x80w\\xe3\\xc5\\xc0@\\xf1\\xa5ZE\\x02\\xc6\\xc0@\\xac\\xb44\\x13!\\xc6\\xc0@g\\xc3\\x0e\\xe1?\\xc6\\xc0@\"\\xd2\\xe8\\xae^\\xc6\\xc0@\\xde\\xe0\\xc2|}\\xc6\\xc0@\\x99\\xef\\x9cJ\\x9c\\xc6\\xc0@S\\xfev\\x18\\xbb\\xc6\\xc0@\\x0e\\rQ\\xe6\\xd9\\xc6\\xc0@\\xc9\\x1b+\\xb4\\xf8\\xc6\\xc0@\\x84*\\x05\\x82\\x17\\xc7\\xc0@>9\\xdfO6\\xc7\\xc0@\\xf9G\\xb9\\x1dU\\xc7\\xc0@\\xb4V\\x93\\xebs\\xc7\\xc0@pem\\xb9\\x92\\xc7\\xc0@*tG\\x87\\xb1\\xc7\\xc0@\\xe5\\x82!U\\xd0\\xc7\\xc0@\\xa0\\x91\\xfb\"\\xef\\xc7\\xc0@[\\xa0\\xd5\\xf0\\r\\xc8\\xc0@\\x16\\xaf\\xaf\\xbe,\\xc8\\xc0@\\xd1\\xbd\\x89\\x8cK\\xc8\\xc0@\\x8c\\xcccZj\\xc8\\xc0@G\\xdb=(\\x89\\xc8\\xc0@\\x02\\xea\\x17\\xf6\\xa7\\xc8\\xc0@\\xbc\\xf8\\xf1\\xc3\\xc6\\xc8\\xc0@w\\x07\\xcc\\x91\\xe5\\xc8\\xc0@2\\x16\\xa6_\\x04\\xc9\\xc0@\\xed$\\x80-#\\xc9\\xc0@\\xa83Z\\xfbA\\xc9\\xc0@cB4\\xc9`\\xc9\\xc0@\\x1eQ\\x0e\\x97\\x7f\\xc9\\xc0@\\xd9_\\xe8d\\x9e\\xc9\\xc0@\\x94n\\xc22\\xbd\\xc9\\xc0@O}\\x9c\\x00\\xdc\\xc9\\xc0@\\n\\x8cv\\xce\\xfa\\xc9\\xc0@\\xc5\\x9aP\\x9c\\x19\\xca\\xc0@\\x80\\xa9*j8\\xca\\xc0@9\\xb8\\x048W\\xca\\xc0@\\xf4\\xc6\\xde\\x05v\\xca\\xc0@\\xb0\\xd5\\xb8\\xd3\\x94\\xca\\xc0@k\\xe4\\x92\\xa1\\xb3\\xca\\xc0@&\\xf3lo\\xd2\\xca\\xc0@\\xe1\\x01G=\\xf1\\xca\\xc0@\\x9c\\x10!\\x0b\\x10\\xcb\\xc0@W\\x1f\\xfb\\xd8.\\xcb\\xc0@\\x11.\\xd5\\xa6M\\xcb\\xc0@\\xcc<\\xaftl\\xcb\\xc0@\\x88K\\x89B\\x8b\\xcb\\xc0@CZc\\x10\\xaa\\xcb\\xc0@\\xfeh=\\xde\\xc8\\xcb\\xc0@\\xb9w\\x17\\xac\\xe7\\xcb\\xc0@s\\x86\\xf1y\\x06\\xcc\\xc0@.\\x95\\xcbG%\\xcc\\xc0@\\xe8\\xa3\\xa5\\x15D\\xcc\\xc0@\\xa3\\xb2\\x7f\\xe3b\\xcc\\xc0@^\\xc1Y\\xb1\\x81\\xcc\\xc0@\\x1a\\xd03\\x7f\\xa0\\xcc\\xc0@\\xd5\\xde\\rM\\xbf\\xcc\\xc0@\\x90\\xed\\xe7\\x1a\\xde\\xcc\\xc0@K\\xfc\\xc1\\xe8\\xfc\\xcc\\xc0@\\x05\\x0b\\x9c\\xb6\\x1b\\xcd\\xc0@\\xc0\\x19v\\x84:\\xcd\\xc0@{(PRY\\xcd\\xc0@67* x\\xcd\\xc0@\\xf1E\\x04\\xee\\x96\\xcd\\xc0@\\xacT\\xde\\xbb\\xb5\\xcd\\xc0@gc\\xb8\\x89\\xd4\\xcd\\xc0@\"r\\x92W\\xf3\\xcd\\xc0@\\xdc\\x80l%\\x12\\xce\\xc0@\\x97\\x8fF\\xf30\\xce\\xc0@R\\x9e \\xc1O\\xce\\xc0@\\r\\xad\\xfa\\x8en\\xce\\xc0@\\xc9\\xbb\\xd4\\\\\\x8d\\xce\\xc0@\\x84\\xca\\xae*\\xac\\xce\\xc0@?\\xd9\\x88\\xf8\\xca\\xce\\xc0@\\xf9\\xe7b\\xc6\\xe9\\xce\\xc0@\\xb4\\xf6<\\x94\\x08\\xcf\\xc0@o\\x05\\x17b\\'\\xcf\\xc0@)\\x14\\xf1/F\\xcf\\xc0@\\xe4\"\\xcb\\xfdd\\xcf\\xc0@\\xa01\\xa5\\xcb\\x83\\xcf\\xc0@[@\\x7f\\x99\\xa2\\xcf\\xc0@\\x16OYg\\xc1\\xcf\\xc0@\\xd0]35\\xe0\\xcf\\xc0@\\x8bl\\r\\x03\\xff\\xcf\\xc0@F{\\xe7\\xd0\\x1d\\xd0\\xc0@\\x01\\x8a\\xc1\\x9e<\\xd0\\xc0@\\xbc\\x98\\x9bl[\\xd0\\xc0@w\\xa7u:z\\xd0\\xc0@3\\xb6O\\x08\\x99\\xd0\\xc0@\\xee\\xc4)\\xd6\\xb7\\xd0\\xc0@\\xa7\\xd3\\x03\\xa4\\xd6\\xd0\\xc0@b\\xe2\\xddq\\xf5\\xd0\\xc0@\\x1d\\xf1\\xb7?\\x14\\xd1\\xc0@\\xd8\\xff\\x91\\r3\\xd1\\xc0@\\x93\\x0el\\xdbQ\\xd1\\xc0@N\\x1dF\\xa9p\\xd1\\xc0@\\n, w\\x8f\\xd1\\xc0@\\xc4:\\xfaD\\xae\\xd1\\xc0@\\x7fI\\xd4\\x12\\xcd\\xd1\\xc0@:X\\xae\\xe0\\xeb\\xd1\\xc0@\\xf5f\\x88\\xae\\n\\xd2\\xc0@\\xb0ub|)\\xd2\\xc0@k\\x84<JH\\xd2\\xc0@%\\x93\\x16\\x18g\\xd2\\xc0@\\xe0\\xa1\\xf0\\xe5\\x85\\xd2\\xc0@\\x9b\\xb0\\xca\\xb3\\xa4\\xd2\\xc0@V\\xbf\\xa4\\x81\\xc3\\xd2\\xc0@\\x11\\xce~O\\xe2\\xd2\\xc0@\\xcc\\xdcX\\x1d\\x01\\xd3\\xc0@\\x87\\xeb2\\xeb\\x1f\\xd3\\xc0@B\\xfa\\x0c\\xb9>\\xd3\\xc0@\\xfd\\x08\\xe7\\x86]\\xd3\\xc0@\\xb8\\x17\\xc1T|\\xd3\\xc0@s&\\x9b\"\\x9b\\xd3\\xc0@.5u\\xf0\\xb9\\xd3\\xc0@\\xe9CO\\xbe\\xd8\\xd3\\xc0@\\xa4R)\\x8c\\xf7\\xd3\\xc0@^a\\x03Z\\x16\\xd4\\xc0@\\x19p\\xdd\\'5\\xd4\\xc0@\\xd4~\\xb7\\xf5S\\xd4\\xc0@\\x8e\\x8d\\x91\\xc3r\\xd4\\xc0@J\\x9ck\\x91\\x91\\xd4\\xc0@\\x05\\xabE_\\xb0\\xd4\\xc0@\\xc0\\xb9\\x1f-\\xcf\\xd4\\xc0@{\\xc8\\xf9\\xfa\\xed\\xd4\\xc0@6\\xd7\\xd3\\xc8\\x0c\\xd5\\xc0@\\xf1\\xe5\\xad\\x96+\\xd5\\xc0@\\xac\\xf4\\x87dJ\\xd5\\xc0@f\\x03b2i\\xd5\\xc0@\"\\x12<\\x00\\x88\\xd5\\xc0@\\xdc \\x16\\xce\\xa6\\xd5\\xc0@\\x97/\\xf0\\x9b\\xc5\\xd5\\xc0@R>\\xcai\\xe4\\xd5\\xc0@\\rM\\xa47\\x03\\xd6\\xc0@\\xc8[~\\x05\"\\xd6\\xc0@\\x82jX\\xd3@\\xd6\\xc0@=y2\\xa1_\\xd6\\xc0@\\xf8\\x87\\x0co~\\xd6\\xc0@\\xb4\\x96\\xe6<\\x9d\\xd6\\xc0@o\\xa5\\xc0\\n\\xbc\\xd6\\xc0@*\\xb4\\x9a\\xd8\\xda\\xd6\\xc0@\\xe5\\xc2t\\xa6\\xf9\\xd6\\xc0@\\xa0\\xd1Nt\\x18\\xd7\\xc0@Y\\xe0(B7\\xd7\\xc0@\\x14\\xef\\x02\\x10V\\xd7\\xc0@\\xcf\\xfd\\xdc\\xddt\\xd7\\xc0@\\x8b\\x0c\\xb7\\xab\\x93\\xd7\\xc0@F\\x1b\\x91y\\xb2\\xd7\\xc0@\\x01*kG\\xd1\\xd7\\xc0@\\xbc8E\\x15\\xf0\\xd7\\xc0@wG\\x1f\\xe3\\x0e\\xd8\\xc0@1V\\xf9\\xb0-\\xd8\\xc0@\\xecd\\xd3~L\\xd8\\xc0@\\xa7s\\xadLk\\xd8\\xc0@b\\x82\\x87\\x1a\\x8a\\xd8\\xc0@\\x1e\\x91a\\xe8\\xa8\\xd8\\xc0@\\xd9\\x9f;\\xb6\\xc7\\xd8\\xc0@\\x93\\xae\\x15\\x84\\xe6\\xd8\\xc0@M\\xbd\\xefQ\\x05\\xd9\\xc0@\\x08\\xcc\\xc9\\x1f$\\xd9\\xc0@\\xc3\\xda\\xa3\\xedB\\xd9\\xc0@~\\xe9}\\xbba\\xd9\\xc0@9\\xf8W\\x89\\x80\\xd9\\xc0@\\xf5\\x062W\\x9f\\xd9\\xc0@\\xb0\\x15\\x0c%\\xbe\\xd9\\xc0@k$\\xe6\\xf2\\xdc\\xd9\\xc0@%3\\xc0\\xc0\\xfb\\xd9\\xc0@\\xe0A\\x9a\\x8e\\x1a\\xda\\xc0@\\x9bPt\\\\9\\xda\\xc0@V_N*X\\xda\\xc0@\\x10n(\\xf8v\\xda\\xc0@\\xcc|\\x02\\xc6\\x95\\xda\\xc0@\\x87\\x8b\\xdc\\x93\\xb4\\xda\\xc0@\\x94\\x8c\\x05numpy\\x94\\x8c\\x05dtype\\x94\\x93\\x94\\x8c\\x02f8\\x94K\\x00K\\x01\\x87\\x94R\\x94(K\\x03\\x8c\\x01<\\x94NNNJ\\xff\\xff\\xff\\xffJ\\xff\\xff\\xff\\xffK\\x00t\\x94bM\\xdd\\x05\\x85\\x94\\x8c\\x01C\\x94t\\x94R\\x94.')"
}
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[12].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[12].electronFunctionString = {
    "data": '# @ct.electron\ndef local_sidereal_time(d, long, T):\n    LST = 100.46 + 0.985647 * (d + T / 24) + long + 15 * T\n    return LST\n\n\n',
}
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[12].electronError = null
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[12].electronInput = {
    "data": "{'args': (), 'kwargs': {'T': '[ 7.     7.016  7.032 ... 30.968 30.984 31.   ]', 'd': '8305', 'long': '-123.1207'}}",
    "python_object": "import pickle\npickle.loads(b'\\x80\\x05\\x95n\\x00\\x00\\x00\\x00\\x00\\x00\\x00}\\x94(\\x8c\\x04args\\x94)\\x8c\\x06kwargs\\x94}\\x94(\\x8c\\x01T\\x94\\x8c/[ 7.     7.016  7.032 ... 30.968 30.984 31.   ]\\x94\\x8c\\x01d\\x94\\x8c\\x048305\\x94\\x8c\\x04long\\x94\\x8c\\t-123.1207\\x94uu.')"
}
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[14].electronDetails = {
    "id": 14,
    "node_id": 14,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/ba3c238c-cb92-48e8-b7b2-debeebe2e81a/node_4",
    "name": "hour_angle",
    "status": "PENDING",
    "started_at": "2022-08-10T12:14:39",
    "ended_at": "2022-08-11T12:14:40",
    "runtime": 50
}
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[14].electronResult = null
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[14].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[14].electronFunctionString = {
    "data": '# @ct.electron\ndef hour_angle(LST, RA):\n    LST_list = []\n    for source in RA:\n        LST_list.append(np.asarray([value - source for value in LST]))\n    return LST_list\n\n\n',
}
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[14].electronError = null
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[14].electronInput = {
    "data": "{'args': (), 'kwargs': {'RA': '[101.28715533333333, 346.6223687285788]', 'LST': '[8268.42511537 8268.66577247 8268.90642957 ... 8628.92944818 8629.17010528\\n 8629.41076238]'}}",
    "python_object": "import pickle\npickle.loads(b\"\\x80\\x05\\x95\\xac\\x00\\x00\\x00\\x00\\x00\\x00\\x00}\\x94(\\x8c\\x04args\\x94)\\x8c\\x06kwargs\\x94}\\x94(\\x8c\\x02RA\\x94\\x8c'[101.28715533333333, 346.6223687285788]\\x94\\x8c\\x03LST\\x94\\x8cZ[8268.42511537 8268.66577247 8268.90642957 ... 8628.92944818 8629.17010528\\n 8629.41076238]\\x94uu.\")"
}
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[15].electronDetails = {
    "id": 15,
    "node_id": 15,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/ba3c238c-cb92-48e8-b7b2-debeebe2e81a/node_4",
    "name": "altitude_of_target",
    "status": "PENDING",
    "started_at": "2022-08-10T12:14:39",
    "ended_at": "2022-08-11T12:14:40",
    "runtime": 50
}
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[15].electronResult = null
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[15].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[15].electronFunctionString = {
    "data": '# @ct.electron\ndef altitude_of_target(dec, lat, ha):\n    alt_list = []\n    lat = lat * 0.0174533\n    for i in range(len(dec)):\n        dec_i = dec[i] * 0.0174533\n        ha_i = ha[i] * 0.0174533\n        alt = np.arcsin(\n            np.sin(dec_i) * np.sin(lat) + np.cos(dec_i) * np.cos(lat) * np.cos(ha_i)\n        )\n        alt_list.append(alt * 57.2958)\n    return alt_list\n\n\n',
}
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[15].electronError = null
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[15].electronInput = {
    "data": "{'args': (), 'kwargs': {'dec': '[-16.71611586111111, -5.041399250518333]', 'ha': '[array([8167.13796004, 8167.37861714, 8167.61927424, ..., 8527.64229285,\\n       8527.88294994, 8528.12360704]), array([7921.80274665, 7922.04340374, 7922.28406084, ..., 8282.30707945,\\n       8282.54773655, 8282.78839365])]', 'lat': '49.2827'}}",
    "python_object": "import pickle\npickle.loads(b'\\x80\\x05\\x95A\\x01\\x00\\x00\\x00\\x00\\x00\\x00}\\x94(\\x8c\\x04args\\x94)\\x8c\\x06kwargs\\x94}\\x94(\\x8c\\x03dec\\x94\\x8c([-16.71611586111111, -5.041399250518333]\\x94\\x8c\\x02ha\\x94\\x8c\\xde[array([8167.13796004, 8167.37861714, 8167.61927424, ..., 8527.64229285,\\n       8527.88294994, 8528.12360704]), array([7921.80274665, 7922.04340374, 7922.28406084, ..., 8282.30707945,\\n       8282.54773655, 8282.78839365])]\\x94\\x8c\\x03lat\\x94\\x8c\\x0749.2827\\x94uu.')"
}
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[17].electronDetails = {
    "id": 17,
    "node_id": 17,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/ba3c238c-cb92-48e8-b7b2-debeebe2e81a/node_4",
    "name": "get_azimuth",
    "status": "PENDING",
    "started_at": "2022-08-10T12:14:39",
    "ended_at": "2022-08-11T12:14:40",
    "runtime": 50
}
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[17].electronResult = null
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[17].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[17].electronFunctionString = {
    "data": '# @ct.electron\ndef get_azimuth(dec, lat, ha, alt):\n    az_list = []\n    lat = round(lat * 0.0174533, 2)\n    for i in range(len(dec)):\n        azimuth = []\n        dec_i = round(dec[i] * 0.0174533, 2)\n        ha_i = ha[i] * 0.0174533\n        alt_i = alt[i] * 0.0174533\n        a = np.arccos(\n            (np.sin(dec_i) - np.sin(alt_i) * np.sin(lat))\n            / (np.cos(alt_i) * np.cos(lat))\n        )\n        for q in range(len(ha_i)):\n            if np.sin(ha_i[q]) < 0:\n                azimuth.append(a[q] * 57.2958)\n            else:\n                azimuth.append(360 - (a[q] * 57.2958))\n        az_list.append(np.array(azimuth))\n    return az_list\n\n\n',
}
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[17].electronError = null
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[17].electronInput = {
    "data": "{'args': (), 'kwargs': {'dec': '[-16.71611586111111, -5.041399250518333]', 'ha': '[array([8167.13796004, 8167.37861714, 8167.61927424, ..., 8527.64229285,\\n       8527.88294994, 8528.12360704]), array([7921.80274665, 7922.04340374, 7922.28406084, ..., 8282.30707945,\\n       8282.54773655, 8282.78839365])]', 'alt': '[array([-27.43219742, -27.27607228, -27.11989331, ..., -27.10485205,\\n       -26.94861616, -26.79233023]), array([35.65312336, 35.64665394, 35.63937735, ..., 35.63863409,\\n       35.630473  , 35.6215055 ])]', 'lat': '49.2827'}}",
    "python_object": "import pickle\npickle.loads(b'\\x80\\x05\\x95\\x16\\x02\\x00\\x00\\x00\\x00\\x00\\x00}\\x94(\\x8c\\x04args\\x94)\\x8c\\x06kwargs\\x94}\\x94(\\x8c\\x03dec\\x94\\x8c([-16.71611586111111, -5.041399250518333]\\x94\\x8c\\x02ha\\x94\\x8c\\xde[array([8167.13796004, 8167.37861714, 8167.61927424, ..., 8527.64229285,\\n       8527.88294994, 8528.12360704]), array([7921.80274665, 7922.04340374, 7922.28406084, ..., 8282.30707945,\\n       8282.54773655, 8282.78839365])]\\x94\\x8c\\x03alt\\x94\\x8c\\xcc[array([-27.43219742, -27.27607228, -27.11989331, ..., -27.10485205,\\n       -26.94861616, -26.79233023]), array([35.65312336, 35.64665394, 35.63937735, ..., 35.63863409,\\n       35.630473  , 35.6215055 ])]\\x94\\x8c\\x03lat\\x94\\x8c\\x0749.2827\\x94uu.')"
}

//   Dispatch 699d2cb1-0776-4c54-a958-0a79082497e4
latticeDetailsDemoData["699d2cb1-0776-4c54-a958-0a79082497e4"] = {}
latticeDetailsDemoData["699d2cb1-0776-4c54-a958-0a79082497e4"].latticeDetails =
{
    "dispatch_id": "699d2cb1-0776-4c54-a958-0a79082497e4",
    "status": "COMPLETED",
    "total_electrons": 4,
    "total_electrons_completed": 4,
    "started_at": "2022-10-03T09:04:56",
    "ended_at": "2022-10-03T09:04:58",
    "directory": "/home/prasannavenkatesh/Desktop/workflows/results/699d2cb1-0776-4c54-a958-0a79082497e4",
    "description": "",
    "runtime": 2000,
    "updated_at": null
};
latticeDetailsDemoData["699d2cb1-0776-4c54-a958-0a79082497e4"].latticeError = "";
latticeDetailsDemoData["699d2cb1-0776-4c54-a958-0a79082497e4"].latticeResult = {
    "data": "\"[[1, 1, 1], [1, 1, 1], [1, 1, 1]]\"",
    "python_object": "import pickle\npickle.loads(b'\\x80\\x05\\x95#\\x00\\x00\\x00\\x00\\x00\\x00\\x00]\\x94(]\\x94(K\\x01K\\x01K\\x01e]\\x94(K\\x01K\\x01K\\x01e]\\x94(K\\x01K\\x01K\\x01ee.')"
}
latticeDetailsDemoData["699d2cb1-0776-4c54-a958-0a79082497e4"].latticeInput = {
    "data": "{'args': ('1',), 'kwargs': {}}",
    "python_object": "import pickle\npickle.loads(b'\\x80\\x05\\x95\\x1d\\x00\\x00\\x00\\x00\\x00\\x00\\x00}\\x94(\\x8c\\x04args\\x94\\x8c\\x011\\x94\\x85\\x94\\x8c\\x06kwargs\\x94}\\x94u.')"
}
latticeDetailsDemoData["699d2cb1-0776-4c54-a958-0a79082497e4"].latticeFunctionString = {
    "data": "@ct.lattice\ndef compute_energy(x):\n    y=identity(x)\n    result=SubEta(y)\n    result=SubBeta(result)\n    return result\n\n\n"
}
latticeDetailsDemoData["699d2cb1-0776-4c54-a958-0a79082497e4"].latticeExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["699d2cb1-0776-4c54-a958-0a79082497e4"].sublatticesList = [
    {
        "dispatch_id": "419d22a3-e1d7-46a8-92ba-d4ef234674b0",
        "lattice_name": "SubBeta",
        "runtime": 1000,
        "total_electrons": 15,
        "total_electrons_completed": 15,
        "started_at": "2022-10-03T09:04:57",
        "ended_at": "2022-10-03T09:04:58",
        "status": "COMPLETED",
        "updated_at": "2022-10-03T09:04:58"
    },
    {
        "dispatch_id": "e8096480-15da-41c3-b869-212e7e773749",
        "lattice_name": "SubEta",
        "runtime": 0,
        "total_electrons": 6,
        "total_electrons_completed": 6,
        "started_at": "2022-10-03T09:04:57",
        "ended_at": "2022-10-03T09:04:57",
        "status": "COMPLETED",
        "updated_at": "2022-10-03T09:04:57"
    }
]

// electron data initilisation
latticeDetailsDemoData["699d2cb1-0776-4c54-a958-0a79082497e4"].electron = []
latticeDetailsDemoData["699d2cb1-0776-4c54-a958-0a79082497e4"].electron[0] = {}
latticeDetailsDemoData["699d2cb1-0776-4c54-a958-0a79082497e4"].electron[1] = {}
latticeDetailsDemoData["699d2cb1-0776-4c54-a958-0a79082497e4"].electron[2] = {}
latticeDetailsDemoData["699d2cb1-0776-4c54-a958-0a79082497e4"].electron[3] = {}

latticeDetailsDemoData["699d2cb1-0776-4c54-a958-0a79082497e4"].electron[0].electronDetails = {
    "id": 1076,
    "node_id": 0,
    "parent_lattice_id": 34,
    "type": "function",
    "storage_path": "/home/prasannavenkatesh/Desktop/workflows/results/699d2cb1-0776-4c54-a958-0a79082497e4/node_0",
    "name": "identity",
    "status": "COMPLETED",
    "started_at": "2022-10-03T09:04:56",
    "ended_at": "2022-10-03T09:04:56",
    "runtime": 0,
    "description": ""
}
latticeDetailsDemoData["699d2cb1-0776-4c54-a958-0a79082497e4"].electron[0].electronResult = {
    "data": "\"1\"",
    "python_object": "import pickle\npickle.loads(b'\\x80\\x05K\\x01.')"
}
latticeDetailsDemoData["699d2cb1-0776-4c54-a958-0a79082497e4"].electron[0].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["699d2cb1-0776-4c54-a958-0a79082497e4"].electron[0].electronFunctionString = {
    "data": "@ct.electron\ndef identity(x):\n    return x\n\n\n"
}
latticeDetailsDemoData["699d2cb1-0776-4c54-a958-0a79082497e4"].electron[0].electronError = null
latticeDetailsDemoData["699d2cb1-0776-4c54-a958-0a79082497e4"].electron[0].electronInput = {
    "data": "{'args': ('1',), 'kwargs': {}}",
    "python_object": "import pickle\npickle.loads(b'\\x80\\x05\\x95\\x1d\\x00\\x00\\x00\\x00\\x00\\x00\\x00}\\x94(\\x8c\\x04args\\x94\\x8c\\x011\\x94\\x85\\x94\\x8c\\x06kwargs\\x94}\\x94u.')"
}

latticeDetailsDemoData["699d2cb1-0776-4c54-a958-0a79082497e4"].electron[2].electronDetails = {
    "id": 1078,
    "node_id": 2,
    "parent_lattice_id": 34,
    "type": "sublattice",
    "storage_path": "/home/prasannavenkatesh/Desktop/workflows/results/699d2cb1-0776-4c54-a958-0a79082497e4/node_2",
    "name": ":sublattice:SubEta",
    "status": "COMPLETED",
    "started_at": "2022-10-03T09:04:57",
    "ended_at": "2022-10-03T09:04:57",
    "runtime": 0,
    "description": ""
}
latticeDetailsDemoData["699d2cb1-0776-4c54-a958-0a79082497e4"].electron[2].electronResult = {
    "data": "\"[1, 1, 1]\"",
    "python_object": "import pickle\npickle.loads(b'\\x80\\x05\\x95\\x0b\\x00\\x00\\x00\\x00\\x00\\x00\\x00]\\x94(K\\x01K\\x01K\\x01e.')"
}
latticeDetailsDemoData["699d2cb1-0776-4c54-a958-0a79082497e4"].electron[2].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["699d2cb1-0776-4c54-a958-0a79082497e4"].electron[2].electronFunctionString = {
    "data": "@ct.electron\n@ct.lattice\ndef SubEta(x):\n    a=[]\n    for i in range(3):\n        a.append(identity(x))\n    return a\n\n\n"
}
latticeDetailsDemoData["699d2cb1-0776-4c54-a958-0a79082497e4"].electron[2].electronError = null
latticeDetailsDemoData["699d2cb1-0776-4c54-a958-0a79082497e4"].electron[2].electronInput = {
    "data": "{'args': ('1',), 'kwargs': {}}",
    "python_object": "import pickle\npickle.loads(b'\\x80\\x05\\x95\\x1d\\x00\\x00\\x00\\x00\\x00\\x00\\x00}\\x94(\\x8c\\x04args\\x94\\x8c\\x011\\x94\\x85\\x94\\x8c\\x06kwargs\\x94}\\x94u.')"
}

latticeDetailsDemoData["699d2cb1-0776-4c54-a958-0a79082497e4"].electron[3].electronDetails = {
    "id": 1079,
    "node_id": 3,
    "parent_lattice_id": 34,
    "type": "sublattice",
    "storage_path": "/home/prasannavenkatesh/Desktop/workflows/results/699d2cb1-0776-4c54-a958-0a79082497e4/node_3",
    "name": ":sublattice:SubBeta",
    "status": "COMPLETED",
    "started_at": "2022-10-03T09:04:57",
    "ended_at": "2022-10-03T09:04:58",
    "runtime": 1000,
    "description": ""
}
latticeDetailsDemoData["699d2cb1-0776-4c54-a958-0a79082497e4"].electron[3].electronResult = {
    "data": "\"[[1, 1, 1], [1, 1, 1], [1, 1, 1]]\"",
    "python_object": "import pickle\npickle.loads(b'\\x80\\x05\\x95#\\x00\\x00\\x00\\x00\\x00\\x00\\x00]\\x94(]\\x94(K\\x01K\\x01K\\x01e]\\x94(K\\x01K\\x01K\\x01e]\\x94(K\\x01K\\x01K\\x01ee.')"
}
latticeDetailsDemoData["699d2cb1-0776-4c54-a958-0a79082497e4"].electron[3].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["699d2cb1-0776-4c54-a958-0a79082497e4"].electron[3].electronFunctionString = {
    "data": "@ct.electron\n@ct.lattice\ndef SubBeta(x):\n    a=[]\n    for i in range(3):\n        a.append(identity(x))\n    return a    \n\n\n"
}
latticeDetailsDemoData["699d2cb1-0776-4c54-a958-0a79082497e4"].electron[3].electronError = null
latticeDetailsDemoData["699d2cb1-0776-4c54-a958-0a79082497e4"].electron[3].electronInput = {
    "data": "{'args': ('[1, 1, 1]',), 'kwargs': {}}",
    "python_object": "import pickle\npickle.loads(b'\\x80\\x05\\x95%\\x00\\x00\\x00\\x00\\x00\\x00\\x00}\\x94(\\x8c\\x04args\\x94\\x8c\\t[1, 1, 1]\\x94\\x85\\x94\\x8c\\x06kwargs\\x94}\\x94u.')"
}



//   Dispatch e8096480-15da-41c3-b869-212e7e773749
latticeDetailsDemoData["e8096480-15da-41c3-b869-212e7e773749"] = {}
latticeDetailsDemoData["e8096480-15da-41c3-b869-212e7e773749"].latticeDetails =
{
    "dispatch_id": "e8096480-15da-41c3-b869-212e7e773749",
    "status": "COMPLETED",
    "total_electrons": 4,
    "total_electrons_completed": 4,
    "started_at": "2022-10-03T09:04:56",
    "ended_at": "2022-10-03T09:04:58",
    "directory": "/home/prasannavenkatesh/Desktop/workflows/results/e8096480-15da-41c3-b869-212e7e773749",
    "description": "",
    "runtime": 2000,
    "updated_at": null
};
latticeDetailsDemoData["e8096480-15da-41c3-b869-212e7e773749"].latticeError = "";
latticeDetailsDemoData["e8096480-15da-41c3-b869-212e7e773749"].latticeResult = {
    "data": "\"[[1, 1, 1], [1, 1, 1], [1, 1, 1]]\""
  };
latticeDetailsDemoData["e8096480-15da-41c3-b869-212e7e773749"].latticeInput = {
    "data": "{\"args\": [\"1\"], \"kwargs\": {}}"
};
latticeDetailsDemoData["e8096480-15da-41c3-b869-212e7e773749"].latticeFunctionString = {
    "data": "@ct.lattice\ndef compute_energy(x):\n    y=identity(x)\n    result=SubEta(y)\n    result=SubBeta(result)\n    return result\n\n\n"
}
latticeDetailsDemoData["e8096480-15da-41c3-b869-212e7e773749"].latticeExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["e8096480-15da-41c3-b869-212e7e773749"].sublatticesList = [
    {
        "dispatch_id": "419d22a3-e1d7-46a8-92ba-d4ef234674b0",
        "lattice_name": "SubBeta",
        "runtime": 1000,
        "total_electrons": 15,
        "total_electrons_completed": 15,
        "started_at": "2022-10-03T09:04:57",
        "ended_at": "2022-10-03T09:04:58",
        "status": "COMPLETED",
        "updated_at": "2022-10-03T09:04:58"
    },
    {
        "dispatch_id": "e8096480-15da-41c3-b869-212e7e773749",
        "lattice_name": "SubEta",
        "runtime": 0,
        "total_electrons": 6,
        "total_electrons_completed": 6,
        "started_at": "2022-10-03T09:04:57",
        "ended_at": "2022-10-03T09:04:57",
        "status": "COMPLETED",
        "updated_at": "2022-10-03T09:04:57"
    }
]

// electron data initilisation
latticeDetailsDemoData["e8096480-15da-41c3-b869-212e7e773749"].electron = []
latticeDetailsDemoData["e8096480-15da-41c3-b869-212e7e773749"].electron[0] = {}
latticeDetailsDemoData["e8096480-15da-41c3-b869-212e7e773749"].electron[1] = {}
latticeDetailsDemoData["e8096480-15da-41c3-b869-212e7e773749"].electron[2] = {}
latticeDetailsDemoData["e8096480-15da-41c3-b869-212e7e773749"].electron[3] = {}
latticeDetailsDemoData["e8096480-15da-41c3-b869-212e7e773749"].electron[4] = {}
latticeDetailsDemoData["e8096480-15da-41c3-b869-212e7e773749"].electron[5] = {}

latticeDetailsDemoData["e8096480-15da-41c3-b869-212e7e773749"].electron[0].electronDetails = {
    "id": 1080,
    "node_id": 0,
    "parent_lattice_id": 35,
    "type": "function",
    "storage_path": "/home/prasannavenkatesh/Desktop/workflows/results/e8096480-15da-41c3-b869-212e7e773749/node_0",
    "name": "identity",
    "status": "COMPLETED",
    "started_at": "2022-10-03T09:04:57",
    "ended_at": "2022-10-03T09:04:57",
    "runtime": 0,
    "description": ""
}
latticeDetailsDemoData["e8096480-15da-41c3-b869-212e7e773749"].electron[0].electronResult = {
    "data": "\"1\"",
    "python_object": "import pickle\npickle.loads(b'\\x80\\x05K\\x01.')"
}
latticeDetailsDemoData["e8096480-15da-41c3-b869-212e7e773749"].electron[0].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["e8096480-15da-41c3-b869-212e7e773749"].electron[0].electronFunctionString = {
    "data": "@ct.electron\ndef identity(x):\n    return x\n\n\n"
}
latticeDetailsDemoData["e8096480-15da-41c3-b869-212e7e773749"].electron[0].electronError = null
latticeDetailsDemoData["e8096480-15da-41c3-b869-212e7e773749"].electron[0].electronInput = {
    "data": "{'args': ('1',), 'kwargs': {}}",
    "python_object": "import pickle\npickle.loads(b'\\x80\\x05\\x95\\x1d\\x00\\x00\\x00\\x00\\x00\\x00\\x00}\\x94(\\x8c\\x04args\\x94\\x8c\\x011\\x94\\x85\\x94\\x8c\\x06kwargs\\x94}\\x94u.')"
}

latticeDetailsDemoData["e8096480-15da-41c3-b869-212e7e773749"].electron[2].electronDetails = {
    "id": 1082,
    "node_id": 2,
    "parent_lattice_id": 35,
    "type": "function",
    "storage_path": "/home/prasannavenkatesh/Desktop/workflows/results/e8096480-15da-41c3-b869-212e7e773749/node_2",
    "name": "identity",
    "status": "COMPLETED",
    "started_at": "2022-10-03T09:04:57",
    "ended_at": "2022-10-03T09:04:57",
    "runtime": 0,
    "description": ""
}
latticeDetailsDemoData["e8096480-15da-41c3-b869-212e7e773749"].electron[2].electronResult = {
    "data": "\"1\"",
    "python_object": "import pickle\npickle.loads(b'\\x80\\x05K\\x01.')"
}
latticeDetailsDemoData["e8096480-15da-41c3-b869-212e7e773749"].electron[2].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["e8096480-15da-41c3-b869-212e7e773749"].electron[2].electronFunctionString = {
    "data": "@ct.electron\ndef identity(x):\n    return x\n\n\n"
}
latticeDetailsDemoData["e8096480-15da-41c3-b869-212e7e773749"].electron[2].electronError = null
latticeDetailsDemoData["e8096480-15da-41c3-b869-212e7e773749"].electron[2].electronInput = {
    "data": "{'args': ('1',), 'kwargs': {}}",
    "python_object": "import pickle\npickle.loads(b'\\x80\\x05\\x95\\x1d\\x00\\x00\\x00\\x00\\x00\\x00\\x00}\\x94(\\x8c\\x04args\\x94\\x8c\\x011\\x94\\x85\\x94\\x8c\\x06kwargs\\x94}\\x94u.')"
}

latticeDetailsDemoData["e8096480-15da-41c3-b869-212e7e773749"].electron[4].electronDetails = {
    "id": 1084,
    "node_id": 4,
    "parent_lattice_id": 35,
    "type": "function",
    "storage_path": "/home/prasannavenkatesh/Desktop/workflows/results/e8096480-15da-41c3-b869-212e7e773749/node_4",
    "name": "identity",
    "status": "COMPLETED",
    "started_at": "2022-10-03T09:04:57",
    "ended_at": "2022-10-03T09:04:57",
    "runtime": 0,
    "description": ""
}
latticeDetailsDemoData["e8096480-15da-41c3-b869-212e7e773749"].electron[4].electronResult = {
    "data": "\"1\"",
    "python_object": "import pickle\npickle.loads(b'\\x80\\x05K\\x01.')"
}
latticeDetailsDemoData["e8096480-15da-41c3-b869-212e7e773749"].electron[4].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["e8096480-15da-41c3-b869-212e7e773749"].electron[4].electronFunctionString = {
    "data": "@ct.electron\ndef identity(x):\n    return x\n\n\n"
}
latticeDetailsDemoData["e8096480-15da-41c3-b869-212e7e773749"].electron[4].electronError = null
latticeDetailsDemoData["e8096480-15da-41c3-b869-212e7e773749"].electron[4].electronInput = {
    "data": "{'args': ('1',), 'kwargs': {}}",
    "python_object": "import pickle\npickle.loads(b'\\x80\\x05\\x95\\x1d\\x00\\x00\\x00\\x00\\x00\\x00\\x00}\\x94(\\x8c\\x04args\\x94\\x8c\\x011\\x94\\x85\\x94\\x8c\\x06kwargs\\x94}\\x94u.')"
}


//   Dispatch 419d22a3-e1d7-46a8-92ba-d4ef234674b0
latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"] = {}
latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"].latticeDetails =
{
    "dispatch_id": "419d22a3-e1d7-46a8-92ba-d4ef234674b0",
    "status": "COMPLETED",
    "total_electrons": 4,
    "total_electrons_completed": 4,
    "started_at": "2022-10-03T09:04:56",
    "ended_at": "2022-10-03T09:04:58",
    "directory": "/home/prasannavenkatesh/Desktop/workflows/results/419d22a3-e1d7-46a8-92ba-d4ef234674b0",
    "description": "",
    "runtime": 2000,
    "updated_at": null
};
latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"].latticeError = "";
latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"].latticeResult = {
    "data": "\"[[1, 1, 1], [1, 1, 1], [1, 1, 1]]\""
  };
latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"].latticeInput = {
    "data": "{\"args\": [\"1\"], \"kwargs\": {}}"
};
latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"].latticeFunctionString = {
    "data": "@ct.lattice\ndef compute_energy(x):\n    y=identity(x)\n    result=SubEta(y)\n    result=SubBeta(result)\n    return result\n\n\n"
}
latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"].latticeExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"].sublatticesList = [
    {
        "dispatch_id": "419d22a3-e1d7-46a8-92ba-d4ef234674b0",
        "lattice_name": "SubBeta",
        "runtime": 1000,
        "total_electrons": 15,
        "total_electrons_completed": 15,
        "started_at": "2022-10-03T09:04:57",
        "ended_at": "2022-10-03T09:04:58",
        "status": "COMPLETED",
        "updated_at": "2022-10-03T09:04:58"
    },
    {
        "dispatch_id": "419d22a3-e1d7-46a8-92ba-d4ef234674b0",
        "lattice_name": "SubEta",
        "runtime": 0,
        "total_electrons": 6,
        "total_electrons_completed": 6,
        "started_at": "2022-10-03T09:04:57",
        "ended_at": "2022-10-03T09:04:57",
        "status": "COMPLETED",
        "updated_at": "2022-10-03T09:04:57"
    }
]

// electron data initilisation
latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"].electron = []
latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"].electron[0] = {}
latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"].electron[1] = {}
latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"].electron[2] = {}
latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"].electron[3] = {}
latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"].electron[4] = {}
latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"].electron[5] = {}
latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"].electron[6] = {}
latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"].electron[7] = {}
latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"].electron[8] = {}
latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"].electron[9] = {}
latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"].electron[10] = {}
latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"].electron[11] = {}
latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"].electron[12] = {}
latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"].electron[13] = {}
latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"].electron[14] = {}
latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"].electron[15] = {}
latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"].electron[16] = {}
latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"].electron[17] = {}

latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"].electron[0].electronDetails = {
    "id": 1086,
    "node_id": 0,
    "parent_lattice_id": 36,
    "type": "function",
    "storage_path": "/home/prasannavenkatesh/Desktop/workflows/results/419d22a3-e1d7-46a8-92ba-d4ef234674b0/node_0",
    "name": "identity",
    "status": "COMPLETED",
    "started_at": "2022-10-03T09:04:57",
    "ended_at": "2022-10-03T09:04:58",
    "runtime": 1000,
    "description": ""
}
latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"].electron[0].electronResult = {
    "data": "\"[1, 1, 1]\"",
    "python_object": "import pickle\npickle.loads(b'\\x80\\x05\\x95\\x0b\\x00\\x00\\x00\\x00\\x00\\x00\\x00]\\x94(K\\x01K\\x01K\\x01e.')"
}
latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"].electron[0].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"].electron[0].electronFunctionString = {
    "data": "# Copyright 2021 Agnostiq Inc.\n#\n# This file is part of Covalent.\n#\n# Licensed under the GNU Affero General Public License 3.0 (the \"License\").\n# A copy of the License may be obtained with this software package or at\n#\n#      https://www.gnu.org/licenses/agpl-3.0.en.html\n#\n# Use of this file is prohibited except in compliance with the License. Any\n# modifications or derivative works of this file must retain this copyright\n# notice, and modified files must contain a notice indicating that they have\n# been altered from the originals.\n# Covalent is distributed in the hope that it will be useful, but WITHOUT\n# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or\n# FITNESS FOR A PARTICULAR PURPOSE. See the License for more details.\n\n# Relief from the License may be granted by purchasing a commercial license.\n\nimport argparse\nimport os\n\nimport socketio\nimport uvicorn\nfrom fastapi import Request\nfrom fastapi.templating import Jinja2Templates\n\nfrom covalent._data_store.datastore import DataStore\nfrom covalent._shared_files import logger\nfrom covalent._shared_files.config import get_config\nfrom covalent_dispatcher._service.app_dask import DaskCluster\nfrom covalent_ui.api.main import app as fastapi_app\nfrom covalent_ui.api.main import sio\n\n# read env vars configuring server\nCOVALENT_SERVER_IFACE_ANY = os.getenv(\"COVALENT_SERVER_IFACE_ANY\", \"False\").lower() in (\n    \"true\",\n    \"1\",\n    \"t\",\n)\n\nWEBHOOK_PATH = \"/api/webhook\"\nWEBAPP_PATH = \"webapp/build\"\nSTATIC_FILES = {\"\": WEBAPP_PATH, \"/\": f\"{WEBAPP_PATH}/index.html\"}\n\n# Log configuration\napp_log = logger.app_log\nlog_stack_info = logger.log_stack_info\ntemplates = Jinja2Templates(directory=WEBAPP_PATH)\n\n\n@fastapi_app.get(\"/{rest_of_path}\")\ndef get_home(request: Request, rest_of_path: str):\n    return templates.TemplateResponse(\"index.html\", {\"request\": request})\n\n\n"
}
latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"].electron[0].electronError = null
latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"].electron[0].electronInput = {
    "data": "{'args': ('[1, 1, 1]',), 'kwargs': {}}",
    "python_object": "import pickle\npickle.loads(b'\\x80\\x05\\x95%\\x00\\x00\\x00\\x00\\x00\\x00\\x00}\\x94(\\x8c\\x04args\\x94\\x8c\\t[1, 1, 1]\\x94\\x85\\x94\\x8c\\x06kwargs\\x94}\\x94u.')"
}

latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"].electron[5].electronDetails = {
    "id": 1086,
    "node_id": 0,
    "parent_lattice_id": 36,
    "type": "function",
    "storage_path": "/home/prasannavenkatesh/Desktop/workflows/results/419d22a3-e1d7-46a8-92ba-d4ef234674b0/node_0",
    "name": "identity",
    "status": "COMPLETED",
    "started_at": "2022-10-03T09:04:57",
    "ended_at": "2022-10-03T09:04:58",
    "runtime": 1000,
    "description": ""
}
latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"].electron[5].electronResult = {
    "data": "\"[1, 1, 1]\"",
    "python_object": "import pickle\npickle.loads(b'\\x80\\x05\\x95\\x0b\\x00\\x00\\x00\\x00\\x00\\x00\\x00]\\x94(K\\x01K\\x01K\\x01e.')"
}
latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"].electron[5].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"].electron[5].electronFunctionString = {
    "data": "# Copyright 2021 Agnostiq Inc.\n#\n# This file is part of Covalent.\n#\n# Licensed under the GNU Affero General Public License 3.0 (the \"License\").\n# A copy of the License may be obtained with this software package or at\n#\n#      https://www.gnu.org/licenses/agpl-3.0.en.html\n#\n# Use of this file is prohibited except in compliance with the License. Any\n# modifications or derivative works of this file must retain this copyright\n# notice, and modified files must contain a notice indicating that they have\n# been altered from the originals.\n# Covalent is distributed in the hope that it will be useful, but WITHOUT\n# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or\n# FITNESS FOR A PARTICULAR PURPOSE. See the License for more details.\n\n# Relief from the License may be granted by purchasing a commercial license.\n\nimport argparse\nimport os\n\nimport socketio\nimport uvicorn\nfrom fastapi import Request\nfrom fastapi.templating import Jinja2Templates\n\nfrom covalent._data_store.datastore import DataStore\nfrom covalent._shared_files import logger\nfrom covalent._shared_files.config import get_config\nfrom covalent_dispatcher._service.app_dask import DaskCluster\nfrom covalent_ui.api.main import app as fastapi_app\nfrom covalent_ui.api.main import sio\n\n# read env vars configuring server\nCOVALENT_SERVER_IFACE_ANY = os.getenv(\"COVALENT_SERVER_IFACE_ANY\", \"False\").lower() in (\n    \"true\",\n    \"1\",\n    \"t\",\n)\n\nWEBHOOK_PATH = \"/api/webhook\"\nWEBAPP_PATH = \"webapp/build\"\nSTATIC_FILES = {\"\": WEBAPP_PATH, \"/\": f\"{WEBAPP_PATH}/index.html\"}\n\n# Log configuration\napp_log = logger.app_log\nlog_stack_info = logger.log_stack_info\ntemplates = Jinja2Templates(directory=WEBAPP_PATH)\n\n\n@fastapi_app.get(\"/{rest_of_path}\")\ndef get_home(request: Request, rest_of_path: str):\n    return templates.TemplateResponse(\"index.html\", {\"request\": request})\n\n\n"
}
latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"].electron[5].electronError = null
latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"].electron[5].electronInput = {
    "data": "{'args': ('[1, 1, 1]',), 'kwargs': {}}",
    "python_object": "import pickle\npickle.loads(b'\\x80\\x05\\x95%\\x00\\x00\\x00\\x00\\x00\\x00\\x00}\\x94(\\x8c\\x04args\\x94\\x8c\\t[1, 1, 1]\\x94\\x85\\x94\\x8c\\x06kwargs\\x94}\\x94u.')"
}

latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"].electron[10].electronDetails = {
    "id": 1086,
    "node_id": 0,
    "parent_lattice_id": 36,
    "type": "function",
    "storage_path": "/home/prasannavenkatesh/Desktop/workflows/results/419d22a3-e1d7-46a8-92ba-d4ef234674b0/node_0",
    "name": "identity",
    "status": "COMPLETED",
    "started_at": "2022-10-03T09:04:57",
    "ended_at": "2022-10-03T09:04:58",
    "runtime": 1000,
    "description": ""
}
latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"].electron[10].electronResult = {
    "data": "\"[1, 1, 1]\"",
    "python_object": "import pickle\npickle.loads(b'\\x80\\x05\\x95\\x0b\\x00\\x00\\x00\\x00\\x00\\x00\\x00]\\x94(K\\x01K\\x01K\\x01e.')"
}
latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"].electron[10].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"].electron[10].electronFunctionString = {
    "data": "# Copyright 2021 Agnostiq Inc.\n#\n# This file is part of Covalent.\n#\n# Licensed under the GNU Affero General Public License 3.0 (the \"License\").\n# A copy of the License may be obtained with this software package or at\n#\n#      https://www.gnu.org/licenses/agpl-3.0.en.html\n#\n# Use of this file is prohibited except in compliance with the License. Any\n# modifications or derivative works of this file must retain this copyright\n# notice, and modified files must contain a notice indicating that they have\n# been altered from the originals.\n# Covalent is distributed in the hope that it will be useful, but WITHOUT\n# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or\n# FITNESS FOR A PARTICULAR PURPOSE. See the License for more details.\n\n# Relief from the License may be granted by purchasing a commercial license.\n\nimport argparse\nimport os\n\nimport socketio\nimport uvicorn\nfrom fastapi import Request\nfrom fastapi.templating import Jinja2Templates\n\nfrom covalent._data_store.datastore import DataStore\nfrom covalent._shared_files import logger\nfrom covalent._shared_files.config import get_config\nfrom covalent_dispatcher._service.app_dask import DaskCluster\nfrom covalent_ui.api.main import app as fastapi_app\nfrom covalent_ui.api.main import sio\n\n# read env vars configuring server\nCOVALENT_SERVER_IFACE_ANY = os.getenv(\"COVALENT_SERVER_IFACE_ANY\", \"False\").lower() in (\n    \"true\",\n    \"1\",\n    \"t\",\n)\n\nWEBHOOK_PATH = \"/api/webhook\"\nWEBAPP_PATH = \"webapp/build\"\nSTATIC_FILES = {\"\": WEBAPP_PATH, \"/\": f\"{WEBAPP_PATH}/index.html\"}\n\n# Log configuration\napp_log = logger.app_log\nlog_stack_info = logger.log_stack_info\ntemplates = Jinja2Templates(directory=WEBAPP_PATH)\n\n\n@fastapi_app.get(\"/{rest_of_path}\")\ndef get_home(request: Request, rest_of_path: str):\n    return templates.TemplateResponse(\"index.html\", {\"request\": request})\n\n\n"
}
latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"].electron[10].electronError = null
latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"].electron[10].electronInput = {
    "data": "{'args': ('[1, 1, 1]',), 'kwargs': {}}",
    "python_object": "import pickle\npickle.loads(b'\\x80\\x05\\x95%\\x00\\x00\\x00\\x00\\x00\\x00\\x00}\\x94(\\x8c\\x04args\\x94\\x8c\\t[1, 1, 1]\\x94\\x85\\x94\\x8c\\x06kwargs\\x94}\\x94u.')"
}

latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"].electron[1].electronDetails = {
    "id": 1087,
    "node_id": 1,
    "parent_lattice_id": 36,
    "type": "electron_list",
    "storage_path": "/home/prasannavenkatesh/Desktop/workflows/results/419d22a3-e1d7-46a8-92ba-d4ef234674b0/node_1",
    "name": ":electron_list:",
    "status": "COMPLETED",
    "started_at": "2022-10-03T09:04:57",
    "ended_at": "2022-10-03T09:04:57",
    "runtime": 0,
    "description": ""
}
latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"].electron[1].electronResult = {
    "data": "\"[1, 1, 1]\"",
    "python_object": "import pickle\npickle.loads(b'\\x80\\x05\\x95\\x0b\\x00\\x00\\x00\\x00\\x00\\x00\\x00]\\x94(K\\x01K\\x01K\\x01e.')"
}
latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"].electron[1].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"].electron[1].electronFunctionString = {
    "data": "@electron\ndef to_decoded_electron_collection(**x):\n    \"\"\"Interchanges order of serialize -> collection\"\"\"\n    collection = list(x.values())[0]\n    if isinstance(collection, list):\n        return TransportableObject.deserialize_list(collection)\n    elif isinstance(collection, dict):\n        return TransportableObject.deserialize_dict(collection)\n\n\n"
}
latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"].electron[1].electronError = null
latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"].electron[1].electronInput = {
    "data": "{'args': (), 'kwargs': {'x': '[<covalent.TransportableObject object at 0x7f497f7f7970>, <covalent.TransportableObject object at 0x7f497f7b0be0>, <covalent.TransportableObject object at 0x7f497f7b0940>]'}}",
    "python_object": "import pickle\npickle.loads(b'\\x80\\x05\\x95\\xcb\\x00\\x00\\x00\\x00\\x00\\x00\\x00}\\x94(\\x8c\\x04args\\x94)\\x8c\\x06kwargs\\x94}\\x94\\x8c\\x01x\\x94\\x8c\\xab[<covalent.TransportableObject object at 0x7f497f7f7970>, <covalent.TransportableObject object at 0x7f497f7b0be0>, <covalent.TransportableObject object at 0x7f497f7b0940>]\\x94su.')"
}

latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"].electron[6].electronDetails = {
    "id": 1087,
    "node_id": 1,
    "parent_lattice_id": 36,
    "type": "electron_list",
    "storage_path": "/home/prasannavenkatesh/Desktop/workflows/results/419d22a3-e1d7-46a8-92ba-d4ef234674b0/node_1",
    "name": ":electron_list:",
    "status": "COMPLETED",
    "started_at": "2022-10-03T09:04:57",
    "ended_at": "2022-10-03T09:04:57",
    "runtime": 0,
    "description": ""
}
latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"].electron[6].electronResult = {
    "data": "\"[1, 1, 1]\"",
    "python_object": "import pickle\npickle.loads(b'\\x80\\x05\\x95\\x0b\\x00\\x00\\x00\\x00\\x00\\x00\\x00]\\x94(K\\x01K\\x01K\\x01e.')"
}
latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"].electron[6].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"].electron[6].electronFunctionString = {
    "data": "@electron\ndef to_decoded_electron_collection(**x):\n    \"\"\"Interchanges order of serialize -> collection\"\"\"\n    collection = list(x.values())[0]\n    if isinstance(collection, list):\n        return TransportableObject.deserialize_list(collection)\n    elif isinstance(collection, dict):\n        return TransportableObject.deserialize_dict(collection)\n\n\n"
}
latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"].electron[6].electronError = null
latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"].electron[6].electronInput = {
    "data": "{'args': (), 'kwargs': {'x': '[<covalent.TransportableObject object at 0x7f497f7f7970>, <covalent.TransportableObject object at 0x7f497f7b0be0>, <covalent.TransportableObject object at 0x7f497f7b0940>]'}}",
    "python_object": "import pickle\npickle.loads(b'\\x80\\x05\\x95\\xcb\\x00\\x00\\x00\\x00\\x00\\x00\\x00}\\x94(\\x8c\\x04args\\x94)\\x8c\\x06kwargs\\x94}\\x94\\x8c\\x01x\\x94\\x8c\\xab[<covalent.TransportableObject object at 0x7f497f7f7970>, <covalent.TransportableObject object at 0x7f497f7b0be0>, <covalent.TransportableObject object at 0x7f497f7b0940>]\\x94su.')"
}

latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"].electron[11].electronDetails = {
    "id": 1087,
    "node_id": 1,
    "parent_lattice_id": 36,
    "type": "electron_list",
    "storage_path": "/home/prasannavenkatesh/Desktop/workflows/results/419d22a3-e1d7-46a8-92ba-d4ef234674b0/node_1",
    "name": ":electron_list:",
    "status": "COMPLETED",
    "started_at": "2022-10-03T09:04:57",
    "ended_at": "2022-10-03T09:04:57",
    "runtime": 0,
    "description": ""
}
latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"].electron[11].electronResult = {
    "data": "\"[1, 1, 1]\"",
    "python_object": "import pickle\npickle.loads(b'\\x80\\x05\\x95\\x0b\\x00\\x00\\x00\\x00\\x00\\x00\\x00]\\x94(K\\x01K\\x01K\\x01e.')"
}
latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"].electron[11].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"].electron[11].electronFunctionString = {
    "data": "@electron\ndef to_decoded_electron_collection(**x):\n    \"\"\"Interchanges order of serialize -> collection\"\"\"\n    collection = list(x.values())[0]\n    if isinstance(collection, list):\n        return TransportableObject.deserialize_list(collection)\n    elif isinstance(collection, dict):\n        return TransportableObject.deserialize_dict(collection)\n\n\n"
}
latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"].electron[11].electronError = null
latticeDetailsDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"].electron[11].electronInput ={
    "data": "{'args': (), 'kwargs': {'x': '[<covalent.TransportableObject object at 0x7f497f7f7970>, <covalent.TransportableObject object at 0x7f497f7b0be0>, <covalent.TransportableObject object at 0x7f497f7b0940>]'}}",
    "python_object": "import pickle\npickle.loads(b'\\x80\\x05\\x95\\xcb\\x00\\x00\\x00\\x00\\x00\\x00\\x00}\\x94(\\x8c\\x04args\\x94)\\x8c\\x06kwargs\\x94}\\x94\\x8c\\x01x\\x94\\x8c\\xab[<covalent.TransportableObject object at 0x7f497f7f7970>, <covalent.TransportableObject object at 0x7f497f7b0be0>, <covalent.TransportableObject object at 0x7f497f7b0940>]\\x94su.')"
}

export default latticeDetailsDemoData
