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

import { render, screen, fireEvent } from '@testing-library/react'
import NodeDrawer from '../NodeDrawer'
import '@testing-library/jest-dom'
import React from 'react'
import { Provider } from 'react-redux'
import reducers from '../../../redux/reducers'
import { configureStore } from '@reduxjs/toolkit'
import theme from '../../../utils/theme'
import ThemeProvider from '@mui/system/ThemeProvider'
import { BrowserRouter } from 'react-router-dom'

import { ReactFlowProvider } from 'react-flow-renderer'
import { HelmetProvider } from 'react-helmet-async'

var initialState = {
  electronResults: {
    electronDetailsList: {
      isFetching: true,
    },
    electronInput: {
      data: "{'args': ('3', '2'), 'kwargs': {}}",
      python_object:
        "import pickle\npickle.loads(b'\\x80\\x05\\x95!\\x00\\x00\\x00\\x00\\x00\\x00\\x00}\\x94(\\x8c\\x04args\\x94\\x8c\\x013\\x94\\x8c\\x012\\x94\\x86\\x94\\x8c\\x06kwargs\\x94}\\x94u.')",
    },
    electronFunctionString: {
      data: '@ct.electron\n@ct.lattice\ndef mul(a,b):\n    res1 = add(a,b)\n    res2 = sub(a,b)\n    return res1,res2\n\n\n',
      python_object: null,
    },
    electronResultList: { isFetching: true, error: null },
    electronFunctionStringList: { isFetching: true, error: null },
    electronInputList: { isFetching: true, error: null },
    electronErrorList: { isFetching: true, error: null },
    electronExecutorList: { isFetching: true, error: null },
    electronList: {
      description: 'samp',
      ended_at: '2022-11-02T17:54:58',
      id: 37,
      name: ':sublattice:mul',
      node_id: 0,
      parent_lattice_id: 8,
      runtime: 0,
      started_at: '2022-11-02T17:54:58',
      status: 'COMPLETED',
      storage_path:
        '/home/sriranjanivenkatesan/Downloads/results/741da909-a9d5-4827-8747-0af8182183bc/node_0',
      type: 'sublattice',
    },
    electronResult: {
      data: '"(5, 1)"',
      python_object:
        "import pickle\npickle.loads(b'\\x80\\x05\\x95\\x07\\x00\\x00\\x00\\x00\\x00\\x00\\x00K\\x05K\\x01\\x86\\x94.')",
    },
  },
}
function mockRender(renderedComponent) {
  const store = configureStore({
    reducer: reducers,
    preloadedState: initialState,
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

const node = {
  completed_at: '2022-08-09T06:19:26.425370',
  id: 42,
  name: 'identity',
  node_id: 13,
  started_at: '2022-08-09T06:19:26.370932',
  status: 'COMPLETED',
  type: 'function',
}

const dispatchId = 'edcd9b3e-6d52-44ac-baa5-d45614e25699'
const electronId = 42

const electronDetail = {
  ended_at: '2022-08-09T11:49:26',
  id: 43,
  name: 'identity',
  node_id: 14,
  parent_lattice_id: 2,
  runtime: 0,
  started_at: '2022-08-09T11:49:26',
  status: 'COMPLETED',
  storage_path:
    '/home/prasannavenkatesh/Desktop/workflows/results/edcd9b3e-6d52-44ac-baa5-d45614e25699/node_14',
  type: 'function',
}

describe('electronNode file Rendered', () => {
  test('renders inputsrc', async () => {
    reduxRender(
      <NodeDrawer
        node={node}
        dispatchId={dispatchId}
        electronId={electronId}
        electronDetailIsFetching={true}
        electronDetailStatus={electronDetail.status}
        electronDetail={electronDetail}
      />
    )
    const linkElement = screen.getByTestId('nodeDrawer')
    expect(linkElement).toBeInTheDocument()
  })

  test('renders electronNode122', async () => {
    reduxRender(
      <NodeDrawer
        node={node}
        dispatchId={dispatchId}
        electronId={electronId}
        electronDetailIsFetching={false}
      />
    )
    const linkElement = screen.getByTestId('nodeDrawer')
    expect(linkElement).toBeInTheDocument()
  })

  test('renders electronNode', async () => {
    reduxRender(<NodeDrawer />)
    const linkElement = screen.getByTestId('nodeDrawer')
    expect(linkElement).toBeInTheDocument()
  })

  test('renders Node drawer for handleclose function', async () => {
    reduxRender(<NodeDrawer node={node} />)
    const linkElement = screen.getByTestId('node__dra_close')
    fireEvent.click(screen.getByTestId('CloseIcon'))
    expect(linkElement).toBeInTheDocument()
  })
})
