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

import { render, screen, fireEvent } from '@testing-library/react'
import App from '../NavDrawer'
import { LinkButton } from '../NavDrawer'
import { DialogToolbar } from '../NavDrawer'
import { Provider } from 'react-redux'
import { BrowserRouter } from 'react-router-dom'
import { ReactFlowProvider } from 'react-flow-renderer'
import { HelmetProvider } from 'react-helmet-async'
import { configureStore } from '@reduxjs/toolkit'
import reducers from '../../../redux/reducers'
import React from 'react'

const MockApp = () => {
  const store = configureStore({
    reducer: reducers,
  })
  return (
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
}
const MockLinkButton = ({ title, path, val }) => {
  const initialState = {
    dataRes: {
      popupData: {
        data: {
          log_dir: '/home/sriranjanivenkatesan/.cache/covalentss',
        },
        isChanged: val,
      },
    },
  }
  const store = configureStore({
    reducer: reducers,
    preloadedState: initialState,
  })
  return (
    <Provider store={store}>
      <HelmetProvider>
        <ReactFlowProvider>
          <BrowserRouter>
            <LinkButton title={title} margintop={'10px'} path={path} />
          </BrowserRouter>
        </ReactFlowProvider>
      </HelmetProvider>
    </Provider>
  )
}
const MockDialogToolbar = () => {
  const store = configureStore({
    reducer: reducers,
  })
  return (
    <Provider store={store}>
      <HelmetProvider>
        <ReactFlowProvider>
          <BrowserRouter>
            <DialogToolbar openDialogBox={true} />
          </BrowserRouter>
        </ReactFlowProvider>
      </HelmetProvider>
    </Provider>
  )
}
const navDrawerCases = ['navDrawer', 'covalentLogo']
const navDrawerCases2 = [
  'Dispatch list',
  'Lattice draw preview',
  'Logs',
  'Settings',
]

describe('navDrawers', () => {
  test.each(navDrawerCases)('render %p', (firstArg) => {
    render(<MockApp />)
    const element = screen.getByTestId(firstArg)
    expect(element).toBeInTheDocument()
  })

  test.each(navDrawerCases2)('render %p', (firstArg) => {
    render(<MockApp />)
    const element = screen.getByLabelText(firstArg)
    expect(element).toBeInTheDocument()
  })

  test('render button actions', () => {
    render(<MockApp />)
    const element = screen.getByTestId('LogoListItemButton')
    expect(element).toBeInTheDocument()
    fireEvent.mouseOver(element)
    const textHover = screen.getByTestId('covalentLogoHover')
    expect(textHover).toBeInTheDocument()
    fireEvent.mouseOut(element)
    const textHoverOut = screen.getByTestId('covalentLogo')
    expect(textHoverOut).toBeInTheDocument()
    fireEvent.click(element)
    expect(screen.getByTestId('LogoListItemButton')).toBeEnabled()
  })

  test('render LinkButton with title value and margin top', () => {
    render(<MockLinkButton title="sample" path="/settings" val={true} />)
    const element = screen.getByTestId('SpecificListItemButton')
    expect(element).toBeInTheDocument()
    fireEvent.click(element)
    expect(screen.getByTestId('SpecificListItemButton')).toBeEnabled()
    render(<MockLinkButton title="Logo" path="/settings" val={true} />)
    const linkelement = screen.getByTestId('LogoListItemButton')
    fireEvent.click(linkelement)
    expect(screen.getByTestId('LogoListItemButton')).toBeEnabled()
  })

  test('render dialog toolbar', () => {
    render(<MockDialogToolbar />)
    const element = screen.getByTestId('toolBar')
    expect(element).toBeInTheDocument()
  })

  test('render LinkButton else case', () => {
    render(<MockLinkButton title="Logo" path="/logs" val={true} />)
    const linkelementElseCase1 = screen.getByTestId('LogoListItemButton')
    fireEvent.click(linkelementElseCase1)
    expect(screen.getByTestId('dialogbox')).toBeInTheDocument()
  })

  test('render LinkButton else case with isChanged false', () => {
    render(<MockLinkButton title="Logo" path="/logs" val={false} />)
    const linkelementElseCase2 = screen.getByTestId('LogoListItemButton')
    fireEvent.click(linkelementElseCase2)
    expect(screen.queryByTestId('dialogbox')).not.toBeInTheDocument()
  })
})
