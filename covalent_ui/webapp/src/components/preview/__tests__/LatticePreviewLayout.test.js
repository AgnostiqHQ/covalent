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

import App from '../LatticePreviewLayout'
import React from 'react'
import { render, screen } from '../../../testHelpers/testUtils'
import { BrowserRouter } from 'react-router-dom'
import { Provider } from 'react-redux'
import reducers from '../../../redux/reducers'
import { configureStore } from '@reduxjs/toolkit'
import { ReactFlowProvider } from 'react-flow-renderer'
import ThemeProvider from '@mui/system/ThemeProvider'
import configureMockStore from 'redux-mock-store'
import thunk from 'redux-thunk'
import theme from '../../../utils/theme'

const mockStore = configureMockStore([thunk])

function mockRender(renderedComponent) {
  const store = configureStore({
    reducer: reducers,
  })
  return render(
    <Provider store={store}>
      <ReactFlowProvider>
        <BrowserRouter>{renderedComponent}</BrowserRouter>
      </ReactFlowProvider>
    </Provider>
  )
}

function mockRenderSlice(renderedComponent) {
  const storeMock = mockStore({
    dataRes: {
      popupData: '',
    },
    latticePreview: {
      lattice: {
        function_string:
          '@ct.lattice\ndef final_calc(\n    target_list=["sirius", "trappist-1"],\n    region="America/Los_Angeles",\n    latitude=49.2827,\n    longitude=-123.1207,\n):\n    RA = get_RA(target_list=target_list)\n    dec = get_dec(target_list=target_list)\n    T = convert_to_utc(time_zone=region)\n    d = days_since_J2000(region=region)\n    lst = local_sidereal_time(d=d, long=longitude, T=T)\n    ha = hour_angle(LST=lst, RA=RA)\n    alt = altitude_of_target(dec=dec, lat=latitude, ha=ha)\n    az = get_azimuth(dec=dec, lat=latitude, ha=ha, alt=alt)\n    return alt, az\n\n\n',
        doc: 'null',
        name: 'final_calc',
        inputs: {
          target_list: "['sirius', 'trappist-1']",
          region: 'America/Los_Angeles',
          latitude: '49.2827',
          longitude: '-123.1207',
        },
        metadata: {
          executor: {
            log_stdout: 'stdout.log',
            log_stderr: 'stderr.log',
            cache_dir: '/home/kamaleshsuresh/.cache/covalent',
            time_limit: '-1',
            retries: '0',
          },
          results_dir: '/home/kamaleshsuresh/Downloads/Dispatches/results',
          workflow_executor: 'local',
          deps: {},
          call_before: [],
          call_after: [],
          executor_data: {},
          workflow_executor_data: {},
          executor_name: 'local',
        },
      },
      graph: {
        nodes: [
          {
            name: 'get_RA',
            metadata: {
              executor: {
                log_stdout: 'stdout.log',
                log_stderr: 'stderr.log',
                cache_dir: '/home/kamaleshsuresh/.cache/covalent',
                time_limit: '-1',
                retries: '0',
              },
              deps: {
                bash: "{'type': 'DepsBash', 'short_name': 'covalent', 'attributes': {'commands': [], 'apply_fn': {'type': 'TransportableObject', 'attributes': {'_object': 'gAWVNwAAAAAAAACMG2NvdmFsZW50Ll93b3JrZmxvdy5kZXBzYmFzaJSME2FwcGx5X2Jhc2hfY29tbWFuZHOUk5Qu', 'python_version': '3.8.13', 'object_string': '<function apply_bash_commands at 0x7f8921304a60>', '_json': '', 'attrs': {'doc': None, 'name': 'apply_bash_commands'}}}, 'apply_args': {'type': 'TransportableObject', 'attributes': {'_object': 'gAWVBgAAAAAAAABdlF2UYS4=', 'python_version': '3.8.13', 'object_string': '[[]]', '_json': '[[]]', 'attrs': {'doc': 'Built-in mutable sequence.\\n\\nIf no argument is given, the constructor creates a new empty list.\\nThe argument must be an iterable if specified.', 'name': ''}}}, 'apply_kwargs': {'type': 'TransportableObject', 'attributes': {'_object': 'gAV9lC4=', 'python_version': '3.8.13', 'object_string': '{}', '_json': '{}', 'attrs': {'doc': \"dict() -> new empty dictionary\\ndict(mapping) -> new dictionary initialized from a mapping object's\\n    (key, value) pairs\\ndict(iterable) -> new dictionary initialized as if via:\\n    d = {}\\n    for k, v in iterable:\\n        d[k] = v\\ndict(**kwargs) -> new dictionary initialized with the name=value pairs\\n    in the keyword argument list.  For example:  dict(one=1, two=2)\", 'name': ''}}}, 'retval_keyword': ''}}",
              },
              call_before: [],
              call_after: [],
              executor_data: {},
              executor_name: 'local',
            },
            function_string:
              '@ct.electron\ndef get_RA(target_list):\n    RA = []\n    for target_name in target_list:\n        response = requests.get(\n            "http://simbad.u-strasbg.fr/simbad/sim-id?output.format=votable&Ident=%s&output.params=ra,dec"\n            % target_name\n        )\n        star_info = response.text\n        RA.append(star_info[star_info.index("<TR><TD>") + 8 : star_info.index("</TD><TD>")])\n    RA_degs = []\n    for source in RA:\n        hour = float(source.split(" ")[0])\n        minute = float(source.split(" ")[1])\n        second = float(source.split(" ")[2])\n        RA_degs.append(((hour + minute / 60 + second / 3600) * 15))\n    return RA_degs\n\n\n',
            id: 0,
            doc: null,
            kwargs: null,
          },
          {
            name: ':electron_list:',
            metadata: {
              executor: {
                log_stdout: 'stdout.log',
                log_stderr: 'stderr.log',
                cache_dir: '/home/kamaleshsuresh/.cache/covalent',
                time_limit: '-1',
                retries: '0',
              },
              deps: {},
              call_before: [],
              call_after: [],
              workflow_executor: 'local',
              executor_data: {},
              workflow_executor_data: {},
              executor_name: 'local',
            },
            function_string:
              '@electron\ndef to_decoded_electron_collection(**x):\n    """Interchanges order of serialize -> collection"""\n    collection = list(x.values())[0]\n    if isinstance(collection, list):\n        return TransportableObject.deserialize_list(collection)\n    elif isinstance(collection, dict):\n        return TransportableObject.deserialize_dict(collection)\n\n\n',
            id: 1,
            doc: 'Interchanges order of serialize -> collection',
            kwargs: null,
          },
          {
            name: ':parameter:sirius',
            metadata: {
              executor: {
                log_stdout: 'stdout.log',
                log_stderr: 'stderr.log',
                cache_dir: '/home/kamaleshsuresh/.cache/covalent',
                time_limit: '-1',
                retries: '0',
              },
              deps: {},
              call_before: [],
              call_after: [],
              workflow_executor: 'local',
              executor_data: {},
              workflow_executor_data: {},
              executor_name: 'local',
            },
            value: 'sirius',
            id: 2,
            doc: null,
            kwargs: null,
          },
          {
            name: ':parameter:trappist-1',
            metadata: {
              executor: {
                log_stdout: 'stdout.log',
                log_stderr: 'stderr.log',
                cache_dir: '/home/kamaleshsuresh/.cache/covalent',
                time_limit: '-1',
                retries: '0',
              },
              deps: {},
              call_before: [],
              call_after: [],
              workflow_executor: 'local',
              executor_data: {},
              workflow_executor_data: {},
              executor_name: 'local',
            },
            value: 'trappist-1',
            id: 3,
            doc: null,
            kwargs: null,
          },
          {
            name: 'get_dec',
            metadata: {
              executor: {
                log_stdout: 'stdout.log',
                log_stderr: 'stderr.log',
                cache_dir: '/home/kamaleshsuresh/.cache/covalent',
                time_limit: '-1',
                retries: '0',
              },
              deps: {
                bash: "{'type': 'DepsBash', 'short_name': 'covalent', 'attributes': {'commands': [], 'apply_fn': {'type': 'TransportableObject', 'attributes': {'_object': 'gAWVNwAAAAAAAACMG2NvdmFsZW50Ll93b3JrZmxvdy5kZXBzYmFzaJSME2FwcGx5X2Jhc2hfY29tbWFuZHOUk5Qu', 'python_version': '3.8.13', 'object_string': '<function apply_bash_commands at 0x7f8921304a60>', '_json': '', 'attrs': {'doc': None, 'name': 'apply_bash_commands'}}}, 'apply_args': {'type': 'TransportableObject', 'attributes': {'_object': 'gAWVBgAAAAAAAABdlF2UYS4=', 'python_version': '3.8.13', 'object_string': '[[]]', '_json': '[[]]', 'attrs': {'doc': 'Built-in mutable sequence.\\n\\nIf no argument is given, the constructor creates a new empty list.\\nThe argument must be an iterable if specified.', 'name': ''}}}, 'apply_kwargs': {'type': 'TransportableObject', 'attributes': {'_object': 'gAV9lC4=', 'python_version': '3.8.13', 'object_string': '{}', '_json': '{}', 'attrs': {'doc': \"dict() -> new empty dictionary\\ndict(mapping) -> new dictionary initialized from a mapping object's\\n    (key, value) pairs\\ndict(iterable) -> new dictionary initialized as if via:\\n    d = {}\\n    for k, v in iterable:\\n        d[k] = v\\ndict(**kwargs) -> new dictionary initialized with the name=value pairs\\n    in the keyword argument list.  For example:  dict(one=1, two=2)\", 'name': ''}}}, 'retval_keyword': ''}}",
              },
              call_before: [],
              call_after: [],
              executor_data: {},
              executor_name: 'local',
            },
            function_string:
              '@ct.electron\ndef get_dec(target_list):\n    dec = []\n    for target_name in target_list:\n        response = requests.get(\n            "http://simbad.u-strasbg.fr/simbad/sim-id?output.format=votable&Ident=%s&output.params=ra,dec"\n            % target_name\n        )\n        star_info = response.text\n        dec.append(star_info[star_info.index("</TD><TD>") + 9 : star_info.index("</TD></TR>")])\n    dec_degs = []\n    for source in dec:\n        degree = float(source.split(" ")[0])\n        arcmin = float(source.split(" ")[1])\n        arcsec = float(source.split(" ")[2])\n        if degree < 0:\n            dec_degs.append(degree - arcmin / 60 - arcsec / 3600)\n        else:\n            dec_degs.append(degree + arcmin / 60 + arcsec / 3600)\n    return dec_degs\n\n\n',
            id: 4,
            doc: null,
            kwargs: null,
          },
          {
            name: ':electron_list:',
            metadata: {
              executor: {
                log_stdout: 'stdout.log',
                log_stderr: 'stderr.log',
                cache_dir: '/home/kamaleshsuresh/.cache/covalent',
                time_limit: '-1',
                retries: '0',
              },
              deps: {},
              call_before: [],
              call_after: [],
              workflow_executor: 'local',
              executor_data: {},
              workflow_executor_data: {},
              executor_name: 'local',
            },
            function_string:
              '@electron\ndef to_decoded_electron_collection(**x):\n    """Interchanges order of serialize -> collection"""\n    collection = list(x.values())[0]\n    if isinstance(collection, list):\n        return TransportableObject.deserialize_list(collection)\n    elif isinstance(collection, dict):\n        return TransportableObject.deserialize_dict(collection)\n\n\n',
            id: 5,
            doc: 'Interchanges order of serialize -> collection',
            kwargs: null,
          },
          {
            name: ':parameter:sirius',
            metadata: {
              executor: {
                log_stdout: 'stdout.log',
                log_stderr: 'stderr.log',
                cache_dir: '/home/kamaleshsuresh/.cache/covalent',
                time_limit: '-1',
                retries: '0',
              },
              deps: {},
              call_before: [],
              call_after: [],
              workflow_executor: 'local',
              executor_data: {},
              workflow_executor_data: {},
              executor_name: 'local',
            },
            value: 'sirius',
            id: 6,
            doc: null,
            kwargs: null,
          },
          {
            name: ':parameter:trappist-1',
            metadata: {
              executor: {
                log_stdout: 'stdout.log',
                log_stderr: 'stderr.log',
                cache_dir: '/home/kamaleshsuresh/.cache/covalent',
                time_limit: '-1',
                retries: '0',
              },
              deps: {},
              call_before: [],
              call_after: [],
              workflow_executor: 'local',
              executor_data: {},
              workflow_executor_data: {},
              executor_name: 'local',
            },
            value: 'trappist-1',
            id: 7,
            doc: null,
            kwargs: null,
          },
          {
            name: 'convert_to_utc',
            metadata: {
              executor: {
                log_stdout: 'stdout.log',
                log_stderr: 'stderr.log',
                cache_dir: '/home/kamaleshsuresh/.cache/covalent',
                time_limit: '-1',
                retries: '0',
              },
              deps: {
                bash: "{'type': 'DepsBash', 'short_name': 'covalent', 'attributes': {'commands': [], 'apply_fn': {'type': 'TransportableObject', 'attributes': {'_object': 'gAWVNwAAAAAAAACMG2NvdmFsZW50Ll93b3JrZmxvdy5kZXBzYmFzaJSME2FwcGx5X2Jhc2hfY29tbWFuZHOUk5Qu', 'python_version': '3.8.13', 'object_string': '<function apply_bash_commands at 0x7f8921304a60>', '_json': '', 'attrs': {'doc': None, 'name': 'apply_bash_commands'}}}, 'apply_args': {'type': 'TransportableObject', 'attributes': {'_object': 'gAWVBgAAAAAAAABdlF2UYS4=', 'python_version': '3.8.13', 'object_string': '[[]]', '_json': '[[]]', 'attrs': {'doc': 'Built-in mutable sequence.\\n\\nIf no argument is given, the constructor creates a new empty list.\\nThe argument must be an iterable if specified.', 'name': ''}}}, 'apply_kwargs': {'type': 'TransportableObject', 'attributes': {'_object': 'gAV9lC4=', 'python_version': '3.8.13', 'object_string': '{}', '_json': '{}', 'attrs': {'doc': \"dict() -> new empty dictionary\\ndict(mapping) -> new dictionary initialized from a mapping object's\\n    (key, value) pairs\\ndict(iterable) -> new dictionary initialized as if via:\\n    d = {}\\n    for k, v in iterable:\\n        d[k] = v\\ndict(**kwargs) -> new dictionary initialized with the name=value pairs\\n    in the keyword argument list.  For example:  dict(one=1, two=2)\", 'name': ''}}}, 'retval_keyword': ''}}",
              },
              call_before: [],
              call_after: [],
              executor_data: {},
              executor_name: 'local',
            },
            function_string:
              '@ct.electron\ndef convert_to_utc(time_zone):\n    start_time = 0\n    end_time = 24.016\n    now = datetime.now(pytz.timezone(time_zone))\n    offset = now.utcoffset().total_seconds() / 60 / 60\n    utc_timerange = np.arange(start_time - offset, end_time - offset, 0.016)\n    return utc_timerange\n\n\n',
            id: 8,
            doc: null,
            kwargs: null,
          },
          {
            name: ':parameter:America/Los_Angeles',
            metadata: {
              executor: {
                log_stdout: 'stdout.log',
                log_stderr: 'stderr.log',
                cache_dir: '/home/kamaleshsuresh/.cache/covalent',
                time_limit: '-1',
                retries: '0',
              },
              deps: {},
              call_before: [],
              call_after: [],
              workflow_executor: 'local',
              executor_data: {},
              workflow_executor_data: {},
              executor_name: 'local',
            },
            value: 'America/Los_Angeles',
            id: 9,
            doc: null,
            kwargs: null,
          },
          {
            name: 'days_since_J2000',
            metadata: {
              executor: {
                log_stdout: 'stdout.log',
                log_stderr: 'stderr.log',
                cache_dir: '/home/kamaleshsuresh/.cache/covalent',
                time_limit: '-1',
                retries: '0',
              },
              deps: {
                bash: "{'type': 'DepsBash', 'short_name': 'covalent', 'attributes': {'commands': [], 'apply_fn': {'type': 'TransportableObject', 'attributes': {'_object': 'gAWVNwAAAAAAAACMG2NvdmFsZW50Ll93b3JrZmxvdy5kZXBzYmFzaJSME2FwcGx5X2Jhc2hfY29tbWFuZHOUk5Qu', 'python_version': '3.8.13', 'object_string': '<function apply_bash_commands at 0x7f8921304a60>', '_json': '', 'attrs': {'doc': None, 'name': 'apply_bash_commands'}}}, 'apply_args': {'type': 'TransportableObject', 'attributes': {'_object': 'gAWVBgAAAAAAAABdlF2UYS4=', 'python_version': '3.8.13', 'object_string': '[[]]', '_json': '[[]]', 'attrs': {'doc': 'Built-in mutable sequence.\\n\\nIf no argument is given, the constructor creates a new empty list.\\nThe argument must be an iterable if specified.', 'name': ''}}}, 'apply_kwargs': {'type': 'TransportableObject', 'attributes': {'_object': 'gAV9lC4=', 'python_version': '3.8.13', 'object_string': '{}', '_json': '{}', 'attrs': {'doc': \"dict() -> new empty dictionary\\ndict(mapping) -> new dictionary initialized from a mapping object's\\n    (key, value) pairs\\ndict(iterable) -> new dictionary initialized as if via:\\n    d = {}\\n    for k, v in iterable:\\n        d[k] = v\\ndict(**kwargs) -> new dictionary initialized with the name=value pairs\\n    in the keyword argument list.  For example:  dict(one=1, two=2)\", 'name': ''}}}, 'retval_keyword': ''}}",
              },
              call_before: [],
              call_after: [],
              executor_data: {},
              executor_name: 'local',
            },
            function_string:
              '@ct.electron\ndef days_since_J2000(region):\n    f_date = date(2000, 1, 1)\n    year = get_date(time_zone=region)[0]\n    month = get_date(time_zone=region)[1]\n    day = get_date(time_zone=region)[2]\n    l_date = date(year, month, day)\n    delta = l_date - f_date\n    return delta.days\n\n\n',
            id: 10,
            doc: null,
            kwargs: null,
          },
          {
            name: ':parameter:America/Los_Angeles',
            metadata: {
              executor: {
                log_stdout: 'stdout.log',
                log_stderr: 'stderr.log',
                cache_dir: '/home/kamaleshsuresh/.cache/covalent',
                time_limit: '-1',
                retries: '0',
              },
              deps: {},
              call_before: [],
              call_after: [],
              workflow_executor: 'local',
              executor_data: {},
              workflow_executor_data: {},
              executor_name: 'local',
            },
            value: 'America/Los_Angeles',
            id: 11,
            doc: null,
            kwargs: null,
          },
          {
            name: 'local_sidereal_time',
            metadata: {
              executor: {
                log_stdout: 'stdout.log',
                log_stderr: 'stderr.log',
                cache_dir: '/home/kamaleshsuresh/.cache/covalent',
                time_limit: '-1',
                retries: '0',
              },
              deps: {
                bash: "{'type': 'DepsBash', 'short_name': 'covalent', 'attributes': {'commands': [], 'apply_fn': {'type': 'TransportableObject', 'attributes': {'_object': 'gAWVNwAAAAAAAACMG2NvdmFsZW50Ll93b3JrZmxvdy5kZXBzYmFzaJSME2FwcGx5X2Jhc2hfY29tbWFuZHOUk5Qu', 'python_version': '3.8.13', 'object_string': '<function apply_bash_commands at 0x7f8921304a60>', '_json': '', 'attrs': {'doc': None, 'name': 'apply_bash_commands'}}}, 'apply_args': {'type': 'TransportableObject', 'attributes': {'_object': 'gAWVBgAAAAAAAABdlF2UYS4=', 'python_version': '3.8.13', 'object_string': '[[]]', '_json': '[[]]', 'attrs': {'doc': 'Built-in mutable sequence.\\n\\nIf no argument is given, the constructor creates a new empty list.\\nThe argument must be an iterable if specified.', 'name': ''}}}, 'apply_kwargs': {'type': 'TransportableObject', 'attributes': {'_object': 'gAV9lC4=', 'python_version': '3.8.13', 'object_string': '{}', '_json': '{}', 'attrs': {'doc': \"dict() -> new empty dictionary\\ndict(mapping) -> new dictionary initialized from a mapping object's\\n    (key, value) pairs\\ndict(iterable) -> new dictionary initialized as if via:\\n    d = {}\\n    for k, v in iterable:\\n        d[k] = v\\ndict(**kwargs) -> new dictionary initialized with the name=value pairs\\n    in the keyword argument list.  For example:  dict(one=1, two=2)\", 'name': ''}}}, 'retval_keyword': ''}}",
              },
              call_before: [],
              call_after: [],
              executor_data: {},
              executor_name: 'local',
            },
            function_string:
              '@ct.electron\ndef local_sidereal_time(d, long, T):\n    LST = 100.46 + 0.985647 * (d + T / 24) + long + 15 * T\n    return LST\n\n\n',
            id: 12,
            doc: null,
            kwargs: null,
          },
          {
            name: ':parameter:-123.1207',
            metadata: {
              executor: {
                log_stdout: 'stdout.log',
                log_stderr: 'stderr.log',
                cache_dir: '/home/kamaleshsuresh/.cache/covalent',
                time_limit: '-1',
                retries: '0',
              },
              deps: {},
              call_before: [],
              call_after: [],
              workflow_executor: 'local',
              executor_data: {},
              workflow_executor_data: {},
              executor_name: 'local',
            },
            value: '-123.1207',
            id: 13,
            doc: null,
            kwargs: null,
          },
          {
            name: 'hour_angle',
            metadata: {
              executor: {
                log_stdout: 'stdout.log',
                log_stderr: 'stderr.log',
                cache_dir: '/home/kamaleshsuresh/.cache/covalent',
                time_limit: '-1',
                retries: '0',
              },
              deps: {
                bash: "{'type': 'DepsBash', 'short_name': 'covalent', 'attributes': {'commands': [], 'apply_fn': {'type': 'TransportableObject', 'attributes': {'_object': 'gAWVNwAAAAAAAACMG2NvdmFsZW50Ll93b3JrZmxvdy5kZXBzYmFzaJSME2FwcGx5X2Jhc2hfY29tbWFuZHOUk5Qu', 'python_version': '3.8.13', 'object_string': '<function apply_bash_commands at 0x7f8921304a60>', '_json': '', 'attrs': {'doc': None, 'name': 'apply_bash_commands'}}}, 'apply_args': {'type': 'TransportableObject', 'attributes': {'_object': 'gAWVBgAAAAAAAABdlF2UYS4=', 'python_version': '3.8.13', 'object_string': '[[]]', '_json': '[[]]', 'attrs': {'doc': 'Built-in mutable sequence.\\n\\nIf no argument is given, the constructor creates a new empty list.\\nThe argument must be an iterable if specified.', 'name': ''}}}, 'apply_kwargs': {'type': 'TransportableObject', 'attributes': {'_object': 'gAV9lC4=', 'python_version': '3.8.13', 'object_string': '{}', '_json': '{}', 'attrs': {'doc': \"dict() -> new empty dictionary\\ndict(mapping) -> new dictionary initialized from a mapping object's\\n    (key, value) pairs\\ndict(iterable) -> new dictionary initialized as if via:\\n    d = {}\\n    for k, v in iterable:\\n        d[k] = v\\ndict(**kwargs) -> new dictionary initialized with the name=value pairs\\n    in the keyword argument list.  For example:  dict(one=1, two=2)\", 'name': ''}}}, 'retval_keyword': ''}}",
              },
              call_before: [],
              call_after: [],
              executor_data: {},
              executor_name: 'local',
            },
            function_string:
              '@ct.electron\ndef hour_angle(LST, RA):\n    LST_list = []\n    for source in RA:\n        LST_list.append(np.asarray([value - source for value in LST]))\n    return LST_list\n\n\n',
            id: 14,
            doc: null,
            kwargs: null,
          },
          {
            name: 'altitude_of_target',
            metadata: {
              executor: {
                log_stdout: 'stdout.log',
                log_stderr: 'stderr.log',
                cache_dir: '/home/kamaleshsuresh/.cache/covalent',
                time_limit: '-1',
                retries: '0',
              },
              deps: {
                bash: "{'type': 'DepsBash', 'short_name': 'covalent', 'attributes': {'commands': [], 'apply_fn': {'type': 'TransportableObject', 'attributes': {'_object': 'gAWVNwAAAAAAAACMG2NvdmFsZW50Ll93b3JrZmxvdy5kZXBzYmFzaJSME2FwcGx5X2Jhc2hfY29tbWFuZHOUk5Qu', 'python_version': '3.8.13', 'object_string': '<function apply_bash_commands at 0x7f8921304a60>', '_json': '', 'attrs': {'doc': None, 'name': 'apply_bash_commands'}}}, 'apply_args': {'type': 'TransportableObject', 'attributes': {'_object': 'gAWVBgAAAAAAAABdlF2UYS4=', 'python_version': '3.8.13', 'object_string': '[[]]', '_json': '[[]]', 'attrs': {'doc': 'Built-in mutable sequence.\\n\\nIf no argument is given, the constructor creates a new empty list.\\nThe argument must be an iterable if specified.', 'name': ''}}}, 'apply_kwargs': {'type': 'TransportableObject', 'attributes': {'_object': 'gAV9lC4=', 'python_version': '3.8.13', 'object_string': '{}', '_json': '{}', 'attrs': {'doc': \"dict() -> new empty dictionary\\ndict(mapping) -> new dictionary initialized from a mapping object's\\n    (key, value) pairs\\ndict(iterable) -> new dictionary initialized as if via:\\n    d = {}\\n    for k, v in iterable:\\n        d[k] = v\\ndict(**kwargs) -> new dictionary initialized with the name=value pairs\\n    in the keyword argument list.  For example:  dict(one=1, two=2)\", 'name': ''}}}, 'retval_keyword': ''}}",
              },
              call_before: [],
              call_after: [],
              executor_data: {},
              executor_name: 'local',
            },
            function_string:
              '@ct.electron\ndef altitude_of_target(dec, lat, ha):\n    alt_list = []\n    lat = lat * 0.0174533\n    for i in range(len(dec)):\n        dec_i = dec[i] * 0.0174533\n        ha_i = ha[i] * 0.0174533\n        alt = np.arcsin(np.sin(dec_i) * np.sin(lat) + np.cos(dec_i) * np.cos(lat) * np.cos(ha_i))\n        alt_list.append(alt * 57.2958)\n    return alt_list\n\n\n',
            id: 15,
            doc: null,
            kwargs: null,
          },
          {
            name: ':parameter:49.2827',
            metadata: {
              executor: {
                log_stdout: 'stdout.log',
                log_stderr: 'stderr.log',
                cache_dir: '/home/kamaleshsuresh/.cache/covalent',
                time_limit: '-1',
                retries: '0',
              },
              deps: {},
              call_before: [],
              call_after: [],
              workflow_executor: 'local',
              executor_data: {},
              workflow_executor_data: {},
              executor_name: 'local',
            },
            value: '49.2827',
            id: 16,
            doc: null,
            kwargs: null,
          },
          {
            name: 'get_azimuth',
            metadata: {
              executor: {
                log_stdout: 'stdout.log',
                log_stderr: 'stderr.log',
                cache_dir: '/home/kamaleshsuresh/.cache/covalent',
                time_limit: '-1',
                retries: '0',
              },
              deps: {
                bash: "{'type': 'DepsBash', 'short_name': 'covalent', 'attributes': {'commands': [], 'apply_fn': {'type': 'TransportableObject', 'attributes': {'_object': 'gAWVNwAAAAAAAACMG2NvdmFsZW50Ll93b3JrZmxvdy5kZXBzYmFzaJSME2FwcGx5X2Jhc2hfY29tbWFuZHOUk5Qu', 'python_version': '3.8.13', 'object_string': '<function apply_bash_commands at 0x7f8921304a60>', '_json': '', 'attrs': {'doc': None, 'name': 'apply_bash_commands'}}}, 'apply_args': {'type': 'TransportableObject', 'attributes': {'_object': 'gAWVBgAAAAAAAABdlF2UYS4=', 'python_version': '3.8.13', 'object_string': '[[]]', '_json': '[[]]', 'attrs': {'doc': 'Built-in mutable sequence.\\n\\nIf no argument is given, the constructor creates a new empty list.\\nThe argument must be an iterable if specified.', 'name': ''}}}, 'apply_kwargs': {'type': 'TransportableObject', 'attributes': {'_object': 'gAV9lC4=', 'python_version': '3.8.13', 'object_string': '{}', '_json': '{}', 'attrs': {'doc': \"dict() -> new empty dictionary\\ndict(mapping) -> new dictionary initialized from a mapping object's\\n    (key, value) pairs\\ndict(iterable) -> new dictionary initialized as if via:\\n    d = {}\\n    for k, v in iterable:\\n        d[k] = v\\ndict(**kwargs) -> new dictionary initialized with the name=value pairs\\n    in the keyword argument list.  For example:  dict(one=1, two=2)\", 'name': ''}}}, 'retval_keyword': ''}}",
              },
              call_before: [],
              call_after: [],
              executor_data: {},
              executor_name: 'local',
            },
            function_string:
              '@ct.electron\ndef get_azimuth(dec, lat, ha, alt):\n    az_list = []\n    lat = round(lat * 0.0174533, 2)\n    for i in range(len(dec)):\n        azimuth = []\n        dec_i = round(dec[i] * 0.0174533, 2)\n        ha_i = ha[i] * 0.0174533\n        alt_i = alt[i] * 0.0174533\n        a = np.arccos(\n            (np.sin(dec_i) - np.sin(alt_i) * np.sin(lat)) / (np.cos(alt_i) * np.cos(lat))\n        )\n        for q in range(len(ha_i)):\n            if np.sin(ha_i[q]) < 0:\n                azimuth.append(a[q] * 57.2958)\n            else:\n                azimuth.append(360 - (a[q] * 57.2958))\n        az_list.append(np.array(azimuth))\n    return az_list\n\n\n',
            id: 17,
            doc: null,
            kwargs: null,
          },
          {
            name: ':parameter:49.2827',
            metadata: {
              executor: {
                log_stdout: 'stdout.log',
                log_stderr: 'stderr.log',
                cache_dir: '/home/kamaleshsuresh/.cache/covalent',
                time_limit: '-1',
                retries: '0',
              },
              deps: {},
              call_before: [],
              call_after: [],
              workflow_executor: 'local',
              executor_data: {},
              workflow_executor_data: {},
              executor_name: 'local',
            },
            value: '49.2827',
            id: 18,
            doc: null,
            kwargs: null,
          },
        ],
        links: [
          {
            edge_name: 'RA',
            param_type: 'kwarg',
            arg_index: null,
            source: 0,
            target: 14,
            key: 0,
          },
          {
            edge_name: 'target_list',
            param_type: 'kwarg',
            arg_index: null,
            source: 1,
            target: 0,
            key: 0,
          },
          {
            edge_name: 'target_list',
            param_type: 'kwarg',
            arg_index: 0,
            source: 2,
            target: 1,
            key: 0,
          },
          {
            edge_name: 'target_list',
            param_type: 'kwarg',
            arg_index: 1,
            source: 3,
            target: 1,
            key: 0,
          },
          {
            edge_name: 'dec',
            param_type: 'kwarg',
            arg_index: null,
            source: 4,
            target: 15,
            key: 0,
          },
          {
            edge_name: 'dec',
            param_type: 'kwarg',
            arg_index: null,
            source: 4,
            target: 17,
            key: 0,
          },
          {
            edge_name: 'target_list',
            param_type: 'kwarg',
            arg_index: null,
            source: 5,
            target: 4,
            key: 0,
          },
          {
            edge_name: 'target_list',
            param_type: 'kwarg',
            arg_index: 0,
            source: 6,
            target: 5,
            key: 0,
          },
          {
            edge_name: 'target_list',
            param_type: 'kwarg',
            arg_index: 1,
            source: 7,
            target: 5,
            key: 0,
          },
          {
            edge_name: 'T',
            param_type: 'kwarg',
            arg_index: null,
            source: 8,
            target: 12,
            key: 0,
          },
          {
            edge_name: 'time_zone',
            param_type: 'kwarg',
            arg_index: null,
            source: 9,
            target: 8,
            key: 0,
          },
          {
            edge_name: 'd',
            param_type: 'kwarg',
            arg_index: null,
            source: 10,
            target: 12,
            key: 0,
          },
          {
            edge_name: 'region',
            param_type: 'kwarg',
            arg_index: null,
            source: 11,
            target: 10,
            key: 0,
          },
          {
            edge_name: 'LST',
            param_type: 'kwarg',
            arg_index: null,
            source: 12,
            target: 14,
            key: 0,
          },
          {
            edge_name: 'long',
            param_type: 'kwarg',
            arg_index: null,
            source: 13,
            target: 12,
            key: 0,
          },
          {
            edge_name: 'ha',
            param_type: 'kwarg',
            arg_index: null,
            source: 14,
            target: 15,
            key: 0,
          },
          {
            edge_name: 'ha',
            param_type: 'kwarg',
            arg_index: null,
            source: 14,
            target: 17,
            key: 0,
          },
          {
            edge_name: 'alt',
            param_type: 'kwarg',
            arg_index: null,
            source: 15,
            target: 17,
            key: 0,
          },
          {
            edge_name: 'lat',
            param_type: 'kwarg',
            arg_index: null,
            source: 16,
            target: 15,
            key: 0,
          },
          {
            edge_name: 'lat',
            param_type: 'kwarg',
            arg_index: null,
            source: 18,
            target: 17,
            key: 0,
          },
        ],
      },
    },
  })

  return render(
    <Provider store={storeMock}>
      <ThemeProvider theme={theme}>
        <ReactFlowProvider>
          <BrowserRouter>{renderedComponent}</BrowserRouter>
        </ReactFlowProvider>
      </ThemeProvider>
    </Provider>
  )
}

describe('lattice preview layout section', () => {
  test('renders lattice preview layout', () => {
    mockRender(<App />)
    const linkElement = screen.getByTestId('logo')
    expect(linkElement).toBeInTheDocument()
  })

  test('renders logo', () => {
    mockRenderSlice(<App />)
    const linkElement = screen.getByTestId('covalentLogo')
    expect(linkElement).toBeInTheDocument()
  })

  test('renders layout not found', () => {
    mockRender(<App />)
    const linkElement = screen.getByText('Lattice preview not found.')
    expect(linkElement).toBeInTheDocument()
  })
})
