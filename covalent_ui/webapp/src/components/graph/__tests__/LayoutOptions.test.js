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

import { fireEvent, render, screen } from '@testing-library/react'
import { LayoutOptions } from '../LayoutOptions'
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

describe('layout options', () => {
  const options = [
    'Layered',
    'Tree',
    'Force',
    'Rectangular',
    'Box',
    'Old Layout',
  ]
  test('render layout options', () => {
    reduxRender(<LayoutOptions />)
    const layoutOption = screen.getByTestId('layoutoption')
    expect(layoutOption).toBeInTheDocument()
  })

  test.each(options)('render %p sort section', (firstArg) => {
    reduxRender(<LayoutOptions open />)
    const elementLink = screen.getByTestId('lay__tit')
    fireEvent.click(elementLink)
    expect(screen.getByText(firstArg)).toBeDefined()
  })
})
