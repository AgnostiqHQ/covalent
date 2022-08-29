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

import { render, screen } from '@testing-library/react'
// import {screen} from '@testing-library/dom'
import LatticeGraph from '../LatticeGraph'
import { BrowserRouter } from 'react-router-dom'
import React from 'react'
import { Provider } from 'react-redux'
import reducers from '../../../redux/reducers'
import { configureStore } from '@reduxjs/toolkit'
import theme from '../../../utils/theme'
import ThemeProvider from '@mui/system/ThemeProvider'
import { HelmetProvider } from 'react-helmet-async'
import { ReactFlowProvider } from 'react-flow-renderer'
import ElectronNode from '../ElectronNode'
import ParameterNode from '../ParameterNode'
import DirectedEdge from '../DirectedEdge'

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

describe('lattice graph', () => {

  const elements = [
    {
      id: "561", type: "electron", position: { x: 529, y: 12 },
      data: { fullName: "identity", label: "identity", status: "COMPLETED" },
      targetPosition: "top", sourcePosition: "bottom"
    },
    {
      id: "562", type: "electron", position: { x: 729, y: 12 },
      data: { fullName: "identity", label: "identity", status: "COMPLETED" },
      targetPosition: "top", sourcePosition: "top"
    },
    {
      id: "563", type: "electron", position: { x: 329, y: 12 },
      data: { fullName: "identity", label: "identity", status: "COMPLETED" },
      targetPosition: "top", sourcePosition: "top"
    },
    {
      id: "564", type: "electron", position: { x: 929, y: 12 },
      data: { fullName: "identity", label: "identity", status: "COMPLETED" },
      targetPosition: "top", sourcePosition: "side"
    },
    {
      id: "565", type: "electron", position: { x: 429, y: 12 },
      data: { fullName: "identity", label: "identity", status: "COMPLETED" },
      targetPosition: "top", sourcePosition: "side"
    }

  ]

  test('Rendering lattice graph', async () => {
    const nodesDraggable = false;
    const link__bond = reduxRender(
      <>
        {elements && (
          <LatticeGraph
            data-testid="lattice__graph"
            nodeTypes={{ electron: ElectronNode, parameter: ParameterNode }}
            edgeTypes={{ directed: DirectedEdge }}
            nodesDraggable={nodesDraggable}
            nodesConnectable={false}
            elements={elements}
            defaultZoom={1}
            minZoom={0}
            maxZoom={3}
          >
          </LatticeGraph>
        )}
      </>
    )
    const linkElement = link__bond.queryByTestId('lattice__graph')
    expect(linkElement).toBeDefined()
  })

  test('render lattice graph', () => {
    const { container } = reduxRender(<LatticeGraph hidden={true} elements={elements} />);
    expect(container.querySelector('.react-flow')).toBeDefined();
  })

})
