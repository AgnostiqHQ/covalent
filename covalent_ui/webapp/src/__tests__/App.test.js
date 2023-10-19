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

import { screen, render } from '@testing-library/react'
import App from '../App'
import { BrowserRouter } from 'react-router-dom'
import React from 'react'
import { Provider } from 'react-redux'
import reducers from '../redux/reducers'
import { configureStore } from '@reduxjs/toolkit'
import theme from '../utils/theme'
import ThemeProvider from '@mui/system/ThemeProvider'
import DispatchLayout from '../components/dispatch/DispatchLayout'

function reduxRender(renderedComponent) {
  const store = configureStore({
    reducer: reducers,
  })

  return render(
    <Provider store={store}>
      <ThemeProvider theme={theme}>
        <BrowserRouter>{renderedComponent}</BrowserRouter>
      </ThemeProvider>
    </Provider>
  )
}

describe('App Page', () => {
  test('app.js is rendered', () => {
    reduxRender(<App element={DispatchLayout} />)
    const linkElement = screen.getByTestId('dashboard')
    expect(linkElement).toBeInTheDocument()
  })
})
