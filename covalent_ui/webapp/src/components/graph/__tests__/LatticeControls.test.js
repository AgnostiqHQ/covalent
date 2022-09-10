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

import { render, screen, fireEvent, waitFor, cleanup } from '@testing-library/react'
import App from '../LatticeControls'
import "@testing-library/jest-dom";
import React from 'react'
import { Provider } from 'react-redux'
import reducers from '../../../redux/reducers'
import { configureStore } from '@reduxjs/toolkit'
import theme from '../../../utils/theme'
import ThemeProvider from '@mui/system/ThemeProvider'
import { BrowserRouter } from 'react-router-dom'
import { ReactFlowProvider } from 'react-flow-renderer'
import { HelmetProvider } from 'react-helmet-async'

import { act, renderHook } from '@testing-library/react-hooks'
import userEvent from "@testing-library/user-event";

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

  const direction = ["TB"]
  const setDirection = ['BT']

  const direction1 = ["BT"]
  const setDirection1 = ['LR']

  const direction2 = ["LR"]
  const setDirection2 = ['RL']

  const direction3 = ["RL"]
  const setDirection3 = ['TB']

  afterEach(cleanup)

  test('should render downward icon', () => {
    const container = reduxRender(<App direction={direction} setDirection={setDirection} />);
    const { result } = renderHook(() => <App direction={direction} setDirection={setDirection} />)
    const linkElement = screen.getByLabelText("Change orientation");
    userEvent.click(linkElement)
    act(() => { result.current.props })
    expect(result.current.props.direction).toBe(direction)
    expect(result.current.props.setDirection).toBe(setDirection)
    expect(screen.getByTestId("ArrowDownwardIcon")).toBeInTheDocument()
  })

  test('should render upward icon', () => {
    const container = reduxRender(<App direction={direction1} setDirection={setDirection1} />);
    const { result } = renderHook(() => <App direction={direction1} setDirection={setDirection1} />)
    const linkElement = screen.getByLabelText("Change orientation");
    userEvent.click(linkElement)
    act(() => { result.current.props })
    expect(result.current.props.direction).toBe(direction1)
    expect(result.current.props.setDirection).toBe(setDirection1)
    expect(screen.getByTestId("ArrowUpwardIcon")).toBeInTheDocument()
  })

  test('should render back icon', () => {
    const container = reduxRender(<App direction={direction2} setDirection={setDirection2} />);
    const { result } = renderHook(() => <App direction={direction2} setDirection={setDirection2} />)
    const linkElement = screen.getByLabelText("Change orientation");
    userEvent.click(linkElement)
    act(() => { result.current.props })
    expect(result.current.props.direction).toBe(direction2)
    expect(result.current.props.setDirection).toBe(setDirection2)
    expect(screen.getByTestId("ArrowForwardIcon")).toBeInTheDocument()
  })

  test('should render forward icon', () => {
    const container = reduxRender(<App direction={direction3} setDirection={setDirection3} />);
    const { result } = renderHook(() => <App direction={direction3} setDirection={setDirection3} />)
    const linkElement = screen.getByLabelText("Change orientation");
    userEvent.click(linkElement)
    act(() => { result.current.props })
    expect(result.current.props.direction).toBe(direction3)
    expect(result.current.props.setDirection).toBe(setDirection3)
    expect(screen.getByTestId("ArrowBackIcon")).toBeInTheDocument()
  })

})
