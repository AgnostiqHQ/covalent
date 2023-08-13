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
import { fireEvent, screen, render } from '@testing-library/react'
import App from '../QElectronList'
import { BrowserRouter } from 'react-router-dom'
import React, { useState } from 'react'
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

describe('Qelectron List', () => {
    test('Qelectron List Grid is rendered', () => {
        reduxRender(<App />)
        const linkElement = screen.getByTestId('QelectronList-grid')
        expect(linkElement).toBeInTheDocument()
    })

    const data = [
        {
            "job_id": "circuit_0@6418e062-7892-4239-8734-39926c5558fc",
            "start_time": "2023-06-13T21:19:27.057015",
            "executor": "QiskitExecutor",
            "status": "COMPLETED"
        },
        {
            "job_id": "circuit_0@a86bf847-84a3-4414-adbe-2bc1d6727371",
            "start_time": "2023-06-13T21:19:27.033453",
            "executor": "QiskitExecutor",
            "status": "COMPLETED"
        },
        {
            "job_id": "circuit_0@25352acb-de2a-4195-99a8-afe60c8ff675",
            "start_time": "2023-06-13T21:19:27.009380",
            "executor": "QiskitExecutor",
            "status": "COMPLETED"
        },
        {
            "job_id": "circuit_0@75a6a5e1-63f3-4231-beea-9374705cbfc8",
            "start_time": "2023-06-13T21:19:26.960943",
            "executor": "QiskitExecutor",
            "status": "COMPLETED"
        }
    ];
    test('Qelectron List data is rendered', () => {
        reduxRender(<App data={data} />)
        const linkElement = screen.getByTestId('QelectronList-table')
        expect(linkElement).toBeInTheDocument()
    })

    test('Qelectron List empty data is rendered', () => {
        reduxRender(<App data={[]} />)
        const linkElement = screen.queryByText('No results found.')
        expect(linkElement).toBeInTheDocument()
    })

})
