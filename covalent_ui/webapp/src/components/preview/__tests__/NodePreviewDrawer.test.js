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

import App from '../NodePreviewDrawer.js'
import React from 'react'
import { render, screen } from '../../../testHelpers/testUtils'
import { BrowserRouter } from 'react-router-dom'
import { Provider } from 'react-redux'
import reducers from '../../../redux/reducers'
import { configureStore } from '@reduxjs/toolkit'
import { ReactFlowProvider } from 'react-flow-renderer'

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

const node = {
  completed_at: '2022-08-25T04:24:10.006856',
  executor_label: 'dask',
  id: 606,
  name: 'combine',
  node_id: 68,
  started_at: '2022-08-25T04:24:09.902067',
  status: 'COMPLETED',
  type: 'function',
}

const previewCases = [
  ['statusLabel', 'Completed'],
  ['status', 'Status'],
  ['Executor', 'Executor:'],
  ['Syntax highlighter', '# source unavailable'],
]

describe('lattice node preview drawer section', () => {
  test('renders nodeDrawer section', () => {
    mockRender(<App node={node} />)
    const linkElement = screen.getByText(/combine/i)
    expect(linkElement).toBeInTheDocument()
  })

  test.each(previewCases)('renders %p', (firstArgs, secondArgs) => {
    mockRender(<App node={node} />)
    const linkElement = screen.getByText(secondArgs)
    expect(linkElement).toBeInTheDocument()
  })
})
