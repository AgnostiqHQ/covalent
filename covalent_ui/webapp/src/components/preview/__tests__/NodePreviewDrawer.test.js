/**
 * This file is part of Covalent.
 *
 * Licensed under the Apache License 2.0 (the "License"). A copy of the
 * License may be obtained with this software package or at
 *
 *     https://www.apache.org/licenses/LICENSE-2.0
 *
 * Use of this file is prohibited except in compliance with the License.
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import App from '../NodePreviewDrawer.js'
import React from 'react'
import { render, screen } from '../../../testHelpers/testUtils'
import { BrowserRouter } from 'react-router-dom'
import { Provider } from 'react-redux'
import reducers from '../../../redux/reducers'
import { configureStore } from '@reduxjs/toolkit'
import { ReactFlowProvider } from 'react-flow-renderer'
import userEvent from '@testing-library/user-event'

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

  test('close nodeDrawer section', async () => {
    mockRender(<App node={node} />)
    const linkElement = await screen.findByTestId('closeNodeDrawer')
    expect(linkElement).toBeInTheDocument()
    userEvent.click(linkElement)
  })
})
