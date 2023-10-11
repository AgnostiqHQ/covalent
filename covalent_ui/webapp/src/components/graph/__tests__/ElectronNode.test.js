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

import { render, screen } from '@testing-library/react'
import { ElectronNode } from '../ElectronNode'
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

describe('electronNode file Rendered', () => {
  const data = {
    fullName: 'identity',
    label: 'identity',
    status: 'COMPLETED',
  }

  test('renders electronNode', async () => {
    reduxRender(<ElectronNode data={data} />)
    const linkElement = screen.getByTestId('electronNode')
    expect(linkElement).toBeInTheDocument()
  })

  test('renders electronNode NODE_TEXT_COLOR', async () => {
    reduxRender(
      <ElectronNode data={data} NODE_TEXT_COLOR="rgba(250, 250, 250, 0.6)" />
    )
    const linkElement = screen.getByTestId('electronNode')
    expect(linkElement).toBeInTheDocument()
  })

  test('renders electronNode hasBorder', async () => {
    reduxRender(<ElectronNode data={data} hasBorder="Completed" />)
    const linkElement = screen.getByTestId('electronNode')
    expect(linkElement).toBeInTheDocument()
  })

  test('renders electronNode color', async () => {
    reduxRender(<ElectronNode data={data} color="Completed" />)
    const linkElement = screen.getByTestId('electronNode')
    expect(linkElement).toBeInTheDocument()
  })

  test('renders handle electronNode', async () => {
    reduxRender(<ElectronNode data={data} />)
    const linkElement = screen.getByTestId('handleelectronNode')
    expect(linkElement).toBeInTheDocument()
  })

  test('renders handle position checked', async () => {
    reduxRender(<ElectronNode data={data} position="top" />)
    const linkElement = screen.getByTestId('handleelectronNode')
    expect(linkElement).toBeInTheDocument()
  })

  test('renders handle isConnectable checked', async () => {
    reduxRender(<ElectronNode data={data} isConnectable={false} />)
    const linkElement = screen.getByTestId('handleelectronNode')
    expect(linkElement).toBeInTheDocument()
  })

  test('renders sourcehandle rendered', async () => {
    reduxRender(<ElectronNode data={data} />)
    const linkElement = screen.getByTestId('sourcehandleelectronNode')
    expect(linkElement).toBeInTheDocument()
  })

  test('renders sourcehandle position rendered', async () => {
    reduxRender(<ElectronNode data={data} position="bottom" />)
    const linkElement = screen.getByTestId('sourcehandleelectronNode')
    expect(linkElement).toBeInTheDocument()
  })

  test('renders sourcehandle connectable rendered', async () => {
    reduxRender(<ElectronNode data={data} isConnectable={false} />)
    const linkElement = screen.getByTestId('sourcehandleelectronNode')
    expect(linkElement).toBeInTheDocument()
  })
})
