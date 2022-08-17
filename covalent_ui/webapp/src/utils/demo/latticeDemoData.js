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
    "lattice_name": "final_calc",
    "runtime": 1000,
    "total_electrons": 10,
    "total_electrons_completed": 10,
    "started_at": "2022-08-11T12:14:39",
    "ended_at": "2022-08-11T12:14:40",
    "status": "COMPLETED",
    "updated_at": "2022-08-11T12:14:40",
    "directory": "/home/covalent/Desktop/workflows/results/2537c3b0-c150-441b-81c6-844e3fd88ef3",
};
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].latticeError = null;
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].latticeResult = {
    "data": "\"[19.30560599 19.22910799 19.1520599  ... 19.14461197 19.0669631218.98876836],[-35.96235506 -36.07771597 -36.1925922  ... -36.20362793 -36.31796856 -36.43181675],[209.39040932 209.61808842 209.84549899 ... 209.86738212 210.09449597 210.32133708],[312.26474717 312.52275968 312.78145573 ... 312.80640174 313.06584912 313.32598355]\""
};
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].latticeInput = null;
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].latticeFunctionString = {
    "data": '# @ct.lattice\ndef final_calc(\n    target_list=["sirius", "trappist-1"],\n    region="America/Los_Angeles",\n    latitude=49.2827,\n    longitude=-123.1207,\n):\n    RA = get_RA(target_list=target_list)\n    dec = get_dec(target_list=target_list)\n    T = convert_to_utc(time_zone=region)\n    d = days_since_J2000(region=region)\n    lst = local_sidereal_time(d=d, long=longitude, T=T)\n    ha = hour_angle(LST=lst, RA=RA)\n    alt = altitude_of_target(dec=dec, lat=latitude, ha=ha)\n    az = get_azimuth(dec=dec, lat=latitude, ha=ha, alt=alt)\n    return alt, az\n\n\n',
};
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].latticeExecutor = {
    "executor_name": "dask",
    "executor_details": "log_stdout: stdout.log\n    log_stderr: stderr.log\n   cache_dir: /tmp/covalent\n    current_env_on_conda_fail: False"
};
// electron data initilisation
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron = []
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[0] = {}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[1] = {}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[4] = {}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[5] = {}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[8] = {}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[10] = {}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[12] = {}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[14] = {}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[15] = {}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[17] = {}

latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[0].electronDetails = {
    "id": 0,
    "node_id": 0,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/2537c3b0-c150-441b-81c6-844e3fd88ef3/node_4",
    "name": "get_RA",
    "status": "COMPLETED",
    "started_at": "2022-08-11T12:14:39",
    "ended_at": "2022-08-11T12:14:39",
    "runtime": 50
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[0].electronResult = {
    "data": "101.28715533333333,346.6223687285788"
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[0].electronExecutor = {
    "executor_name": "dask",
    "executor_details": null
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[0].electronFunctionString = {
    "data": '# @ct.electron\ndef get_RA(target_list):\n    RA = []\n    for target_name in target_list:\n        response = requests.get(\n            "http://simbad.u-strasbg.fr/simbad/sim-id?output.format=votable&Ident=%s&output.params=ra,dec"\n            % target_name\n        )\n        star_info = response.text\n        RA.append(\n            star_info[star_info.index("<TR><TD>") + 8 : star_info.index("</TD><TD>")]\n        )\n    RA_degs = []\n    for source in RA:\n        hour = float(source.split(" ")[0])\n        minute = float(source.split(" ")[1])\n        second = float(source.split(" ")[2])\n        RA_degs.append(((hour + minute / 60 + second / 3600) * 15))\n    return RA_degs\n\n\n'
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[0].electronError = null
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[0].electronInput = {
    "data": "target_list=['sirius','trappist-1']"
}

latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[1].electronDetails = {
    "id": 1,
    "node_id": 1,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/2537c3b0-c150-441b-81c6-844e3fd88ef3/node_4",
    "name": ":electron_list:",
    "status": "COMPLETED",
    "started_at": "2022-08-11T12:14:39",
    "ended_at": "2022-08-11T12:14:39",
    "runtime": 50
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[1].electronResult = {
    "data": "sirius,trappist-1"
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[1].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[1].electronFunctionString = {
    "data": '# to_electron_collection was not inspectable\n\n',
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[1].electronError = null
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[1].electronInput = {
    "data": "target_list=['sirius','trappist-1']"
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[4].electronDetails = {
    "id": 4,
    "node_id": 4,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/2537c3b0-c150-441b-81c6-844e3fd88ef3/node_4",
    "name": "get_dec",
    "status": "COMPLETED",
    "started_at": "2022-08-11T12:14:39",
    "ended_at": "2022-08-11T12:14:39",
    "runtime": 50
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[4].electronResult = {
    "data": "-16.71611586111111,-5.041399250518333"
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[4].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[4].electronFunctionString = {
    "data": '# @ct.electron\ndef get_dec(target_list):\n    dec = []\n    for target_name in target_list:\n        response = requests.get(\n            "http://simbad.u-strasbg.fr/simbad/sim-id?output.format=votable&Ident=%s&output.params=ra,dec"\n            % target_name\n        )\n        star_info = response.text\n        dec.append(\n            star_info[star_info.index("</TD><TD>") + 9 : star_info.index("</TD></TR>")]\n        )\n    dec_degs = []\n    for source in dec:\n        degree = float(source.split(" ")[0])\n        arcmin = float(source.split(" ")[1])\n        arcsec = float(source.split(" ")[2])\n        if degree < 0:\n            dec_degs.append(degree - arcmin / 60 - arcsec / 3600)\n        else:\n            dec_degs.append(degree + arcmin / 60 + arcsec / 3600)\n    return dec_degs\n\n\n',
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[4].electronError = null
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[4].electronInput = {
    "data": "target_list=['sirius','trappist-1']"
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[5].electronDetails = {
    "id": 5,
    "node_id": 5,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/2537c3b0-c150-441b-81c6-844e3fd88ef3/node_4",
    "name": ":electron_list:",
    "status": "COMPLETED",
    "started_at": "2022-08-11T12:14:39",
    "ended_at": "2022-08-11T12:14:39",
    "runtime": 50
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[5].electronResult = {
    "data": "sirius,trappist-1"
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[5].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[5].electronFunctionString = {
    "data": '# to_electron_collection was not inspectable\n\n',
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[5].electronError = null
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[5].electronInput = {
    "data": "target_list=['sirius','trappist-1']"
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[8].electronDetails = {
    "id": 8,
    "node_id": 8,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/2537c3b0-c150-441b-81c6-844e3fd88ef3/node_4",
    "name": "convert_to_utc",
    "status": "COMPLETED",
    "started_at": "2022-08-11T12:14:39",
    "ended_at": "2022-08-11T12:14:39",
    "runtime": 50
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[8].electronResult = {
    "data": "[ 8.     8.016  8.032 ... 31.968 31.984 32.   ]"
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[8].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[8].electronFunctionString = {
    "data": '# @ct.electron\ndef convert_to_utc(time_zone):\n    start_time = 0\n    end_time = 24.016\n    now = datetime.now(pytz.timezone(time_zone))\n    offset = now.utcoffset().total_seconds() / 60 / 60\n    utc_timerange = np.arange(start_time - offset, end_time - offset, 0.016)\n    return utc_timerange\n\n\n',
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[8].electronError = null
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[8].electronInput = {
    "data": "time_zone=America/Los_Angeles"
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[10].electronDetails = {
    "id": 10,
    "node_id": 10,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/2537c3b0-c150-441b-81c6-844e3fd88ef3/node_4",
    "name": "days_since_J2000",
    "status": "COMPLETED",
    "started_at": "2022-08-11T12:14:39",
    "ended_at": "2022-08-11T12:14:39",
    "runtime": 50
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[10].electronResult = {
    "data": "8068"
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[10].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[10].electronFunctionString = {
    "data": '# @ct.electron\ndef days_since_J2000(region):\n    f_date = date(2000, 1, 1)\n    year = get_date(time_zone=region)[0]\n    month = get_date(time_zone=region)[1]\n    day = get_date(time_zone=region)[2]\n    l_date = date(year, month, day)\n    delta = l_date - f_date\n    return delta.days\n\n\n'
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[10].electronError = null
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[10].electronInput = {
    "data": "region=America/Los_Angeles"
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[12].electronDetails = {
    "id": 12,
    "node_id": 12,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/2537c3b0-c150-441b-81c6-844e3fd88ef3/node_4",
    "name": "local_sidereal_time",
    "status": "COMPLETED",
    "started_at": "2022-08-11T12:14:39",
    "ended_at": "2022-08-11T12:14:39",
    "runtime": 50
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[12].electronResult = {
    "data": "[8049.867845  8050.1085021 8050.3491592 ... 8410.3721778 8410.6128349 8410.853492 ]"
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[12].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[12].electronFunctionString = {
    "data": '# @ct.electron\ndef local_sidereal_time(d, long, T):\n    LST = 100.46 + 0.985647 * (d + T / 24) + long + 15 * T\n    return LST\n\n\n',
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[12].electronError = null
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[12].electronInput = {
    "data": "d=8068, long=-123.1207, T=[ 8.     8.016  8.032 ... 31.968 31.984 32.   ]"
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[14].electronDetails = {
    "id": 14,
    "node_id": 14,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/2537c3b0-c150-441b-81c6-844e3fd88ef3/node_4",
    "name": "hour_angle",
    "status": "COMPLETED",
    "started_at": "2022-08-11T12:14:39",
    "ended_at": "2022-08-11T12:14:39",
    "runtime": 50
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[14].electronResult = {
    "data": "[7948.58068967 7948.82134676 7949.06200386 ... 8309.08502247 8309.32567957   8309.56633667],[7703.24547627 7703.48613337 7703.72679047 ... 8063.74980908 8063.99046617  8064.23112327]"
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[14].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[14].electronFunctionString = {
    "data": '# @ct.electron\ndef hour_angle(LST, RA):\n    LST_list = []\n    for source in RA:\n        LST_list.append(np.asarray([value - source for value in LST]))\n    return LST_list\n\n\n',
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[14].electronError = null
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[14].electronInput = {
    "data": "LST=[8049.867845  8050.1085021 8050.3491592 ... 8410.3721778 8410.6128349 \n 8410.853492 ], RA=[101.28715533333333, 346.6223687285788]"
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[15].electronDetails = {
    "id": 15,
    "node_id": 15,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/2537c3b0-c150-441b-81c6-844e3fd88ef3/node_4",
    "name": "altitude_of_target",
    "status": "COMPLETED",
    "started_at": "2022-08-11T12:14:39",
    "ended_at": "2022-08-11T12:14:39",
    "runtime": 50
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[15].electronResult = {
    "data": "[19.30560599 19.22910799 19.1520599  ... 19.14461197 19.06696312        18.98876836],[-35.96235506 -36.07771597 -36.1925922  ... -36.20362793 -36.31796856 -36.43181675]"
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[15].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[15].electronFunctionString = {
    "data": '# @ct.electron\ndef altitude_of_target(dec, lat, ha):\n    alt_list = []\n    lat = lat * 0.0174533\n    for i in range(len(dec)):\n        dec_i = dec[i] * 0.0174533\n        ha_i = ha[i] * 0.0174533\n        alt = np.arcsin(\n            np.sin(dec_i) * np.sin(lat) + np.cos(dec_i) * np.cos(lat) * np.cos(ha_i)\n        )\n        alt_list.append(alt * 57.2958)\n    return alt_list\n\n\n',
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[15].electronError = null
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[15].electronInput = {
    "data": "dec=[-16.71611586111111, -5.041399250518333], lat=49.2827, ha=[array([7948.58068967, 7948.82134676, 7949.06200386, ..., 8309.08502247, \n 8309.32567957, 8309.56633667]), array([7703.24547627, 7703.48613337, 7703.72679047, ..., 8063.74980908,8063.99046617, 8064.23112327])]"
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[17].electronDetails = {
    "id": 17,
    "node_id": 17,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/2537c3b0-c150-441b-81c6-844e3fd88ef3/node_4",
    "name": "get_azimuth",
    "status": "COMPLETED",
    "started_at": "2022-08-11T12:14:39",
    "ended_at": "2022-08-11T12:14:39",
    "runtime": 50
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[17].electronResult = {
    "data": "[209.39040932 209.61808842 209.84549899 ... 209.86738212 210.09449597 210.32133708],[312.26474717 312.52275968 312.78145573 ... 312.80640174 313.06584912 313.32598355]"
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[14].electronExecutor = {
    "executor_name": "local",
    "executor_details": null
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[17].electronFunctionString = {
    "data": '# @ct.electron\ndef get_azimuth(dec, lat, ha, alt):\n    az_list = []\n    lat = round(lat * 0.0174533, 2)\n    for i in range(len(dec)):\n        azimuth = []\n        dec_i = round(dec[i] * 0.0174533, 2)\n        ha_i = ha[i] * 0.0174533\n        alt_i = alt[i] * 0.0174533\n        a = np.arccos(\n            (np.sin(dec_i) - np.sin(alt_i) * np.sin(lat))\n            / (np.cos(alt_i) * np.cos(lat))\n        )\n        for q in range(len(ha_i)):\n            if np.sin(ha_i[q]) < 0:\n                azimuth.append(a[q] * 57.2958)\n            else:\n                azimuth.append(360 - (a[q] * 57.2958))\n        az_list.append(np.array(azimuth))\n    return az_list\n\n\n',
}
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[17].electronError = null
latticeDetailsDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"].electron[17].electronInput = {
    "data": "dec=[-16.71611586111111, -5.041399250518333], lat=49.2827, ha=[array([7948.58068967, 7948.82134676, 7949.06200386, ..., 8309.08502247,8309.32567957, 8309.56633667]), array([7703.24547627, 7703.48613337, 7703.72679047, ..., 8063.74980908,8063.99046617, 8064.23112327])], alt=[array([19.30560599, 19.22910799, 19.1520599 , ..., 19.14461197,19.06696312, 18.98876836]), array([-35.96235506, -36.07771597, -36.1925922 , ..., -36.20362793, -36.31796856, -36.43181675])]"
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
    "data": "target_list=['sirius','trappist-1']"
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
    "data": "sirius,trappist-1"
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
    "data": "target_list=['sirius','trappist-1']"
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
    "data": "-16.71611586111111,-5.041399250518333"
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
    "data": "target_list=['sirius','trappist-1']"
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
    "data": "sirius,trappist-1"
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
    "data": "target_list=['sirius','trappist-1']"
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
    "data": "[ 8.     8.016  8.032 ... 31.968 31.984 32.   ]"
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
    "data": "time_zone=America/Los_Angeles"
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
    "data": "8068"
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
    "data": "region=America/Los_Angeles"
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
    "data": "[8049.867845  8050.1085021 8050.3491592 ... 8410.3721778 8410.6128349 8410.853492 ]"
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
    "data": "d=8068, long=-123.1207, T=[ 8.     8.016  8.032 ... 31.968 31.984 32.   ]"
}
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[14].electronDetails = {
    "id": 14,
    "node_id": 14,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/ba3c238c-cb92-48e8-b7b2-debeebe2e81a/node_4",
    "name": "hour_angle",
    "status": "COMPLETED",
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
    "data": "LST=[8049.867845  8050.1085021 8050.3491592 ... 8410.3721778 8410.6128349 \n 8410.853492 ], RA=[101.28715533333333, 346.6223687285788]"
}
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[15].electronDetails = {
    "id": 15,
    "node_id": 15,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/ba3c238c-cb92-48e8-b7b2-debeebe2e81a/node_4",
    "name": "altitude_of_target",
    "status": "COMPLETED",
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
    "data": "dec=[-16.71611586111111, -5.041399250518333], lat=49.2827, ha=[array([7948.58068967, 7948.82134676, 7949.06200386, ..., 8309.08502247, \n 8309.32567957, 8309.56633667]), array([7703.24547627, 7703.48613337, 7703.72679047, ..., 8063.74980908,8063.99046617, 8064.23112327])]"
}
latticeDetailsDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"].electron[17].electronDetails = {
    "id": 17,
    "node_id": 17,
    "parent_lattice_id": 1,
    "type": "function",
    "storage_path": "/home/covalent/Desktop/workflows/results/ba3c238c-cb92-48e8-b7b2-debeebe2e81a/node_4",
    "name": "get_azimuth",
    "status": "COMPLETED",
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
    "data": "dec=[-16.71611586111111, -5.041399250518333], lat=49.2827, ha=[array([7948.58068967, 7948.82134676, 7949.06200386, ..., 8309.08502247,8309.32567957, 8309.56633667]), array([7703.24547627, 7703.48613337, 7703.72679047, ..., 8063.74980908,8063.99046617, 8064.23112327])], alt=[array([19.30560599, 19.22910799, 19.1520599 , ..., 19.14461197,19.06696312, 18.98876836]), array([-35.96235506, -36.07771597, -36.1925922 , ..., -36.20362793, -36.31796856, -36.43181675])]"
}
export default latticeDetailsDemoData
