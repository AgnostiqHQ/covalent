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

import { screen, render, fireEvent } from '@testing-library/react'
import App from '../DashboardCard'
import { DashBoardCardItems } from '../DashboardCard'
import { BrowserRouter } from 'react-router-dom'
import React from 'react'
import { Provider } from 'react-redux'
import reducers from '../../../redux/reducers'
import { configureStore } from '@reduxjs/toolkit'
import theme from '../../../utils/theme'
import ThemeProvider from '@mui/system/ThemeProvider'

const initialStateMock = {
  dashboard: {
    dashboardOverview: {
      latest_running_task_status: 'COMPLETED',
      total_dispatcher_duration: 4000,
      total_jobs: 5,
      total_jobs_cancelled: 0,
      total_jobs_completed: 4,
      total_jobs_failed: 1,
      total_jobs_new_object: 0,
      total_jobs_running: 0,
    },
    fetchDashboardOverview: { isFetching: false, error: 'hi man' },
  },
}
function mockRender(renderedComponent) {
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

var initialState = {
  dashboard: {
    totalDispatches: 0,
    runningDispatches: 0,
    completedDispatches: 0,
    failedDispatches: 0,
    dashboardOverview: {},
    fetchDashboardOverview: { isFetching: false, error: 'hi man' },
  },
}

function mockRenderSlice(renderedComponent) {
  const store = configureStore({
    reducer: reducers,
    preloadedState: initialState,
  })
  return render(
    <Provider store={store}>
      <ThemeProvider theme={theme}>
        <BrowserRouter>{renderedComponent}</BrowserRouter>
      </ThemeProvider>
    </Provider>
  )
}
const dashboardCardCases = [
  'Dispatch list',
  'Total jobs running',
  'Total jobs done',
  'Latest running task status',
  'Total dispatcher duration',
]

describe('dashboard card', () => {
  test('renders dashboard', () => {
    mockRenderSlice(<App />)
    const linkElement = screen.getByTestId('dashboardCard')
    expect(linkElement).toBeInTheDocument()
  })

  test('renders error message snackbar', () => {
    mockRenderSlice(<App />)
    const linkElement = screen.getByText(
      'Something went wrong,please contact the administrator!'
    )
    expect(linkElement).toBeInTheDocument()
  })

  test('can close snackbar', async () => {
    mockRenderSlice(<App />)
    const linkElement = await screen.findByTestId('closeIcon')
    expect(linkElement).toBeInTheDocument()
    fireEvent.click(linkElement)
  })

  test.each(dashboardCardCases)('render %p section', (firstArg) => {
    mockRender(<App />)
    const element = screen.getByText(firstArg)
    expect(element).toBeInTheDocument()
  })

  test('render with dispatcher duration', () => {
    initialState = initialStateMock
    mockRenderSlice(<App />)
    const element = screen.getByTestId('dashboardCard')
    expect(element).toBeInTheDocument()
  })

  test('render DashBoardCardItems', () => {
    mockRenderSlice(<DashBoardCardItems isSkeletonPresent={true} />)
    const element = screen.getByTestId('skeleton')
    expect(element).toBeInTheDocument()
  })
})
