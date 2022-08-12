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
// import {screen} from '@testing-library/dom'
import { LayoutOptions } from '../LayoutOptions'
import { BrowserRouter } from 'react-router-dom'
import React from 'react'
import { Provider } from 'react-redux'
import reducers from '../../../redux/reducers'
import { configureStore } from '@reduxjs/toolkit'
import theme from '../../../utils/theme'
import ThemeProvider from '@mui/system/ThemeProvider'
import MenuItem from '@mui/material/MenuItem'
import Menu from '@mui/material/Menu'


function reduxRender(rederedComponent) {
    const store = configureStore({
      reducer: reducers,
    })
    return render(
      <Provider store={store}>
        <ThemeProvider theme={theme}>
            <BrowserRouter>{rederedComponent}</BrowserRouter>
        </ThemeProvider>
      </Provider>
    )
  }

  const options = [
    'layered',
    'box',
    'tree',
    'rectangular',
  ]


describe('layout options', () => {
  test('render layout options', () => {
    reduxRender(<LayoutOptions />)
    const layoutOption = screen.getByTestId('layoutoption')
    expect(layoutOption).toBeInTheDocument()
  })

  test.each(options)('render %p sort section', (firstArg) => {
    render(
    <LayoutOptions />
    )
    const element = screen.findByText(firstArg);
    expect(element).toBeDefined()
  })
})
