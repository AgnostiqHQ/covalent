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
import App from '../QElectronDrawer'
import { BrowserRouter } from 'react-router-dom'
import React, { useState } from 'react'
import { Provider } from 'react-redux'
import reducers from '../../../redux/reducers'
import { configureStore } from '@reduxjs/toolkit'
import theme from '../../../utils/theme'
import ThemeProvider from '@mui/system/ThemeProvider'

function reduxRender(renderedComponent) {
    const initialState = {
        electronResults: {
            qelectronJobsList: {
                error: true
            },
            qelectronJobOverviewList: {
                error: true
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


function reduxRenderMock(renderedComponent) {
    const initialState = {
        electronResults: {
            qelectronJobsList: {
                error: {
                    detail: [{ 'msg': 'Something went wrong' }]
                }
            },
            qelectronJobOverviewList: {
                error: {
                    detail: [{ 'msg': 'Something went wrong' }]
                }
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

describe('Qelectron drawer', () => {

    test('Qelectron Drawer is rendered', () => {
        reduxRender(<App openQelectronDrawer={true} electronId={1} toggleQelectron={jest.fn()} />)
        const linkElement = screen.getByTestId('qElectronDrawer')
        expect(linkElement).toBeInTheDocument()
    })

    test('Qelectron Drawer is rendered with error detail', () => {
        reduxRenderMock(<App />)
        const linkElement = screen.getByTestId('qElectronDrawer')
        expect(linkElement).toBeInTheDocument()
        const ele = screen.getByTestId('qElectronDrawerSnackbar')
        expect(ele).toBeInTheDocument()
        fireEvent.click(ele)
    })

})
