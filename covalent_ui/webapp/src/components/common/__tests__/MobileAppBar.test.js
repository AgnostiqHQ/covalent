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
import React from 'react'
import { render, screen, fireEvent } from '../../../testHelpers/testUtils'
import App from '../MobileAppBar'
import { BrowserRouter } from 'react-router-dom'
import reducers from '../../../redux/reducers'
import { configureStore } from '@reduxjs/toolkit'
import theme from '../../../utils/theme'
import ThemeProvider from '@mui/system/ThemeProvider'
import * as redux from 'react-redux'

function mockRender(renderedComponent) {
  const store = configureStore({
    reducer: reducers,
  })
  return render(
    <redux.Provider store={store}>
      <ThemeProvider theme={theme}>
        <BrowserRouter>{renderedComponent}</BrowserRouter>
      </ThemeProvider>
    </redux.Provider>
  )
}

describe('mobile appbar', () => {
  test('renders MobileAppBar section', () => {
    // eslint-disable-next-line no-undef
    mockRender(<App />)
    const linkElement = screen.getByTestId('mobile appbar')
    expect(linkElement).toBeInTheDocument()
  })
  test('renders button', () => {
    const useDispatchSpy = jest.spyOn(redux, 'useDispatch')
    const mockDispatchFn = jest.fn()
    useDispatchSpy.mockReturnValue(mockDispatchFn)
    // eslint-disable-next-line no-undef
    mockRender(<App />)
    const linkElement = screen.getByRole('button')
    expect(linkElement).toBeInTheDocument()
    fireEvent.click(linkElement)
    expect(mockDispatchFn).toBeCalled()
    useDispatchSpy.mockClear()
  })
})
