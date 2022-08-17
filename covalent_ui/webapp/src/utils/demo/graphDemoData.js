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

const graphDemoData = [];

//   Dispatch 2537c3b0-c150-441b-81c6-844e3fd88ef3

graphDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"] = {
    "dispatch_id": "2537c3b0-c150-441b-81c6-844e3fd88ef3",
    "graph": {
        nodes: [
            {
                name: 'get_RA',
                kwargs: {
                    target_list: "['sirius', 'trappist-1']",
                },
                metadata: {
                    backend: 'local',
                    executor: {
                        log_stdout: 'stdout.log',
                        log_stderr: 'stderr.log',
                        conda_env: '',
                        cache_dir: '/tmp/covalent',
                        current_env_on_conda_fail: 'False',
                        current_env: '',
                    },
                },
                function_string:
                    '# @ct.electron\ndef get_RA(target_list):\n    RA = []\n    for target_name in target_list:\n        response = requests.get(\n            "http://simbad.u-strasbg.fr/simbad/sim-id?output.format=votable&Ident=%s&output.params=ra,dec"\n            % target_name\n        )\n        star_info = response.text\n        RA.append(\n            star_info[star_info.index("<TR><TD>") + 8 : star_info.index("</TD><TD>")]\n        )\n    RA_degs = []\n    for source in RA:\n        hour = float(source.split(" ")[0])\n        minute = float(source.split(" ")[1])\n        second = float(source.split(" ")[2])\n        RA_degs.append(((hour + minute / 60 + second / 3600) * 15))\n    return RA_degs\n\n\n',
                id: 0,
                doc: null,
                status: 'COMPLETED'
            },
            {
                name: ':electron_list:',
                kwargs: {
                    target_list: "['sirius', 'trappist-1']",
                },
                metadata: {
                    backend: 'local',
                    executor: {
                        log_stdout: 'stdout.log',
                        log_stderr: 'stderr.log',
                        conda_env: '',
                        cache_dir: '/tmp/covalent',
                        current_env_on_conda_fail: 'False',
                        current_env: '',
                    },
                },
                function_string: '# to_electron_collection was not inspectable\n\n',
                id: 1,
                doc: null,
                status: 'COMPLETED'
            },
            {
                name: ':parameter:sirius',
                kwargs: {
                    target_list: 'sirius',
                },
                metadata: {
                    backend: 'local',
                    executor: {
                        log_stdout: 'stdout.log',
                        log_stderr: 'stderr.log',
                        conda_env: '',
                        cache_dir: '/tmp/covalent',
                        current_env_on_conda_fail: 'False',
                        current_env: '',
                    },
                },
                id: 2,
                doc: null,
                status: 'COMPLETED'
            },
            {
                name: ':parameter:trappist-1',
                kwargs: {
                    target_list: 'trappist-1',
                },
                metadata: {
                    backend: 'local',
                    executor: {
                        log_stdout: 'stdout.log',
                        log_stderr: 'stderr.log',
                        conda_env: '',
                        cache_dir: '/tmp/covalent',
                        current_env_on_conda_fail: 'False',
                        current_env: '',
                    },
                },
                id: 3,
                doc: null,
                status: 'COMPLETED'
            },
            {
                name: 'get_dec',
                kwargs: {
                    target_list: "['sirius', 'trappist-1']",
                },
                metadata: {
                    backend: 'local',
                    executor: {
                        log_stdout: 'stdout.log',
                        log_stderr: 'stderr.log',
                        conda_env: '',
                        cache_dir: '/tmp/covalent',
                        current_env_on_conda_fail: 'False',
                        current_env: '',
                    },
                },
                function_string:
                    '# @ct.electron\ndef get_dec(target_list):\n    dec = []\n    for target_name in target_list:\n        response = requests.get(\n            "http://simbad.u-strasbg.fr/simbad/sim-id?output.format=votable&Ident=%s&output.params=ra,dec"\n            % target_name\n        )\n        star_info = response.text\n        dec.append(\n            star_info[star_info.index("</TD><TD>") + 9 : star_info.index("</TD></TR>")]\n        )\n    dec_degs = []\n    for source in dec:\n        degree = float(source.split(" ")[0])\n        arcmin = float(source.split(" ")[1])\n        arcsec = float(source.split(" ")[2])\n        if degree < 0:\n            dec_degs.append(degree - arcmin / 60 - arcsec / 3600)\n        else:\n            dec_degs.append(degree + arcmin / 60 + arcsec / 3600)\n    return dec_degs\n\n\n',
                id: 4,
                doc: null,
                status: 'COMPLETED'
            },
            {
                name: ':electron_list:',
                kwargs: {
                    target_list: "['sirius', 'trappist-1']",
                },
                metadata: {
                    backend: 'local',
                    executor: {
                        log_stdout: 'stdout.log',
                        log_stderr: 'stderr.log',
                        conda_env: '',
                        cache_dir: '/tmp/covalent',
                        current_env_on_conda_fail: 'False',
                        current_env: '',
                    },
                },
                function_string: '# to_electron_collection was not inspectable\n\n',
                id: 5,
                doc: null,
                status: 'COMPLETED'
            },
            {
                name: ':parameter:sirius',
                kwargs: {
                    target_list: 'sirius',
                },
                metadata: {
                    backend: 'local',
                    executor: {
                        log_stdout: 'stdout.log',
                        log_stderr: 'stderr.log',
                        conda_env: '',
                        cache_dir: '/tmp/covalent',
                        current_env_on_conda_fail: 'False',
                        current_env: '',
                    },
                },
                id: 6,
                doc: null,
                status: 'COMPLETED'
            },
            {
                name: ':parameter:trappist-1',
                kwargs: {
                    target_list: 'trappist-1',
                },
                metadata: {
                    backend: 'local',
                    executor: {
                        log_stdout: 'stdout.log',
                        log_stderr: 'stderr.log',
                        conda_env: '',
                        cache_dir: '/tmp/covalent',
                        current_env_on_conda_fail: 'False',
                        current_env: '',
                    },
                },
                id: 7,
                doc: null,
                status: 'COMPLETED'
            },
            {
                name: 'convert_to_utc',
                kwargs: {
                    time_zone: 'America/Los_Angeles',
                },
                metadata: {
                    backend: 'local',
                    executor: {
                        log_stdout: 'stdout.log',
                        log_stderr: 'stderr.log',
                        conda_env: '',
                        cache_dir: '/tmp/covalent',
                        current_env_on_conda_fail: 'False',
                        current_env: '',
                    },
                },
                function_string:
                    '# @ct.electron\ndef convert_to_utc(time_zone):\n    start_time = 0\n    end_time = 24.016\n    now = datetime.now(pytz.timezone(time_zone))\n    offset = now.utcoffset().total_seconds() / 60 / 60\n    utc_timerange = np.arange(start_time - offset, end_time - offset, 0.016)\n    return utc_timerange\n\n\n',
                id: 8,
                doc: null,
                status: 'COMPLETED'
            },
            {
                name: ':parameter:America/Los_Angeles',
                kwargs: {
                    time_zone: 'America/Los_Angeles',
                },
                metadata: {
                    backend: 'local',
                    executor: {
                        log_stdout: 'stdout.log',
                        log_stderr: 'stderr.log',
                        conda_env: '',
                        cache_dir: '/tmp/covalent',
                        current_env_on_conda_fail: 'False',
                        current_env: '',
                    },
                },
                id: 9,
                doc: null,
                status: 'COMPLETED'
            },
            {
                name: 'days_since_J2000',
                kwargs: {
                    region: 'America/Los_Angeles',
                },
                metadata: {
                    backend: 'local',
                    executor: {
                        log_stdout: 'stdout.log',
                        log_stderr: 'stderr.log',
                        conda_env: '',
                        cache_dir: '/tmp/covalent',
                        current_env_on_conda_fail: 'False',
                        current_env: '',
                    },
                },
                function_string:
                    '# @ct.electron\ndef days_since_J2000(region):\n    f_date = date(2000, 1, 1)\n    year = get_date(time_zone=region)[0]\n    month = get_date(time_zone=region)[1]\n    day = get_date(time_zone=region)[2]\n    l_date = date(year, month, day)\n    delta = l_date - f_date\n    return delta.days\n\n\n',
                id: 10,
                doc: null,
                status: 'COMPLETED'
            },
            {
                name: ':parameter:America/Los_Angeles',
                kwargs: {
                    region: 'America/Los_Angeles',
                },
                metadata: {
                    backend: 'local',
                    executor: {
                        log_stdout: 'stdout.log',
                        log_stderr: 'stderr.log',
                        conda_env: '',
                        cache_dir: '/tmp/covalent',
                        current_env_on_conda_fail: 'False',
                        current_env: '',
                    },
                },
                id: 11,
                doc: null,
                status: 'COMPLETED'
            },
            {
                name: 'local_sidereal_time',
                kwargs: {
                    d: '<covalent._workflow.electron.Electron object at 0x7f839d9c3550>',
                    long: '-123.1207',
                    T: '<covalent._workflow.electron.Electron object at 0x7f839d9a8100>',
                },
                metadata: {
                    backend: 'local',
                    executor: {
                        log_stdout: 'stdout.log',
                        log_stderr: 'stderr.log',
                        conda_env: '',
                        cache_dir: '/tmp/covalent',
                        current_env_on_conda_fail: 'False',
                        current_env: '',
                    },
                },
                function_string:
                    '# @ct.electron\ndef local_sidereal_time(d, long, T):\n    LST = 100.46 + 0.985647 * (d + T / 24) + long + 15 * T\n    return LST\n\n\n',
                id: 12,
                doc: null,
                status: 'COMPLETED'
            },
            {
                name: ':parameter:-123.1207',
                kwargs: {
                    long: '-123.1207',
                },
                metadata: {
                    backend: 'local',
                    executor: {
                        log_stdout: 'stdout.log',
                        log_stderr: 'stderr.log',
                        conda_env: '',
                        cache_dir: '/tmp/covalent',
                        current_env_on_conda_fail: 'False',
                        current_env: '',
                    },
                },
                id: 13,
                doc: null,
                status: 'COMPLETED'
            },
            {
                name: 'hour_angle',
                kwargs: {
                    LST: '<covalent._workflow.electron.Electron object at 0x7f839d9c3eb0>',
                    RA: '<covalent._workflow.electron.Electron object at 0x7f839da53d00>',
                },
                metadata: {
                    backend: 'local',
                    executor: {
                        log_stdout: 'stdout.log',
                        log_stderr: 'stderr.log',
                        conda_env: '',
                        cache_dir: '/tmp/covalent',
                        current_env_on_conda_fail: 'False',
                        current_env: '',
                    },
                },
                function_string:
                    '# @ct.electron\ndef hour_angle(LST, RA):\n    LST_list = []\n    for source in RA:\n        LST_list.append(np.asarray([value - source for value in LST]))\n    return LST_list\n\n\n',
                id: 14,
                doc: null,
                status: 'COMPLETED'
            },
            {
                name: 'altitude_of_target',
                kwargs: {
                    dec: '<covalent._workflow.electron.Electron object at 0x7f839d997460>',
                    lat: '49.2827',
                    ha: '<covalent._workflow.electron.Electron object at 0x7f839d9c3b80>',
                },
                metadata: {
                    backend: 'local',
                    executor: {
                        log_stdout: 'stdout.log',
                        log_stderr: 'stderr.log',
                        conda_env: '',
                        cache_dir: '/tmp/covalent',
                        current_env_on_conda_fail: 'False',
                        current_env: '',
                    },
                },
                function_string:
                    '# @ct.electron\ndef altitude_of_target(dec, lat, ha):\n    alt_list = []\n    lat = lat * 0.0174533\n    for i in range(len(dec)):\n        dec_i = dec[i] * 0.0174533\n        ha_i = ha[i] * 0.0174533\n        alt = np.arcsin(\n            np.sin(dec_i) * np.sin(lat) + np.cos(dec_i) * np.cos(lat) * np.cos(ha_i)\n        )\n        alt_list.append(alt * 57.2958)\n    return alt_list\n\n\n',
                id: 15,
                doc: null,
                status: 'COMPLETED'
            },
            {
                name: ':parameter:49.2827',
                kwargs: {
                    lat: '49.2827',
                },
                metadata: {
                    backend: 'local',
                    executor: {
                        log_stdout: 'stdout.log',
                        log_stderr: 'stderr.log',
                        conda_env: '',
                        cache_dir: '/tmp/covalent',
                        current_env_on_conda_fail: 'False',
                        current_env: '',
                    },
                },
                id: 16,
                doc: null,
                status: 'COMPLETED'
            },
            {
                name: 'get_azimuth',
                kwargs: {
                    dec: '<covalent._workflow.electron.Electron object at 0x7f839d997460>',
                    lat: '49.2827',
                    ha: '<covalent._workflow.electron.Electron object at 0x7f839d9c3b80>',
                    alt: '<covalent._workflow.electron.Electron object at 0x7f839d9b5610>',
                },
                metadata: {
                    backend: 'local',
                    executor: {
                        log_stdout: 'stdout.log',
                        log_stderr: 'stderr.log',
                        conda_env: '',
                        cache_dir: '/tmp/covalent',
                        current_env_on_conda_fail: 'False',
                        current_env: '',
                    },
                },
                function_string:
                    '# @ct.electron\ndef get_azimuth(dec, lat, ha, alt):\n    az_list = []\n    lat = round(lat * 0.0174533, 2)\n    for i in range(len(dec)):\n        azimuth = []\n        dec_i = round(dec[i] * 0.0174533, 2)\n        ha_i = ha[i] * 0.0174533\n        alt_i = alt[i] * 0.0174533\n        a = np.arccos(\n            (np.sin(dec_i) - np.sin(alt_i) * np.sin(lat))\n            / (np.cos(alt_i) * np.cos(lat))\n        )\n        for q in range(len(ha_i)):\n            if np.sin(ha_i[q]) < 0:\n                azimuth.append(a[q] * 57.2958)\n            else:\n                azimuth.append(360 - (a[q] * 57.2958))\n        az_list.append(np.array(azimuth))\n    return az_list\n\n\n',
                id: 17,
                doc: null,
                status: 'COMPLETED'
            },
            {
                name: ':parameter:49.2827',
                kwargs: {
                    lat: '49.2827',
                },
                metadata: {
                    backend: 'local',
                    executor: {
                        log_stdout: 'stdout.log',
                        log_stderr: 'stderr.log',
                        conda_env: '',
                        cache_dir: '/tmp/covalent',
                        current_env_on_conda_fail: 'False',
                        current_env: '',
                    },
                },
                id: 18,
                doc: null,
                status: 'COMPLETED'
            },
        ],
        links: [
            {
                variable: 'RA',
                source: 0,
                target: 14,
            },
            {
                variable: 'target_list',
                source: 1,
                target: 0,
            },
            {
                variable: 'target_list',
                source: 2,
                target: 1,
            },
            {
                variable: 'target_list',
                source: 3,
                target: 1,
            },
            {
                variable: 'dec',
                source: 4,
                target: 15,
            },
            {
                variable: 'dec',
                source: 4,
                target: 17,
            },
            {
                variable: 'target_list',
                source: 5,
                target: 4,
            },
            {
                variable: 'target_list',
                source: 6,
                target: 5,
            },
            {
                variable: 'target_list',
                source: 7,
                target: 5,
            },
            {
                variable: 'T',
                source: 8,
                target: 12,
            },
            {
                variable: 'time_zone',
                source: 9,
                target: 8,
            },
            {
                variable: 'd',
                source: 10,
                target: 12,
            },
            {
                variable: 'region',
                source: 11,
                target: 10,
            },
            {
                variable: 'LST',
                source: 12,
                target: 14,
            },
            {
                variable: 'long',
                source: 13,
                target: 12,
            },
            {
                variable: 'ha',
                source: 14,
                target: 15,
            },
            {
                variable: 'ha',
                source: 14,
                target: 17,
            },
            {
                variable: 'alt',
                source: 15,
                target: 17,
            },
            {
                variable: 'lat',
                source: 16,
                target: 15,
            },
            {
                variable: 'lat',
                source: 18,
                target: 17,
            },
        ],
    },
}

// Dispatch eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a
graphDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"] = {
    "dispatch_id": "eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a",
    "graph": {
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

// Dispatch fcd385e2-7881-4bcd-862c-2ac99706d2f9
graphDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"] = {
    "dispatch_id": "fcd385e2-7881-4bcd-862c-2ac99706d2f9",
    "graph": {
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

// Dispatch b199afa5-301f-47d8-a8dc-fd78e1f5d08a
graphDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"] = {
    "dispatch_id": "b199afa5-301f-47d8-a8dc-fd78e1f5d08a",
    "graph": {
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

// Dispatch df4601e7-7658-4a14-a860-f91a35a1b453
graphDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"] = {
    "dispatch_id": "df4601e7-7658-4a14-a860-f91a35a1b453",
    "graph": {
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

//   Dispatch ba3c238c-cb92-48e8-b7b2-debeebe2e81a

graphDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"] = {
    "dispatch_id": "ba3c238c-cb92-48e8-b7b2-debeebe2e81a",
    "graph": {
        nodes: [
            {
                name: 'get_RA',
                kwargs: {
                    target_list: "['sirius', 'trappist-1']",
                },
                metadata: {
                    backend: 'local',
                    executor: {
                        log_stdout: 'stdout.log',
                        log_stderr: 'stderr.log',
                        conda_env: '',
                        cache_dir: '/tmp/covalent',
                        current_env_on_conda_fail: 'False',
                        current_env: '',
                    },
                },
                function_string:
                    '# @ct.electron\ndef get_RA(target_list):\n    RA = []\n    for target_name in target_list:\n        response = requests.get(\n            "http://simbad.u-strasbg.fr/simbad/sim-id?output.format=votable&Ident=%s&output.params=ra,dec"\n            % target_name\n        )\n        star_info = response.text\n        RA.append(\n            star_info[star_info.index("<TR><TD>") + 8 : star_info.index("</TD><TD>")]\n        )\n    RA_degs = []\n    for source in RA:\n        hour = float(source.split(" ")[0])\n        minute = float(source.split(" ")[1])\n        second = float(source.split(" ")[2])\n        RA_degs.append(((hour + minute / 60 + second / 3600) * 15))\n    return RA_degs\n\n\n',
                id: 0,
                doc: null,
                status: 'FAILED'
            },
            {
                name: ':electron_list:',
                kwargs: {
                    target_list: "['sirius', 'trappist-1']",
                },
                metadata: {
                    backend: 'local',
                    executor: {
                        log_stdout: 'stdout.log',
                        log_stderr: 'stderr.log',
                        conda_env: '',
                        cache_dir: '/tmp/covalent',
                        current_env_on_conda_fail: 'False',
                        current_env: '',
                    },
                },
                function_string: '# to_electron_collection was not inspectable\n\n',
                id: 1,
                doc: null,
                status: 'COMPLETED'
            },
            {
                name: ':parameter:sirius',
                kwargs: {
                    target_list: 'sirius',
                },
                metadata: {
                    backend: 'local',
                    executor: {
                        log_stdout: 'stdout.log',
                        log_stderr: 'stderr.log',
                        conda_env: '',
                        cache_dir: '/tmp/covalent',
                        current_env_on_conda_fail: 'False',
                        current_env: '',
                    },
                },
                id: 2,
                doc: null,
                status: 'COMPLETED'
            },
            {
                name: ':parameter:trappist-1',
                kwargs: {
                    target_list: 'trappist-1',
                },
                metadata: {
                    backend: 'local',
                    executor: {
                        log_stdout: 'stdout.log',
                        log_stderr: 'stderr.log',
                        conda_env: '',
                        cache_dir: '/tmp/covalent',
                        current_env_on_conda_fail: 'False',
                        current_env: '',
                    },
                },
                id: 3,
                doc: null,
                status: 'COMPLETED'
            },
            {
                name: 'get_dec',
                kwargs: {
                    target_list: "['sirius', 'trappist-1']",
                },
                metadata: {
                    backend: 'local',
                    executor: {
                        log_stdout: 'stdout.log',
                        log_stderr: 'stderr.log',
                        conda_env: '',
                        cache_dir: '/tmp/covalent',
                        current_env_on_conda_fail: 'False',
                        current_env: '',
                    },
                },
                function_string:
                    '# @ct.electron\ndef get_dec(target_list):\n    dec = []\n    for target_name in target_list:\n        response = requests.get(\n            "http://simbad.u-strasbg.fr/simbad/sim-id?output.format=votable&Ident=%s&output.params=ra,dec"\n            % target_name\n        )\n        star_info = response.text\n        dec.append(\n            star_info[star_info.index("</TD><TD>") + 9 : star_info.index("</TD></TR>")]\n        )\n    dec_degs = []\n    for source in dec:\n        degree = float(source.split(" ")[0])\n        arcmin = float(source.split(" ")[1])\n        arcsec = float(source.split(" ")[2])\n        if degree < 0:\n            dec_degs.append(degree - arcmin / 60 - arcsec / 3600)\n        else:\n            dec_degs.append(degree + arcmin / 60 + arcsec / 3600)\n    return dec_degs\n\n\n',
                id: 4,
                doc: null,
                status: 'COMPLETED'
            },
            {
                name: ':electron_list:',
                kwargs: {
                    target_list: "['sirius', 'trappist-1']",
                },
                metadata: {
                    backend: 'local',
                    executor: {
                        log_stdout: 'stdout.log',
                        log_stderr: 'stderr.log',
                        conda_env: '',
                        cache_dir: '/tmp/covalent',
                        current_env_on_conda_fail: 'False',
                        current_env: '',
                    },
                },
                function_string: '# to_electron_collection was not inspectable\n\n',
                id: 5,
                doc: null,
                status: 'COMPLETED'
            },
            {
                name: ':parameter:sirius',
                kwargs: {
                    target_list: 'sirius',
                },
                metadata: {
                    backend: 'local',
                    executor: {
                        log_stdout: 'stdout.log',
                        log_stderr: 'stderr.log',
                        conda_env: '',
                        cache_dir: '/tmp/covalent',
                        current_env_on_conda_fail: 'False',
                        current_env: '',
                    },
                },
                id: 6,
                doc: null,
                status: 'COMPLETED'
            },
            {
                name: ':parameter:trappist-1',
                kwargs: {
                    target_list: 'trappist-1',
                },
                metadata: {
                    backend: 'local',
                    executor: {
                        log_stdout: 'stdout.log',
                        log_stderr: 'stderr.log',
                        conda_env: '',
                        cache_dir: '/tmp/covalent',
                        current_env_on_conda_fail: 'False',
                        current_env: '',
                    },
                },
                id: 7,
                doc: null,
                status: 'COMPLETED'
            },
            {
                name: 'convert_to_utc',
                kwargs: {
                    time_zone: 'America/Los_Angeles',
                },
                metadata: {
                    backend: 'local',
                    executor: {
                        log_stdout: 'stdout.log',
                        log_stderr: 'stderr.log',
                        conda_env: '',
                        cache_dir: '/tmp/covalent',
                        current_env_on_conda_fail: 'False',
                        current_env: '',
                    },
                },
                function_string:
                    '# @ct.electron\ndef convert_to_utc(time_zone):\n    start_time = 0\n    end_time = 24.016\n    now = datetime.now(pytz.timezone(time_zone))\n    offset = now.utcoffset().total_seconds() / 60 / 60\n    utc_timerange = np.arange(start_time - offset, end_time - offset, 0.016)\n    return utc_timerange\n\n\n',
                id: 8,
                doc: null,
                status: 'COMPLETED'
            },
            {
                name: ':parameter:America/Los_Angeles',
                kwargs: {
                    time_zone: 'America/Los_Angeles',
                },
                metadata: {
                    backend: 'local',
                    executor: {
                        log_stdout: 'stdout.log',
                        log_stderr: 'stderr.log',
                        conda_env: '',
                        cache_dir: '/tmp/covalent',
                        current_env_on_conda_fail: 'False',
                        current_env: '',
                    },
                },
                id: 9,
                doc: null,
                status: 'COMPLETED'
            },
            {
                name: 'days_since_J2000',
                kwargs: {
                    region: 'America/Los_Angeles',
                },
                metadata: {
                    backend: 'local',
                    executor: {
                        log_stdout: 'stdout.log',
                        log_stderr: 'stderr.log',
                        conda_env: '',
                        cache_dir: '/tmp/covalent',
                        current_env_on_conda_fail: 'False',
                        current_env: '',
                    },
                },
                function_string:
                    '# @ct.electron\ndef days_since_J2000(region):\n    f_date = date(2000, 1, 1)\n    year = get_date(time_zone=region)[0]\n    month = get_date(time_zone=region)[1]\n    day = get_date(time_zone=region)[2]\n    l_date = date(year, month, day)\n    delta = l_date - f_date\n    return delta.days\n\n\n',
                id: 10,
                doc: null,
                status: 'COMPLETED'
            },
            {
                name: ':parameter:America/Los_Angeles',
                kwargs: {
                    region: 'America/Los_Angeles',
                },
                metadata: {
                    backend: 'local',
                    executor: {
                        log_stdout: 'stdout.log',
                        log_stderr: 'stderr.log',
                        conda_env: '',
                        cache_dir: '/tmp/covalent',
                        current_env_on_conda_fail: 'False',
                        current_env: '',
                    },
                },
                id: 11,
                doc: null,
                status: 'COMPLETED'
            },
            {
                name: 'local_sidereal_time',
                kwargs: {
                    d: '<covalent._workflow.electron.Electron object at 0x7f839d9c3550>',
                    long: '-123.1207',
                    T: '<covalent._workflow.electron.Electron object at 0x7f839d9a8100>',
                },
                metadata: {
                    backend: 'local',
                    executor: {
                        log_stdout: 'stdout.log',
                        log_stderr: 'stderr.log',
                        conda_env: '',
                        cache_dir: '/tmp/covalent',
                        current_env_on_conda_fail: 'False',
                        current_env: '',
                    },
                },
                function_string:
                    '# @ct.electron\ndef local_sidereal_time(d, long, T):\n    LST = 100.46 + 0.985647 * (d + T / 24) + long + 15 * T\n    return LST\n\n\n',
                id: 12,
                doc: null,
                status: 'COMPLETED'
            },
            {
                name: ':parameter:-123.1207',
                kwargs: {
                    long: '-123.1207',
                },
                metadata: {
                    backend: 'local',
                    executor: {
                        log_stdout: 'stdout.log',
                        log_stderr: 'stderr.log',
                        conda_env: '',
                        cache_dir: '/tmp/covalent',
                        current_env_on_conda_fail: 'False',
                        current_env: '',
                    },
                },
                id: 13,
                doc: null,
                status: 'COMPLETED'
            },
            {
                name: 'hour_angle',
                kwargs: {
                    LST: '<covalent._workflow.electron.Electron object at 0x7f839d9c3eb0>',
                    RA: '<covalent._workflow.electron.Electron object at 0x7f839da53d00>',
                },
                metadata: {
                    backend: 'local',
                    executor: {
                        log_stdout: 'stdout.log',
                        log_stderr: 'stderr.log',
                        conda_env: '',
                        cache_dir: '/tmp/covalent',
                        current_env_on_conda_fail: 'False',
                        current_env: '',
                    },
                },
                function_string:
                    '# @ct.electron\ndef hour_angle(LST, RA):\n    LST_list = []\n    for source in RA:\n        LST_list.append(np.asarray([value - source for value in LST]))\n    return LST_list\n\n\n',
                id: 14,
                doc: null,
                status: 'PENDING'
            },
            {
                name: 'altitude_of_target',
                kwargs: {
                    dec: '<covalent._workflow.electron.Electron object at 0x7f839d997460>',
                    lat: '49.2827',
                    ha: '<covalent._workflow.electron.Electron object at 0x7f839d9c3b80>',
                },
                metadata: {
                    backend: 'local',
                    executor: {
                        log_stdout: 'stdout.log',
                        log_stderr: 'stderr.log',
                        conda_env: '',
                        cache_dir: '/tmp/covalent',
                        current_env_on_conda_fail: 'False',
                        current_env: '',
                    },
                },
                function_string:
                    '# @ct.electron\ndef altitude_of_target(dec, lat, ha):\n    alt_list = []\n    lat = lat * 0.0174533\n    for i in range(len(dec)):\n        dec_i = dec[i] * 0.0174533\n        ha_i = ha[i] * 0.0174533\n        alt = np.arcsin(\n            np.sin(dec_i) * np.sin(lat) + np.cos(dec_i) * np.cos(lat) * np.cos(ha_i)\n        )\n        alt_list.append(alt * 57.2958)\n    return alt_list\n\n\n',
                id: 15,
                doc: null,
                status: 'PENDING'
            },
            {
                name: ':parameter:49.2827',
                kwargs: {
                    lat: '49.2827',
                },
                metadata: {
                    backend: 'local',
                    executor: {
                        log_stdout: 'stdout.log',
                        log_stderr: 'stderr.log',
                        conda_env: '',
                        cache_dir: '/tmp/covalent',
                        current_env_on_conda_fail: 'False',
                        current_env: '',
                    },
                },
                id: 16,
                doc: null,
                status: 'COMPLETED'
            },
            {
                name: 'get_azimuth',
                kwargs: {
                    dec: '<covalent._workflow.electron.Electron object at 0x7f839d997460>',
                    lat: '49.2827',
                    ha: '<covalent._workflow.electron.Electron object at 0x7f839d9c3b80>',
                    alt: '<covalent._workflow.electron.Electron object at 0x7f839d9b5610>',
                },
                metadata: {
                    backend: 'local',
                    executor: {
                        log_stdout: 'stdout.log',
                        log_stderr: 'stderr.log',
                        conda_env: '',
                        cache_dir: '/tmp/covalent',
                        current_env_on_conda_fail: 'False',
                        current_env: '',
                    },
                },
                function_string:
                    '# @ct.electron\ndef get_azimuth(dec, lat, ha, alt):\n    az_list = []\n    lat = round(lat * 0.0174533, 2)\n    for i in range(len(dec)):\n        azimuth = []\n        dec_i = round(dec[i] * 0.0174533, 2)\n        ha_i = ha[i] * 0.0174533\n        alt_i = alt[i] * 0.0174533\n        a = np.arccos(\n            (np.sin(dec_i) - np.sin(alt_i) * np.sin(lat))\n            / (np.cos(alt_i) * np.cos(lat))\n        )\n        for q in range(len(ha_i)):\n            if np.sin(ha_i[q]) < 0:\n                azimuth.append(a[q] * 57.2958)\n            else:\n                azimuth.append(360 - (a[q] * 57.2958))\n        az_list.append(np.array(azimuth))\n    return az_list\n\n\n',
                id: 17,
                doc: null,
                status: 'PENDING'
            },
            {
                name: ':parameter:49.2827',
                kwargs: {
                    lat: '49.2827',
                },
                metadata: {
                    backend: 'local',
                    executor: {
                        log_stdout: 'stdout.log',
                        log_stderr: 'stderr.log',
                        conda_env: '',
                        cache_dir: '/tmp/covalent',
                        current_env_on_conda_fail: 'False',
                        current_env: '',
                    },
                },
                id: 18,
                doc: null,
                status: 'COMPLETED'
            },
        ],
        links: [
            {
                variable: 'RA',
                source: 0,
                target: 14,
            },
            {
                variable: 'target_list',
                source: 1,
                target: 0,
            },
            {
                variable: 'target_list',
                source: 2,
                target: 1,
            },
            {
                variable: 'target_list',
                source: 3,
                target: 1,
            },
            {
                variable: 'dec',
                source: 4,
                target: 15,
            },
            {
                variable: 'dec',
                source: 4,
                target: 17,
            },
            {
                variable: 'target_list',
                source: 5,
                target: 4,
            },
            {
                variable: 'target_list',
                source: 6,
                target: 5,
            },
            {
                variable: 'target_list',
                source: 7,
                target: 5,
            },
            {
                variable: 'T',
                source: 8,
                target: 12,
            },
            {
                variable: 'time_zone',
                source: 9,
                target: 8,
            },
            {
                variable: 'd',
                source: 10,
                target: 12,
            },
            {
                variable: 'region',
                source: 11,
                target: 10,
            },
            {
                variable: 'LST',
                source: 12,
                target: 14,
            },
            {
                variable: 'long',
                source: 13,
                target: 12,
            },
            {
                variable: 'ha',
                source: 14,
                target: 15,
            },
            {
                variable: 'ha',
                source: 14,
                target: 17,
            },
            {
                variable: 'alt',
                source: 15,
                target: 17,
            },
            {
                variable: 'lat',
                source: 16,
                target: 15,
            },
            {
                variable: 'lat',
                source: 18,
                target: 17,
            },
        ],
    },
}
export default graphDemoData
