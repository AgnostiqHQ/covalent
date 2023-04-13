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

import {
  render,
  screen,
  fireEvent,
  waitFor,
  cleanup,
} from '@testing-library/react'
import App from '../LatticeControlsElk'
import '@testing-library/jest-dom'
import React from 'react'
import { Provider } from 'react-redux'
import reducers from '../../../redux/reducers'
import { configureStore } from '@reduxjs/toolkit'
import theme from '../../../utils/theme'
import ThemeProvider from '@mui/system/ThemeProvider'
import { BrowserRouter } from 'react-router-dom'
import { ReactFlowProvider } from 'react-flow-renderer'
import { HelmetProvider } from 'react-helmet-async'
import { renderHook } from '@testing-library/react-hooks'

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
    fireEvent.click(linkElement)
    await waitFor(() => screen.getByLabelText('Zoom in'))
    expect(screen.getByLabelText('Zoom in')).toBeInTheDocument('Zoom in')
    expect(linkElement).toBeInTheDocument()
  })

  test('renders zoom out button', async () => {
    reduxRender(<App openDialogBox={true} title={'Zoom out'} />)
    const linkElement = screen.getByTestId('RemoveIcon')
    fireEvent.click(linkElement)
    await waitFor(() => screen.getByLabelText('Zoom out'))
    expect(screen.getByLabelText('Zoom out')).toBeInTheDocument('Zoom out')
    expect(linkElement).toBeVisible()
  })

  test('renders fit to screen button', async () => {
    reduxRender(<App openDialogBox={true} title={'Fit to screen'} />)
    const linkElement = screen.getByTestId('FullscreenIcon')
    fireEvent.click(linkElement)
    await waitFor(() => screen.getByLabelText('Fit to screen'))
    expect(screen.getByLabelText('Fit to screen')).toBeInTheDocument(
      'Fit to screen'
    )
    expect(linkElement).toBeVisible()
  })

  test('renders hide labels nodes button', async () => {
    const handleHideLabels = jest.fn()
    reduxRender(
      <App
        openDialogBox={true}
        title={'hideLabels'}
        handleHideLabels={handleHideLabels}
      />
    )
    const linkElement = screen.getByTestId('LabelIcon')
    fireEvent.click(linkElement)
    await waitFor(() => screen.getByLabelText('Hide labels'))
    expect(handleHideLabels).toBeDefined()
    expect(screen.getByLabelText('Hide labels')).toBeInTheDocument(
      'Hide labels'
    )
    expect(linkElement).toBeVisible()
  })

  test('renders Layout option button', async () => {
    reduxRender(<App openDialogBox={true} title={'Change layout'} />)
    const linkElement = screen.getByTestId('DashboardIcon')
    expect(linkElement).toBeVisible()
  })

  test('renders toggle minimap button', async () => {
    reduxRender(<App openDialogBox={true} title={'Toggle minimap'} />)
    const linkElement = screen.getByTestId('MapOutlinedIcon')
    fireEvent.click(linkElement)
    await waitFor(() => screen.getByLabelText('Toggle minimap'))
    expect(screen.getByLabelText('Toggle minimap')).toBeInTheDocument(
      'Toggle minimap'
    )
    expect(linkElement).toBeVisible()
  })

  test('renders toggle draggable nodes button', async () => {
    reduxRender(<App openDialogBox={true} title={'Change orientation'} />)
    const linkElement = screen.getByLabelText('Change orientation')
    fireEvent.click(linkElement)
    await waitFor(() => screen.getByLabelText('Change orientation'))
    expect(screen.getByLabelText('Change orientation')).toBeInTheDocument(
      'Change orientation'
    )
    expect(linkElement).toBeVisible()
  })

  test('renders toggle draggable nodes buttons', async () => {
    reduxRender(<App openDialogBox={true} title={'Toggle draggable nodes'} />)
    const linkElement = screen.getByTestId('LockOutlinedIcon')
    fireEvent.click(linkElement)
    await waitFor(() => screen.getByLabelText('Toggle draggable nodes'))
    expect(screen.getByLabelText('Toggle draggable nodes')).toBeInTheDocument(
      'Toggle draggable nodes'
    )
    expect(linkElement).toBeVisible()
  })

  test('renders toggle parameters nodes button', async () => {
    reduxRender(<App openDialogBox={true} title={'Toggle parameters'} />)
    const linkElement = screen.getByLabelText('Toggle parameters')
    fireEvent.click(linkElement)
    await waitFor(() => screen.getByLabelText('Toggle parameters'))
    expect(screen.getByLabelText('Toggle parameters')).toBeInTheDocument(
      'Toggle parameters'
    )
    expect(linkElement).toBeVisible()
  })

  test('renders toggle parameters tooglebuttonclick', async () => {
    reduxRender(<App />)
    const linkElement = screen.getByTestId('tooglebuttonclick')
    expect(linkElement).toBeInTheDocument()
  })

  test('toggle button Click rendered', () => {
    const handleClick = jest.fn()
    reduxRender(<App handleClick={handleClick} />)
    const linkElement = screen.getByTestId('tooglebuttonclick')
    fireEvent.click(linkElement)
  })

  test('renders changeorientation', async () => {
    reduxRender(<App />)
    const linkElement = screen.getByTestId('changeorientation')
    expect(linkElement).toBeInTheDocument()
  })

  test('renders handlelabelhide', async () => {
    reduxRender(<App />)
    const linkElement = screen.getByTestId('handlelabelhide')
    expect(linkElement).toBeInTheDocument()
  })

  test('renders handlelabelhide title Show labels rendered', async () => {
    reduxRender(<App hideLabels="Show labels" />)
    const linkElement = screen.getByTestId('handlelabelhide')
    expect(linkElement).toBeInTheDocument()
  })

  test('renders handlelabelhide title Hide labels rendered', async () => {
    reduxRender(<App hideLabels="Hide labels" />)
    const linkElement = screen.getByTestId('handlelabelhide')
    expect(linkElement).toBeInTheDocument()
  })

  test('renders toggleparams', async () => {
    reduxRender(<App />)
    const linkElement = screen.getByTestId('toggleparams')
    expect(linkElement).toBeInTheDocument()
  })

  test('renders toggledragablenode', async () => {
    reduxRender(<App />)
    const linkElement = screen.getByTestId('toggledragablenode')
    expect(linkElement).toBeInTheDocument()
  })

  test('toggledragablenode onclicked rendered', () => {
    const toggleNodesDraggable = jest.fn()
    reduxRender(<App toggleNodesDraggable={toggleNodesDraggable} />)
    const linkElement = screen.getByTestId('toggledragablenode')
    fireEvent.click(linkElement)
  })

  const direction = ['DOWN']

  const direction1 = ['UP']

  const direction2 = ['LEFT']

  const direction3 = ['RIGHT']

  afterEach(cleanup)

  it('render the change orientation left button', () => {
    const { result } = renderHook(() => <App direction={direction1} />)
    expect(result.current.props.direction).toBe(direction1)
  })

  it('render the change orientation up button', () => {
    const { result } = renderHook(() => <App direction={direction2} />)
    expect(result.current.props.direction).toBe(direction2)
  })

  it('render the change orientation right button', () => {
    const { result } = renderHook(() => <App direction={direction3} />)
    expect(result.current.props.direction).toBe(direction3)
  })

  it('render the change orientation down button', () => {
    const { result } = renderHook(() => <App direction={direction} />)
    expect(result.current.props.direction).toBe(direction)
  })

  test('renders up button for change orientation', async () => {
    const setStateMock = jest.fn()
    const useStateMock = (useState) => [useState, setStateMock]
    jest.spyOn(React, 'useState').mockImplementation(useStateMock)

    reduxRender(<App direction={direction1} />)
    const linkElement = screen.getByTestId('changeorientation')
    fireEvent.click(linkElement)
    const elementLink = screen.getByTestId('ArrowUpwardIcon')
    expect(elementLink).toBeInTheDocument('')
  })

  test('renders left button for change orientation', async () => {
    const setStateMock = jest.fn()
    const useStateMock = (useState) => [useState, setStateMock]
    jest.spyOn(React, 'useState').mockImplementation(useStateMock)

    reduxRender(<App direction={direction2} />)
    const linkElement = screen.getByTestId('changeorientation')
    fireEvent.click(linkElement)
    const elementLink = screen.getByTestId('ArrowBackIcon')
    expect(elementLink).toBeInTheDocument('')
  })

  test('renders right button for change orientation', async () => {
    const setStateMock = jest.fn()
    const useStateMock = (useState) => [useState, setStateMock]
    jest.spyOn(React, 'useState').mockImplementation(useStateMock)

    reduxRender(<App direction={direction3} />)
    const linkElement = screen.getByTestId('changeorientation')
    fireEvent.click(linkElement)
    const elementLink = screen.getByTestId('ArrowForwardIcon')
    expect(elementLink).toBeInTheDocument()
  })
})
