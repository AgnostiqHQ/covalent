// /**
//  * Copyright 2021 Agnostiq Inc.
//  *
//  * This file is part of Covalent.
//  *
//  * Licensed under the GNU Affero General Public License 3.0 (the "License").
//  * A copy of the License may be obtained with this software package or at
//  *
//  *      https://www.gnu.org/licenses/agpl-3.0.en.html
//  *
//  * Use of this file is prohibited except in compliance with the License. Any
//  * modifications or derivative works of this file must retain this copyright
//  * notice, and modified files must contain a notice indicating that they have
//  * been altered from the originals.
//  *
//  * Covalent is distributed in the hope that it will be useful, but WITHOUT
//  * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
//  * FITNESS FOR A PARTICULAR PURPOSE. See the License for more details.
//  *
//  * Relief from the License may be granted by purchasing a commercial license.
//  */

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
