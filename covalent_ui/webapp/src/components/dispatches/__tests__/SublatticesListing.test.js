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
import { render, screen , fireEvent} from '../../../testHelpers/testUtils'
import App from '../SublatticesListing.js'
import { BrowserRouter } from 'react-router-dom'
import { Provider } from 'react-redux'
import reducers from '../../../redux/reducers'
import { configureStore } from '@reduxjs/toolkit'
import theme from '../../../utils/theme'
import ThemeProvider from '@mui/system/ThemeProvider'

const initialState = {
  latticeResults:{
  latticeDetails: {},
  latticeError: {},
  latticeOutput: {},
  latticeResult: {},
  latticeInput: {},
  latticeFunctionString: {},
  latticeExecutorDetail: {},
  sublatticesList: [{
    "dispatch_id": "cfef46ea-6539-4ace-87fe-617d09a0086c",
    "lattice_name": "mul",
    "runtime": 0,
    "total_electrons": 6,
    "total_electrons_completed": 6,
    "started_at": "2022-11-02T13:14:51",
    "ended_at": "2022-11-02T13:14:51",
    "status": "COMPLETED",
    "updated_at": "2022-11-02T13:14:51"
  },
  {
    "dispatch_id": "5a97fa3b-d564-47b4-8dd8-5559d22f0046",
    "lattice_name": "div",
    "runtime": 1000,
    "total_electrons": 6,
    "total_electrons_completed": 6,
    "started_at": "2022-11-02T13:14:51",
    "ended_at": "2022-11-02T13:14:52",
    "status": "COMPLETED",
    "updated_at": "2022-11-02T13:14:52"
  }],
  latticeDetailsResults: { isFetching: false, error: null },
  latticeResultsList: { isFetching: false, error: null },
  latticeOutputList: { isFetching: false, error: null },
  latticeFunctionStringList: { isFetching: false, error: null },
  latticeInputList: { isFetching: false, error: null },
  latticeErrorList: { isFetching: false, error: null },
  latticeExecutorDetailList: { isFetching: false, error: null },
  sublatticesListResults: { isFetching: false, error: null },
  sublatticesDispatchId: null
  }
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

describe('sublattice table', () => {
  test('renders sublattice table', () => {
    mockRender(<App />)
    const linkElement = screen.getByTestId('sublatticeTable')
    expect(linkElement).toBeInTheDocument()
  })
  test('checks click event of tablesortlabel', () => {
    mockRender(<App />)
    const element = screen.queryAllByTestId("tablesortlabel")
    fireEvent.click(element[0]);
    expect(element[0]).toBeEnabled();
  })
  test('checks click event of sublattice TableRow', () => {
    mockRender(<App />)
    const element = screen.getAllByTestId("tableRowSublattice")
    fireEvent.click(element[0]);
    expect(element[0]).toBeEnabled();
  })
})
