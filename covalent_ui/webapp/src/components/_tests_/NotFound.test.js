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
