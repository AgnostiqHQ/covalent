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
import { render, screen } from '../../../testHelpers/testUtils'
import App from '../ResultListing'
import { BrowserRouter } from 'react-router-dom'
import { Provider } from 'react-redux'
import reducers from '../../../redux/reducers'
import { configureStore } from '@reduxjs/toolkit'
import theme from '../../../utils/theme'
import ThemeProvider from '@mui/system/ThemeProvider'

function mockRender(renderedComponent) {
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

const resultListCases = ['All', 'Completed', 'Failed', 'Running']

describe('Result Listing', () => {


  test('renders result lists section', () => {
    mockRender(<App />)
    const linkElement = screen.getByText('All')
    expect(linkElement).toBeInTheDocument()
  })
  test.each(resultListCases)('render %p sort section', (firstArg) => {
    mockRender(<App />)
    const element = screen.getByText(firstArg)
    expect(element).toBeInTheDocument()
  })

  test('renders search  section', () => {
    mockRender(<App />)
    const linkElement = screen.getByPlaceholderText('Search')
    expect(linkElement).toBeInTheDocument()
  })
  test('renders dialogBox', () => {
    mockRender(<App openDialogBox={true} />)
    const linkElement = screen.getByPlaceholderText('Search')
    expect(linkElement).toBeInTheDocument()
  })
})
