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
import { screen, render } from '@testing-library/react'
import App from '../Circuit'
import { BrowserRouter } from 'react-router-dom'
import React from 'react'
import { Provider } from 'react-redux'
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

describe('Circuit Tab', () => {
    const circuitDetails = {
        "total_qbits": 2,
        "qbit1_gates": 2,
        "qbit2_gates": 1,
        "depth": 2,
        "circuit": "RX!0.7984036206686643![0]Hadamard[1]CNOT[0, 1]|||ObservableReturnTypes.Expectation!['PauliY', 'PauliX'][0, 1]"
    }
    test('circuit tab is rendered', () => {
        reduxRender(<App />)
        const linkElement = screen.getByTestId('Circuit-grid')
        expect(linkElement).toBeInTheDocument()
    })

    const filterData = Object.keys(circuitDetails);
    test.each(filterData)('checks rendering for qubit values', (arg) => {
        reduxRender(<App circuitDetails={circuitDetails} />)
        const linkElement = screen.getByTestId(arg)
        expect(linkElement).toBeInTheDocument()
    })
})
