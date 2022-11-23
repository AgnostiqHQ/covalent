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

import { screen, render } from '@testing-library/react'
import { DispatchLayout, DispatchLayoutValidate } from '../DispatchLayout'
import React from 'react'
import { BrowserRouter } from 'react-router-dom'
import { Provider } from 'react-redux'
import reducers from '../../../redux/reducers'
import { configureStore } from '@reduxjs/toolkit'
import theme from '../../../utils/theme'
import ThemeProvider from '@mui/system/ThemeProvider'

import { ReactFlowProvider } from 'react-flow-renderer'
import { HelmetProvider } from 'react-helmet-async'

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

describe('Dispatch layout contents', () => {
  test('Not found is rendered', () => {
    reduxRender(<DispatchLayoutValidate />)
    const linkElement = screen.getByTestId('logo')
    expect(linkElement).toBeInTheDocument()
  })

  test('Not found text rendered', () => {
    reduxRender(<DispatchLayoutValidate text="Page not found." />)
    const linkElement = screen.getByTestId('message')
    expect(linkElement).toBeInTheDocument()
  })

  test('dispatch layout topbar is rendered', () => {
    reduxRender(<DispatchLayout />)
    const linkElement = screen.getByTestId('topbar')
    expect(linkElement).toBeInTheDocument()
  })

  test('dispatch layout topbar card is rendered', () => {
    reduxRender(<DispatchLayout />)
    const linkElement = screen.getByTestId('topbarcard')
    expect(linkElement).toBeInTheDocument()
  })

  test('dispatch layout nav drawer is rendered', () => {
    reduxRender(<DispatchLayout />)
    const linkElement = screen.getByTestId('navDrawer')
    expect(linkElement).toBeInTheDocument()
  })

  test('dispatch layout covalent logo is rendered', () => {
    reduxRender(<DispatchLayout />)
    const linkElement = screen.getByTestId('covalentLogo')
    expect(linkElement).toBeInTheDocument()
  })

  test('dispatch layout dispatch list is rendered', () => {
    reduxRender(<DispatchLayout />)
    const linkElement = screen.getByLabelText('Dispatch list')
    expect(linkElement).toBeInTheDocument()
  })

  test('dispatch layout dashboard icon is rendered', () => {
    const { container } = reduxRender(<DispatchLayout />)
    expect(
      container.querySelector(
        'MuiSvgIcon-root MuiSvgIcon-fontSizeMedium css-1iqd9nb-MuiSvgIcon-root'
      )
    ).toBeDefined()
  })

  test('dispatch layout Lattice draw preview is rendered', () => {
    reduxRender(<DispatchLayout />)
    const linkElement = screen.getByLabelText('Lattice draw preview')
    expect(linkElement).toBeInTheDocument()
  })

  test('dispatch layout license icon is rendered', () => {
    const { container } = reduxRender(<DispatchLayout />)
    expect(
      container.querySelector(
        'MuiSvgIcon-root MuiSvgIcon-fontSizeMedium css-nc05j6-MuiSvgIcon-root'
      )
    ).toBeDefined()
  })

  test('dispatch layout lattice drawer is rendered', () => {
    reduxRender(<DispatchLayout />)
    const linkElement = screen.getByTestId('latticeDrawer')
    expect(linkElement).toBeInTheDocument()
  })

  test('dispatch layout lattice dispatch overview is rendered', () => {
    reduxRender(<DispatchLayout />)
    const linkElement = screen.getByTestId('latticedispatchoverview')
    expect(linkElement).toBeInTheDocument()
  })

  //  test('dispatch layout backbtn is rendered', () => {
  //   reduxRender(<DispatchLayout />)
  //    const linkElement = screen.getByTestId('backbtn')
  //    expect(linkElement).toBeInTheDocument()
  //  })

  test('dispatch layout icon is rendered', () => {
    reduxRender(<DispatchLayout />)
    const linkElement = screen.getByTestId('ChevronLeftIcon')
    expect(linkElement).toBeInTheDocument()
  })

  test('dispatch layout tree icon is rendered', () => {
    const { container } = reduxRender(<DispatchLayout />)
    expect(
      container.querySelector(
        'MuiSvgIcon-root MuiSvgIcon-fontSizeMedium css-khmmae-MuiSvgIcon-root'
      )
    ).toBeDefined()
  })

  test('dispatch layout copy dispatch button is rendered', () => {
    reduxRender(<DispatchLayout />)
    const linkElement = screen.getByTestId('copydispatchId')
    expect(linkElement).toBeInTheDocument()
  })

  test('dispatch layout overview text is rendered', () => {
    const { container } = reduxRender(<DispatchLayout />)
    expect(
      container.querySelector(
        'MuiButtonBase-root MuiTab-root MuiTab-textColorPrimary MuiTab-fullWidth Mui-selected css-bpxy16-MuiButtonBase-root-MuiTab-root'
      )
    ).toBeDefined()
  })

  test('dispatch layout overview button div is rendered', () => {
    reduxRender(<DispatchLayout />)
    const linkElement = screen.getByRole('tablist')
    expect(linkElement).toBeInTheDocument()
  })

  test('dispatch layout overview button is rendered', () => {
    reduxRender(<DispatchLayout />)
    const linkElement = screen.getByRole('tab')
    expect(linkElement).toBeInTheDocument()
  })

  test('dispatch layout dispatch overview is rendered', () => {
    reduxRender(<DispatchLayout />)
    const linkElement = screen.getByTestId('dispatchoverview')
    expect(linkElement).toBeInTheDocument()
  })

  test('dispatch layout page loading is rendered', () => {
    reduxRender(<DispatchLayout />)
    const linkElement = screen.getByTestId('pageLoader')
    expect(linkElement).toBeInTheDocument()
  })
})
