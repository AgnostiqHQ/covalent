/**
 * Copyright 2023 Agnostiq Inc.
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
