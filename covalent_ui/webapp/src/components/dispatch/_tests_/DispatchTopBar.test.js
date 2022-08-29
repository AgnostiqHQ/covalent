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

 import { screen } from '@testing-library/react'
 import App from '../DispatchTopBar'
 import { BrowserRouter } from 'react-router-dom'
 import React from 'react'
 import { Provider } from 'react-redux'
 import { render } from '@testing-library/react'
 import reducers from '../../../redux/reducers'
 import { configureStore } from '@reduxjs/toolkit'
 import theme from '../../../utils/theme'
 import ThemeProvider from '@mui/system/ThemeProvider'

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

 describe('Dispatch TopBar', () => {
  const latDetails = {
    directory: "/home/prasannavenkatesh/Desktop/workflows/results/4be2f8f9-528d-4006-9e13-0ddf84172c98",
    dispatch_id: "4be2f8f9-528d-4006-9e13-0ddf84172c98",
    ended_at: "2022-08-09T11:49:33",
    runtime: 2000,
    started_at: "2022-08-09T11:49:31",
    status: "COMPLETED",
    total_electrons: 54,
    total_electrons_completed: 54,
    updated_at: null,
  }
  test('dispatch top bar is rendered', () => {
    reduxRender(<App />)
    const linkElement = screen.getByTestId('topbar')
    expect(linkElement).toBeInTheDocument()
  })

  test('status card is rendered', () => {
    reduxRender(<App />)
    const linkElement = screen.getByTestId('topbarcard')
    expect(linkElement).toBeInTheDocument()
  })

  test('status card isfetching rendered', () => {
    reduxRender(<App isFetching={false}/>)
    const linkElement = screen.getByTestId('topbarcard')
    expect(linkElement).toBeInTheDocument()
  })

  test('status card latDetails rendered', () => {
    reduxRender(<App latDetails={latDetails}/>)
    const linkElement = screen.getByTestId('topbarcard')
    expect(linkElement).toBeInTheDocument()
  })
 })
