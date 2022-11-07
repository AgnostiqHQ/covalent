// /**
//  * Copyright 2021 Agnostiq Inc.
//  *
//  * This file is part of Covalent.
//  *
//  * Licensed under the GNU Affero General Public License 3.0 (the "License").
//  * A copy of the License may be obtained with this software package or at
//  *
//  *      https://www.gnu.org/licenses/agpl-3.0.en.html
//  *
//  * Use of this file is prohibited except in compliance with the License. Any
//  * modifications or derivative works of this file must retain this copyright
//  * notice, and modified files must contain a notice indicating that they have
//  * been altered from the originals.
//  *
//  * Covalent is distributed in the hope that it will be useful, but WITHOUT
//  * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
//  * FITNESS FOR A PARTICULAR PURPOSE. See the License for more details.
//  *
//  * Relief from the License may be granted by purchasing a commercial license.
//  */

import { render } from '@testing-library/react'
import { layoutElk as App } from '../LayoutElk'
import { BrowserRouter } from 'react-router-dom'
import React from 'react'
import { Provider } from 'react-redux'
import reducers from '../../../redux/reducers'
import { configureStore } from '@reduxjs/toolkit'
import theme from '../../../utils/theme'
import ThemeProvider from '@mui/system/ThemeProvider'
import { HelmetProvider } from 'react-helmet-async'
import { ReactFlowProvider } from 'react-flow-renderer'

function reduxRender(renderedComponent) {
  const store = configureStore({
    reducer: reducers,
  })
  return render(
    <Provider store={store}>
      <HelmetProvider>
        <ReactFlowProvider>
          <ThemeProvider theme={theme}>
            <BrowserRouter>{renderedComponent}</BrowserRouter>
          </ThemeProvider>
        </ReactFlowProvider>
      </HelmetProvider>
    </Provider>
  )
}

const graph = {
  nodes: [
    {
      id: 138,
      name: 'make_ag_crystal',
      node_id: 0,
      started_at: '2022-10-27 07:14:43.087549',
      completed_at: '2022-10-27 07:14:43.154272',
      status: 'COMPLETED',
      type: 'function',
      executor_label: 'local',
      sublattice_dispatch_id: null,
    },
    {
      id: 139,
      name: ':parameter:0.95',
      node_id: 1,
      started_at: '2022-10-27 07:14:42.730673',
      completed_at: '2022-10-27 07:14:42.730678',
      status: 'COMPLETED',
      type: 'parameter',
      executor_label: 'local',
      sublattice_dispatch_id: null,
    },
    {
      id: 140,
      name: 'compute_energy',
      node_id: 2,
      started_at: '2022-10-27 07:14:43.589235',
      completed_at: '2022-10-27 07:14:43.695388',
      status: 'FAILED',
      type: 'function',
      executor_label: 'local',
      sublattice_dispatch_id: null,
    },
    {
      id: 141,
      name: 'make_ag_crystal',
      node_id: 3,
      started_at: '2022-10-27 07:14:43.111271',
      completed_at: '2022-10-27 07:14:43.190705',
      status: 'COMPLETED',
      type: 'function',
      executor_label: 'local',
      sublattice_dispatch_id: null,
    },
    {
      id: 142,
      name: ':parameter:0.9655555555555555',
      node_id: 4,
      started_at: '2022-10-27 07:14:42.767030',
      completed_at: '2022-10-27 07:14:42.767033',
      status: 'COMPLETED',
      type: 'parameter',
      executor_label: 'local',
      sublattice_dispatch_id: null,
    },
    {
      id: 143,
      name: 'compute_energy',
      node_id: 5,
      started_at: '2022-10-27 07:14:43.673084',
      completed_at: '2022-10-27 07:14:43.752662',
      status: 'FAILED',
      type: 'function',
      executor_label: 'local',
      sublattice_dispatch_id: null,
    },
    {
      id: 144,
      name: 'make_ag_crystal',
      node_id: 6,
      started_at: '2022-10-27 07:14:43.137098',
      completed_at: '2022-10-27 07:14:43.269907',
      status: 'COMPLETED',
      type: 'function',
      executor_label: 'local',
      sublattice_dispatch_id: null,
    },
    {
      id: 145,
      name: ':parameter:0.981111111111111',
      node_id: 7,
      started_at: '2022-10-27 07:14:42.804085',
      completed_at: '2022-10-27 07:14:42.804090',
      status: 'COMPLETED',
      type: 'parameter',
      executor_label: 'local',
      sublattice_dispatch_id: null,
    },
    {
      id: 146,
      name: 'compute_energy',
      node_id: 8,
      started_at: '2022-10-27 07:14:43.719695',
      completed_at: '2022-10-27 07:14:43.817448',
      status: 'FAILED',
      type: 'function',
      executor_label: 'local',
      sublattice_dispatch_id: null,
    },
    {
      id: 147,
      name: 'make_ag_crystal',
      node_id: 9,
      started_at: '2022-10-27 07:14:43.225770',
      completed_at: '2022-10-27 07:14:43.302687',
      status: 'COMPLETED',
      type: 'function',
      executor_label: 'local',
      sublattice_dispatch_id: null,
    },
    {
      id: 148,
      name: ':parameter:0.9966666666666667',
      node_id: 10,
      started_at: '2022-10-27 07:14:42.839056',
      completed_at: '2022-10-27 07:14:42.839058',
      status: 'COMPLETED',
      type: 'parameter',
      executor_label: 'local',
      sublattice_dispatch_id: null,
    },
    {
      id: 149,
      name: 'compute_energy',
      node_id: 11,
      started_at: '2022-10-27 07:14:43.794646',
      completed_at: '2022-10-27 07:14:43.904668',
      status: 'FAILED',
      type: 'function',
      executor_label: 'local',
      sublattice_dispatch_id: null,
    },
    {
      id: 150,
      name: 'make_ag_crystal',
      node_id: 12,
      started_at: '2022-10-27 07:14:43.253331',
      completed_at: '2022-10-27 07:14:43.364126',
      status: 'COMPLETED',
      type: 'function',
      executor_label: 'local',
      sublattice_dispatch_id: null,
    },
    {
      id: 151,
      name: ':parameter:1.0122222222222221',
      node_id: 13,
      started_at: '2022-10-27 07:14:42.875773',
      completed_at: '2022-10-27 07:14:42.875776',
      status: 'COMPLETED',
      type: 'parameter',
      executor_label: 'local',
      sublattice_dispatch_id: null,
    },
    {
      id: 152,
      name: 'compute_energy',
      node_id: 14,
      started_at: '2022-10-27 07:14:43.861399',
      completed_at: '2022-10-27 07:14:44.022004',
      status: 'FAILED',
      type: 'function',
      executor_label: 'local',
      sublattice_dispatch_id: null,
    },
    {
      id: 153,
      name: 'make_ag_crystal',
      node_id: 15,
      started_at: '2022-10-27 07:14:43.339055',
      completed_at: '2022-10-27 07:14:43.419409',
      status: 'COMPLETED',
      type: 'function',
      executor_label: 'local',
      sublattice_dispatch_id: null,
    },
    {
      id: 154,
      name: ':parameter:1.027777777777778',
      node_id: 16,
      started_at: '2022-10-27 07:14:42.913831',
      completed_at: '2022-10-27 07:14:42.913833',
      status: 'COMPLETED',
      type: 'parameter',
      executor_label: 'local',
      sublattice_dispatch_id: null,
    },
    {
      id: 155,
      name: 'compute_energy',
      node_id: 17,
      started_at: '2022-10-27 07:14:43.969999',
      completed_at: '2022-10-27 07:14:44.069682',
      status: 'FAILED',
      type: 'function',
      executor_label: 'local',
      sublattice_dispatch_id: null,
    },
    {
      id: 156,
      name: 'make_ag_crystal',
      node_id: 18,
      started_at: '2022-10-27 07:14:43.396162',
      completed_at: '2022-10-27 07:14:43.491698',
      status: 'COMPLETED',
      type: 'function',
      executor_label: 'local',
      sublattice_dispatch_id: null,
    },
    {
      id: 157,
      name: ':parameter:1.0433333333333334',
      node_id: 19,
      started_at: '2022-10-27 07:14:42.957781',
      completed_at: '2022-10-27 07:14:42.957784',
      status: 'COMPLETED',
      type: 'parameter',
      executor_label: 'local',
      sublattice_dispatch_id: null,
    },
    {
      id: 158,
      name: 'compute_energy',
      node_id: 20,
      started_at: '2022-10-27 07:14:44.044205',
      completed_at: '2022-10-27 07:14:44.155813',
      status: 'FAILED',
      type: 'function',
      executor_label: 'local',
      sublattice_dispatch_id: null,
    },
    {
      id: 159,
      name: 'make_ag_crystal',
      node_id: 21,
      started_at: '2022-10-27 07:14:43.450567',
      completed_at: '2022-10-27 07:14:43.547974',
      status: 'COMPLETED',
      type: 'function',
      executor_label: 'local',
      sublattice_dispatch_id: null,
    },
    {
      id: 160,
      name: ':parameter:1.058888888888889',
      node_id: 22,
      started_at: '2022-10-27 07:14:42.995198',
      completed_at: '2022-10-27 07:14:42.995200',
      status: 'COMPLETED',
      type: 'parameter',
      executor_label: 'local',
      sublattice_dispatch_id: null,
    },
    {
      id: 161,
      name: 'compute_energy',
      node_id: 23,
      started_at: '2022-10-27 07:14:44.125170',
      completed_at: '2022-10-27 07:14:44.262392',
      status: 'FAILED',
      type: 'function',
      executor_label: 'local',
      sublattice_dispatch_id: null,
    },
    {
      id: 162,
      name: 'make_ag_crystal',
      node_id: 24,
      started_at: '2022-10-27 07:14:43.475309',
      completed_at: '2022-10-27 07:14:43.607444',
      status: 'COMPLETED',
      type: 'function',
      executor_label: 'local',
      sublattice_dispatch_id: null,
    },
    {
      id: 163,
      name: ':parameter:1.0744444444444445',
      node_id: 25,
      started_at: '2022-10-27 07:14:43.021959',
      completed_at: '2022-10-27 07:14:43.021961',
      status: 'COMPLETED',
      type: 'parameter',
      executor_label: 'local',
      sublattice_dispatch_id: null,
    },
    {
      id: 164,
      name: 'compute_energy',
      node_id: 26,
      started_at: '2022-10-27 07:14:44.209691',
      completed_at: '2022-10-27 07:14:44.317622',
      status: 'FAILED',
      type: 'function',
      executor_label: 'local',
      sublattice_dispatch_id: null,
    },
    {
      id: 165,
      name: 'make_ag_crystal',
      node_id: 27,
      started_at: '2022-10-27 07:14:43.529019',
      completed_at: '2022-10-27 07:14:43.642728',
      status: 'COMPLETED',
      type: 'function',
      executor_label: 'local',
      sublattice_dispatch_id: null,
    },
    {
      id: 166,
      name: ':parameter:1.09',
      node_id: 28,
      started_at: '2022-10-27 07:14:43.052014',
      completed_at: '2022-10-27 07:14:43.052016',
      status: 'COMPLETED',
      type: 'parameter',
      executor_label: 'local',
      sublattice_dispatch_id: null,
    },
    {
      id: 167,
      name: 'compute_energy',
      node_id: 29,
      started_at: '2022-10-27 07:14:44.288866',
      completed_at: '2022-10-27 07:14:44.397430',
      status: 'FAILED',
      type: 'function',
      executor_label: 'local',
      sublattice_dispatch_id: null,
    },
  ],
  links: [
    {
      edge_name: 'atoms',
      parameter_type: 'arg',
      target: 140,
      source: 138,
      arg_index: 0,
    },
    {
      edge_name: 'scale',
      parameter_type: 'arg',
      target: 138,
      source: 139,
      arg_index: 0,
    },
    {
      edge_name: 'atoms',
      parameter_type: 'arg',
      target: 143,
      source: 141,
      arg_index: 0,
    },
    {
      edge_name: 'scale',
      parameter_type: 'arg',
      target: 141,
      source: 142,
      arg_index: 0,
    },
    {
      edge_name: 'atoms',
      parameter_type: 'arg',
      target: 146,
      source: 144,
      arg_index: 0,
    },
    {
      edge_name: 'scale',
      parameter_type: 'arg',
      target: 144,
      source: 145,
      arg_index: 0,
    },
    {
      edge_name: 'atoms',
      parameter_type: 'arg',
      target: 149,
      source: 147,
      arg_index: 0,
    },
    {
      edge_name: 'scale',
      parameter_type: 'arg',
      target: 147,
      source: 148,
      arg_index: 0,
    },
    {
      edge_name: 'atoms',
      parameter_type: 'arg',
      target: 152,
      source: 150,
      arg_index: 0,
    },
    {
      edge_name: 'scale',
      parameter_type: 'arg',
      target: 150,
      source: 151,
      arg_index: 0,
    },
    {
      edge_name: 'atoms',
      parameter_type: 'arg',
      target: 155,
      source: 153,
      arg_index: 0,
    },
    {
      edge_name: 'scale',
      parameter_type: 'arg',
      target: 153,
      source: 154,
      arg_index: 0,
    },
    {
      edge_name: 'atoms',
      parameter_type: 'arg',
      target: 158,
      source: 156,
      arg_index: 0,
    },
    {
      edge_name: 'scale',
      parameter_type: 'arg',
      target: 156,
      source: 157,
      arg_index: 0,
    },
    {
      edge_name: 'atoms',
      parameter_type: 'arg',
      target: 161,
      source: 159,
      arg_index: 0,
    },
    {
      edge_name: 'scale',
      parameter_type: 'arg',
      target: 159,
      source: 160,
      arg_index: 0,
    },
    {
      edge_name: 'atoms',
      parameter_type: 'arg',
      target: 164,
      source: 162,
      arg_index: 0,
    },
    {
      edge_name: 'scale',
      parameter_type: 'arg',
      target: 162,
      source: 163,
      arg_index: 0,
    },
    {
      edge_name: 'atoms',
      parameter_type: 'arg',
      target: 167,
      source: 165,
      arg_index: 0,
    },
    {
      edge_name: 'scale',
      parameter_type: 'arg',
      target: 165,
      source: 166,
      arg_index: 0,
    },
  ],
}

describe('lattice graph', () => {
  test('render lattice graph', () => {
    reduxRender(
      <>
        <App graph={graph} direction="DOWN"></App>
      </>
    )
  })
  test('render lattice graph1', () => {
    reduxRender(
      <>
        <App graph={graph} direction="UP"></App>
      </>
    )
  })

  test('render lattice graph2', () => {
    reduxRender(
      <>
        <App graph={graph} direction="LEFT"></App>
      </>
    )
  })

  test('render lattice graph3', () => {
    reduxRender(
      <>
        <App graph={graph} direction="RIGHT"></App>
      </>
    )
  })

  test('render lattice graph params', () => {
    reduxRender(
      <>
        <App graph={graph} direction="DOWN" showParams={false}></App>
      </>
    )
  })

  test('hide labels', () => {
    reduxRender(
      <>
        <App graph={graph} direction="DOWN" hideLabels={true}></App>
      </>
    )
  })
})
