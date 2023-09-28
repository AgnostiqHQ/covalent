/**
 * This file is part of Covalent.
 *
 * Licensed under the Apache License 2.0 (the "License"). A copy of the
 * License may be obtained with this software package or at
 *
 *     https://www.apache.org/licenses/LICENSE-2.0
 *
 * Use of this file is prohibited except in compliance with the License.
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
import React from 'react'
import { render, screen, fireEvent } from '../../../testHelpers/testUtils'
import App from '../ResultListing'
import { ResultsTableHead } from '../ResultListing'
import { ResultsTableToolbar } from '../ResultListing'
import { BrowserRouter } from 'react-router-dom'
import { Provider } from 'react-redux'
import reducers from '../../../redux/reducers'
import { configureStore } from '@reduxjs/toolkit'
import theme from '../../../utils/theme'
import ThemeProvider from '@mui/system/ThemeProvider'

const initialState = {
  dashboard: {
    dashboardList: [
      {
        dispatch_id: '8d282f51-6ce5-4629-8d77-c72c9944bbbc',
        lattice_name: 'simple_workflow',
        runtime: 0,
        total_electrons: 4,
        total_electrons_completed: 4,
        started_at: '2022-10-31T14:34:46',
        ended_at: '2022-10-31T14:34:46',
        status: 'COMPLETED',
        updated_at: '2022-10-31T14:34:46',
      },
      {
        dispatch_id: 'ea0dec63-5c11-4634-a71e-46a1aa6259f2',
        lattice_name: 'simple_workflow',
        runtime: 0,
        total_electrons: 4,
        total_electrons_completed: 2,
        started_at: '2022-10-27T15:52:08',
        ended_at: '2022-10-27T15:52:08',
        status: 'FAILED',
        updated_at: '2022-10-27T15:52:08',
      },
    ],
    totalDispatches: 0,
    runningDispatches: 0,
    completedDispatches: 0,
    failedDispatches: 0,
    dashboardOverview: {},
    fetchDashboardList: { isFetching: false, error: null },
    fetchDashboardOverview: { isFetching: false, error: null },
    deleteResults: { isFetching: false, error: null },
    dispatchesDeleted: false,
  },
}
function mockRender(renderedComponent) {
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

const resultListCases = ['All', 'Completed', 'Failed', 'Running']

describe('Result Listing', () => {
  test('renders result lists section', () => {
    mockRender(<App />)
    const linkElement = screen.getByText('All')
    expect(linkElement).toBeInTheDocument()
  })
  test.each(resultListCases)('render %p sort section', (firstArg) => {
    mockRender(<App />)
    const element = screen.getByText(firstArg)
    expect(element).toBeInTheDocument()
  })

  test('renders search  section', () => {
    mockRender(<App />)
    const linkElement = screen.getByPlaceholderText('Search')
    expect(linkElement).toBeInTheDocument()
  })

  test('renders dialogBox', () => {
    mockRender(<App openDialogBox={true} />)
    const linkElement = screen.getByPlaceholderText('Search')
    expect(linkElement).toBeInTheDocument()
  })

  test('checks checkbox rendering', () => {
    mockRender(<App />)
    const linkElement = screen.getAllByTestId('checkbox')
    expect(linkElement).toHaveLength(2)
    fireEvent.click(linkElement[0])
    expect(linkElement[0]).toBeEnabled()
  })

  test('checks pagination rendering', () => {
    mockRender(<App />)
    const linkElement = screen.getByTestId('pagination')
    expect(linkElement).toBeInTheDocument()
  })

  test('checks keyboard arrow down icon rendering', () => {
    mockRender(<App />)
    const linkElement = screen.getByTestId('KeyboardArrowDownIcon')
    expect(linkElement).toBeInTheDocument()
  })
  test('checks pagination rendering with more than 10 records', () => {
    initialState.dashboard = { ...initialState.dashboard, totalDispatches: 20 }
    mockRender(<App />)
    const linkElement = screen.getByTestId('pagination')
    expect(linkElement).toBeInTheDocument()
  })
  const filterData = ['ALL', 'RUNNING', 'COMPLETED', 'FAILED']
  test.each(filterData)('checks rendering for filter values', (arg) => {
    mockRender(<ResultsTableToolbar filterValue={arg} />)
    const linkElement = screen.getByText(
      arg.charAt(0).toUpperCase() + arg.slice(1).toLowerCase()
    )
    expect(linkElement).toBeInTheDocument()
  })

  test('checks tablesortlabel click event', () => {
    mockRender(<App />)
    const element = screen.getAllByTestId('tablesortlabel')
    fireEvent.click(element[0])
    expect(element[0]).toBeEnabled()
  })

  test('checks input change event', () => {
    mockRender(<App />)
    const element = screen.getByPlaceholderText('Search')
    fireEvent.change(element)
    expect(element).toBeEnabled()
  })

  test('checks closeIconButton click event', () => {
    mockRender(<App />)
    const element = screen.getByTestId('closeIconButton')
    fireEvent.click(element)
    expect(element).toBeEnabled()
  })

  const dashboardListView = initialState.dashboard.dashboardList.map((e) => {
    return {
      dispatchId: e.dispatch_id,
      endTime: e.ended_at,
      latticeName: e.lattice_name,
      resultsDir: e.results_dir,
      status: e.status,
      error: e.error,
      runTime: e.runtime,
      startTime: e.started_at,
      totalElectrons: e.total_electrons,
      totalElectronsCompleted: e.total_electrons_completed,
    }
  })

  test('checks KeyboardArrowDownIcon click event', () => {
    const anchorFunc = jest.fn()
    const setSelectedFunc = jest.fn()
    mockRender(
      <ResultsTableHead
        dashboardListView={dashboardListView}
        setAnchorEl={anchorFunc}
        anchorEl={10}
        setSelected={setSelectedFunc}
      />
    )
    const linkElement = screen.getByTestId('KeyboardArrowDownIcon')
    fireEvent.click(linkElement)
    expect(linkElement).toBeEnabled()
    expect(anchorFunc).toHaveBeenCalled()
  })

  test.each(filterData)('checks menuitem rendering and click event', (arg) => {
    const anchorFunc = jest.fn()
    mockRender(
      <ResultsTableHead
        filterValue={arg}
        runningDispatches={10}
        completedDispatches={15}
        failedDispatches={5}
        cancelledDispatches={2}
        dashboardListView={dashboardListView}
        setAnchorEl={anchorFunc}
        anchorEl={10}
        setSelected={jest.fn()}
        setOpenDialogBoxAll={jest.fn()}
        setDeleteFilter={jest.fn()}
        setDeleteCount={jest.fn()}
      />
    )
    const linkElement = screen.getAllByTestId('menuitem')
    fireEvent.click(linkElement[0])
    expect(linkElement[0]).toBeEnabled()
    // expect(anchorFunc).toHaveBeenCalled()
  })
  test('icon button click event', () => {
    const searchfn = jest.fn()
    mockRender(
      <ResultsTableToolbar
        numSelected={5}
        setOpenDialogBox={jest.fn()}
        onSearch={searchfn()}
      />
    )
    const buttonElement = screen.getByTestId('iconButtonDelete')
    fireEvent.click(buttonElement)
    expect(buttonElement).toBeEnabled()
    const inputElement = screen.getByTestId('input')
    fireEvent.change(inputElement)
    expect(inputElement).toBeEnabled()
    expect(searchfn).toHaveBeenCalled()
  })
})
