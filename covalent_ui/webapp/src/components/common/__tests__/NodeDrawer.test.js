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
import App from '../NodeDrawer'
import "@testing-library/jest-dom";
import React from 'react'
import { Provider } from 'react-redux'
import reducers from '../../../redux/reducers'
import { configureStore } from '@reduxjs/toolkit'
import theme from '../../../utils/theme'
import ThemeProvider from '@mui/system/ThemeProvider'
import { BrowserRouter } from 'react-router-dom'

import { ReactFlowProvider } from 'react-flow-renderer'
import { HelmetProvider } from 'react-helmet-async'

function reduxRender(rederedComponent) {
  const store = configureStore({
    reducer: reducers,
  })
  return render(
    <Provider store={store}>
      <HelmetProvider>
        <ReactFlowProvider>
          <ThemeProvider theme={theme}>
            <BrowserRouter>{rederedComponent}</BrowserRouter>
          </ThemeProvider>
        </ReactFlowProvider>
      </HelmetProvider>
    </Provider>
  )
}

const node = {
  completed_at: "2022-08-09T06:19:26.425370",
  id: 42,
  name: "identity",
  node_id: 13,
  started_at: "2022-08-09T06:19:26.370932",
  status: "COMPLETED",
  type: "function",
}

const dispatchId = "edcd9b3e-6d52-44ac-baa5-d45614e25699"
const electronId = 42

const electronDetail = {
  ended_at: "2022-08-09T11:49:26",
  id: 43,
  name: "identity",
  node_id: 14,
  parent_lattice_id: 2,
  runtime: 0,
  started_at: "2022-08-09T11:49:26",
  status: "COMPLETED",
  storage_path: "/home/prasannavenkatesh/Desktop/workflows/results/edcd9b3e-6d52-44ac-baa5-d45614e25699/node_14",
  type: "function"
}

describe('electronNode file Rendered', () => {

  test('renders inoputsrc', async () => {
    reduxRender(<App node={node} dispatchId={dispatchId} electronId={electronId}
      electronDetailIsFetching={true} electronDetailStatus={electronDetail.status}
      electronDetail={electronDetail} />)
    const linkElement = screen.getByTestId('nodeDrawer')
    expect(linkElement).toBeInTheDocument()
  })

  test('renders electronNode122', async () => {
    reduxRender(<App node={node} dispatchId={dispatchId} electronId={electronId} electronDetailIsFetching={false} />)
    const linkElement = screen.getByTestId('nodeDrawer')
    expect(linkElement).toBeInTheDocument()
  })

  test('renders electronNode', async () => {
    reduxRender(<App />)
    const linkElement = screen.getByTestId('nodeDrawer')
    expect(linkElement).toBeInTheDocument()
  })

})