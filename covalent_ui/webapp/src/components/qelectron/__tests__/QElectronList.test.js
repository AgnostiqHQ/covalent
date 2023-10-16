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

function reduxRenderMock(renderedComponent) {
    const initialState = {
        electronResults: {
            qelectronJobsList: {
                isFetching: true
            }
        }
    }
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
        reduxRender(<App data={data} setExpanded={jest.fn()} rowClick={jest.fn()} />)
        const linkElement = screen.getByTestId('QelectronList-table')
        expect(linkElement).toBeInTheDocument()
        const ele = screen.queryAllByTestId('tableHeader');
        expect(ele[0]).toBeInTheDocument()
        fireEvent.click(ele[0])
        const ele1 = screen.queryAllByTestId('copyMessage');
        expect(ele1[0]).toBeInTheDocument()
        fireEvent.click(ele1[0])
    })

    test('Qelectron List empty data is rendered', () => {
        reduxRender(<App data={[]} />)
        const linkElement = screen.queryByText('No results found.')
        expect(linkElement).toBeInTheDocument()
    })

    test('Qelectron List empty data with isFetching', () => {
        reduxRenderMock(<App data={[]} electronId={1} />)
        const linkElement = screen.queryByText('No results found.')
        expect(linkElement).not.toBeInTheDocument()
    })

})
