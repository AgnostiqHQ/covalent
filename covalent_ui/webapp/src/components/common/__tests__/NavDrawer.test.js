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

import { render, screen , fireEvent } from '@testing-library/react'
import App from '../NavDrawer'
import { Provider } from 'react-redux'
import { BrowserRouter } from 'react-router-dom'
import { ReactFlowProvider } from 'react-flow-renderer'
import { HelmetProvider } from 'react-helmet-async'
import { configureStore } from '@reduxjs/toolkit'
import reducers from '../../../redux/reducers'
import React from "react"

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

const navDrawerCases = ['navDrawer', 'covalentLogo']
const navDrawerCases2 = ['Dispatch list', 'Lattice draw preview','Logs','Settings']

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
    const element = screen.getByTestId("LogoListItemButton")
    expect(element).toBeInTheDocument()
    fireEvent.mouseOver(element);
    const textHover= screen.getByTestId("covalentLogoHover");
    expect(textHover).toBeInTheDocument();
    fireEvent.mouseOut(element);
    const textHoverOut= screen.getByTestId("covalentLogo");
    expect(textHoverOut).toBeInTheDocument();
    fireEvent.click(element);
    expect(screen.getByTestId('LogoListItemButton')).toBeEnabled();
  })
})
