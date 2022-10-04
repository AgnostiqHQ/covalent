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

import { render, screen } from '@testing-library/react'
import App from '../NotFound'
import { Provider } from 'react-redux'
import { BrowserRouter } from 'react-router-dom'
import { ReactFlowProvider } from 'react-flow-renderer'
import { HelmetProvider } from 'react-helmet-async'
import { configureStore } from '@reduxjs/toolkit'
import reducers from '../../redux/reducers'

const store = configureStore({
  reducer: reducers,
})
describe('page not found component render', () => {
  test('page not found text check', () => {
    const component = render(
      <Provider store={store}>
        <HelmetProvider>
          <ReactFlowProvider>
            <BrowserRouter>
              <App />
            </BrowserRouter>
          </ReactFlowProvider>
        </HelmetProvider>
      </Provider>
    )
    const linkElement = component.getByText(/Page not found./i)
    expect(linkElement).toBeInTheDocument()
  })

  test('page not found logo', () => {
    render(
      <Provider store={store}>
        <HelmetProvider>
          <ReactFlowProvider>
            <BrowserRouter>
              <App />
            </BrowserRouter>
          </ReactFlowProvider>
        </HelmetProvider>
      </Provider>
    )
    const element = screen.getByTestId('logo')
    expect(element).toBeInTheDocument()
  })

  test('page not found message check', () => {
    render(
      <Provider store={store}>
        <HelmetProvider>
          <ReactFlowProvider>
            <BrowserRouter>
              <App />
            </BrowserRouter>
          </ReactFlowProvider>
        </HelmetProvider>
      </Provider>
    )
    const element = screen.getByTestId('message')
    expect(element).toBeInTheDocument()
  })
})
