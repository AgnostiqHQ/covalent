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
