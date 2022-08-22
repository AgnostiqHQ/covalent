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

import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import App from '../LatticeControls'
import "@testing-library/jest-dom";
import { ToggleButton, ToggleButtonGroup, Tooltip } from '@mui/material'
import {
  Add as PlusIcon,
  ArrowBack,
  ArrowDownward,
  ArrowForward,
  ArrowUpward,
  Fullscreen,
  LockOpenOutlined,
  LockOutlined,
  MapOutlined,
  Remove as MinusIcon,
} from '@mui/icons-material'
import React from 'react'
import { Provider } from 'react-redux'
import reducers from '../../../redux/reducers'
import { configureStore } from '@reduxjs/toolkit'
import theme from '../../../utils/theme'
import ThemeProvider from '@mui/system/ThemeProvider'
import { BrowserRouter } from 'react-router-dom'

import { ReactFlowProvider } from 'react-flow-renderer'
import { HelmetProvider } from 'react-helmet-async'

const onSubmit = jest.fn();

function reduxRender(rederedComponent) {
  const store = configureStore({
    reducer: reducers,
  })
  return render(
    <Provider store={store}>
      <HelmetProvider>
        <ReactFlowProvider>
          <ThemeProvider theme={theme}>
            <BrowserRouter>{rederedComponent}</BrowserRouter>
          </ThemeProvider>
        </ReactFlowProvider>
      </HelmetProvider>
    </Provider>
  )
}

describe('lattice toggle buttons', () => {
  test('renders toggle for zoom-in button', async () => {
    reduxRender(<App openDialogBox={true} title={'Zoom in'} />)
    const linkElement = screen.getByTestId('AddIcon')
    fireEvent.click(screen.getByTestId('AddIcon'))
    await waitFor(() => screen.getByLabelText('Zoom in'))
    expect(screen.getByLabelText('Zoom in')).toBeInTheDocument('Zoom in')
    expect(linkElement).toBeInTheDocument()
  })

  test('renders zoom out button', async () => {
    reduxRender(<App openDialogBox={true} title={'Zoom out'} />)
    const linkElement = screen.getByTestId('RemoveIcon')
    fireEvent.click(screen.getByTestId('RemoveIcon'))
    await waitFor(() => screen.getByLabelText('Zoom out'))
    expect(screen.getByLabelText('Zoom out')).toBeInTheDocument('Zoom out')
    expect(linkElement).toBeVisible();
  })

  test('renders fit to screen button', async () => {
    // const handleClick = jest.fn()
    reduxRender(<App openDialogBox={true} title={'Fit to screen'} />)
    const linkElement = screen.getByTestId('FullscreenIcon')
    fireEvent.click(screen.getByTestId('FullscreenIcon'))
    await waitFor(() => screen.getByLabelText('Fit to screen'))
    expect(screen.getByLabelText('Fit to screen')).toBeInTheDocument('Fit to screen')
    expect(linkElement).toBeVisible();
  })

  test('renders toggle minimap button', async () => {
    reduxRender(<App openDialogBox={true} title={'Toggle minimap'} />)
    const linkElement = screen.getByTestId('MapOutlinedIcon')
    fireEvent.click(screen.getByTestId('MapOutlinedIcon'))
    await waitFor(() => screen.getByLabelText('Toggle minimap'))
    expect(screen.getByLabelText('Toggle minimap')).toBeInTheDocument('Toggle minimap')
    expect(linkElement).toBeVisible();
  })

  test('renders toggle draggable nodes button', async () => {
    reduxRender(<App openDialogBox={true} title={'Change orientation'} />)
    const linkElement = screen.getByLabelText('Change orientation')
    fireEvent.click(screen.getByLabelText('Change orientation'))
    await waitFor(() => screen.getByLabelText('Change orientation'))
    expect(screen.getByLabelText('Change orientation')).toBeInTheDocument('Change orientation')
    expect(linkElement).toBeVisible();
  })

  test('renders toggle draggable nodes button', async () => {
    reduxRender(<App openDialogBox={true} title={'Toggle draggable nodes'} />)
    const linkElement = screen.getByTestId('LockOutlinedIcon')
    fireEvent.click(screen.getByTestId('LockOutlinedIcon'))
    await waitFor(() => screen.getByLabelText('Toggle draggable nodes'))
    expect(screen.getByLabelText('Toggle draggable nodes')).toBeInTheDocument('Toggle draggable nodes')
    expect(linkElement).toBeVisible();
  })

  test('renders toggle parameters nodes button', async () => {
    reduxRender(<App openDialogBox={true} title={'Toggle parameters'} />)
    const linkElement = screen.getByLabelText('Toggle parameters')
    fireEvent.click(screen.getByLabelText('Toggle parameters'))
    await waitFor(() => screen.getByLabelText('Toggle parameters'))
    expect(screen.getByLabelText('Toggle parameters')).toBeInTheDocument('Toggle parameters')
    expect(linkElement).toBeVisible();
  })
})