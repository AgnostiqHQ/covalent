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

const latticePreview = {
  lattice: {
    lattice: {
      function_string:
        '# @ct.lattice\ndef final_calc(\n    target_list=["sirius", "trappist-1"],\n    region="America/Los_Angeles",\n    latitude=49.2827,\n    longitude=-123.1207,\n):\n    """\n    Final calculation\n    """\n\n    RA = get_RA(target_list=target_list)\n    dec = get_dec(target_list=target_list)\n    T = convert_to_utc(time_zone=region)\n    d = days_since_J2000(region=region)\n    lst = local_sidereal_time(d=d, long=longitude, T=T)\n    ha = hour_angle(LST=lst, RA=RA)\n    alt = altitude_of_target(dec=dec, lat=latitude, ha=ha)\n    az = get_azimuth(dec=dec, lat=latitude, ha=ha, alt=alt)\n    return alt, az\n\n\n',
      doc: '\n    Final calculation\n    ',
      name: 'final_calc',
      kwargs: {},
      metadata: {
        backend: 'local',
        results_dir: '/home/valentin/code/agnostiq/examples/results',
      },
    },
    graph: {
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
  },
}

export default latticePreview
