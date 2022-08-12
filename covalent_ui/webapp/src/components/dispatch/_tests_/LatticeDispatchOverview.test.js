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
 import App from '../LatticeDispatchOverview'
 import { BrowserRouter } from 'react-router-dom'
 import React from 'react'
 import { Provider } from 'react-redux'
 import { render } from '@testing-library/react'
 import reducers from '../../../redux/reducers'
 import { configureStore } from '@reduxjs/toolkit'
 import theme from '../../../utils/theme'
 import ThemeProvider from '@mui/system/ThemeProvider'
 
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
 
 describe('Displattice dispatch overview contents', () => {
  const result = {
    directory: "/home/prasannavenkatesh/Desktop/workflows/results/4be2f8f9-528d-4006-9e13-0ddf84172c98",
    dispatch_id: "4be2f8f9-528d-4006-9e13-0ddf84172c98",
    ended_at: "2022-08-09T11:49:33",
    runtime: 2000,
    started_at: "2022-08-09T11:49:31",
    status: "COMPLETED",
    total_electrons: 54,
    total_electrons_completed: 54,
    updated_at: null,
    lattice:"safsaf"
  }

  test('Dispatch drawer contents is rendered', () => {
    reduxRender(<App />)
    const linkElement = screen.getByTestId('dispatchoverview')
    expect(linkElement).toBeInTheDocument()
  })

  test('Dispatch drawer data is rendered', () => {
    reduxRender(<App result={result}/>)
    const linkElement = screen.getByTestId('dispatchoverview')
    expect(linkElement).toBeInTheDocument()
  })

  test('run time rendered', () => {
    reduxRender(<App startTime={result.started_at} 
      endTime={result.ended_at}/>)
    const linkElement = screen.getByTestId('dispatchoverview')
    expect(linkElement).toBeInTheDocument()
  })

  test('directory tooltip rendered', () => {
    reduxRender(<App title={result.directory} />)
    const linkElement = screen.getByTestId('dispatchoverview')
    expect(linkElement).toBeInTheDocument()
  })

  test('directory copybutton rendered', () => {
    reduxRender(<App content={result.directory} />)
    const linkElement = screen.getByTestId('dispatchoverview')
    expect(linkElement).toBeInTheDocument()
  })

  test('input section rendered', () => {
    reduxRender(<App isFetching={false} inputs="input-data"/>)
    const linkElement = screen.getByTestId('dispatchoverview')
    expect(linkElement).toBeInTheDocument()
  })

  test('result section rendered', () => {
    reduxRender(<App src="x=0"/>)
    const linkElement = screen.getByTestId('dispatchoverview')
    expect(linkElement).toBeInTheDocument()
  })

  test('executor section rendered', () => {
    reduxRender(<App isFetching={false} metadata="function x=0"/>)
    const linkElement = screen.getByTestId('dispatchoverview')
    expect(linkElement).toBeInTheDocument()
  })

  test('functionto string rendered', () => {
    reduxRender(<App src="function x=0"/>)
    const linkElement = screen.getByTestId('dispatchoverview')
    expect(linkElement).toBeInTheDocument()
  })
 })
 