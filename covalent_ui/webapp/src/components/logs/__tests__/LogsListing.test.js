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
import React from 'react'
import { fireEvent, render, screen, act } from '../../../testHelpers/testUtils'
import App from '../LogsListing.js'
import { BrowserRouter } from 'react-router-dom'
import { Provider } from 'react-redux'
import reducers from '../../../redux/reducers'
import { configureStore } from '@reduxjs/toolkit'
import theme from '../../../utils/theme'
import ThemeProvider from '@mui/system/ThemeProvider'
import configureMockStore from 'redux-mock-store'
import thunk from 'redux-thunk'
import userEvent from '@testing-library/user-event'

const mockStore = configureMockStore([thunk])

function mockRenderSlice(renderedComponent) {
  const store = mockStore({
    logs: {
      fetchLogList: { isFetching: true },
      logFile: '',
      totalLogs: 1,
      logList: [
        {
          log_date: null,
          status: 'INFO',
          message:
            '/bin/sh: 1: python: not found\n\n/bin/sh: 1: python: not found\n\n/bin/sh: 1: python: not found\n\n/bin/sh: 1: python: not found',
        },
        {
          log_date: '2022-11-02 12:49:46.321000+05:30',
          status: 'INFO',
          message: '127.0.0.1:41948 - "GET /openapi.json HTTP/1.1" 200',
        },
        {
          log_date: '2022-11-02 12:49:45.960000+05:30',
          status: 'ERROR',
          message: 'connection closed',
        },
      ],
    },
  })

  return render(
    <Provider store={store}>
      <ThemeProvider theme={theme}>
        <BrowserRouter>{renderedComponent}</BrowserRouter>
      </ThemeProvider>
    </Provider>
  )
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

describe('Logs table', () => {
  test('renders logs table', () => {
    mockRenderSlice(<App />)
    const linkElement = screen.getByTestId('logsTable')
    expect(linkElement).toBeInTheDocument()
  })

  test('copy mesage on click', () => {
    mockRenderSlice(<App />)
    const linkElement = screen.getAllByTestId('copyMessage')
    expect(linkElement).toHaveLength(3)
    fireEvent.click(linkElement[0])
    const resultText = screen.getAllByText('Copied')
    expect(resultText).toHaveLength(3)
  })

  test('search works', () => {
    mockRenderSlice(<App />)
    const linkElement = screen.getAllByTestId('copyMessage')
    expect(linkElement).toHaveLength(3)
    fireEvent.click(linkElement[0])
    const resultText = screen.getAllByText('Copied')
    expect(resultText).toHaveLength(3)
  })

  test('sort header', () => {
    mockRenderSlice(<App />)
    const linkElement = screen.getAllByTestId('tableHeader')
    expect(linkElement).toHaveLength(2)
    fireEvent.click(linkElement[0])
  })

  test('download logs button works', async () => {
    mockRenderSlice(<App />)
    const linkElement = await screen.findAllByTestId('downloadButton')
    expect(linkElement).toHaveLength(2)
    act(() => fireEvent.click(linkElement[0]))

    const linkElement2 = await screen.findByText(
      'Something went wrong and could not download the file!'
    )
    expect(linkElement2).toBeInTheDocument()
  })

  test('renders search  section', () => {
    mockRender(<App />)
    const linkElement = screen.getByPlaceholderText('Search in logs')
    expect(linkElement).toBeInTheDocument()
  })

  test('renders search icon in section', () => {
    mockRender(<App />)
    const linkElement = screen.getByTestId('SearchIcon')
    expect(linkElement).toBeInTheDocument()
  })

  test('renders clear icon in search section', () => {
    const setQuery = jest.fn()
    mockRender(<App setQuery={setQuery} />)
    const linkElement = screen.getByTestId('ClearIcon')
    expect(linkElement).toBeInTheDocument()
    // const linkElement2 = screen.getByTestId('clear')
    fireEvent.click(linkElement)
  })

  test('renders table header section', () => {
    mockRender(<App />)
    const linkElement = screen.getByText('Time')
    expect(linkElement).toBeInTheDocument()
  })

  test('renders all table header columns', () => {
    mockRender(<App />)
    const linkElement1 = screen.getByText('Time')
    const linkElement2 = screen.getByText('Status')
    const linkElement3 = screen.getByText('Log')

    expect(linkElement1).toBeInTheDocument()
    expect(linkElement3).toBeInTheDocument()
    expect(linkElement2).toBeInTheDocument()
  })
  test('renders sort icon at all columns', () => {
    mockRender(<App />)
    const linkElement = screen.getAllByTestId('ArrowDownwardIcon')
    expect(linkElement).toHaveLength(2)
  })

  test('renders logs download button', () => {
    mockRender(<App />)
    const linkElement = screen.queryByTestId('downloadButton')
    expect(linkElement).not.toBeInTheDocument()
  })

  test('change search value', () => {
    mockRender(<App />)
    const linkElement = screen.getByPlaceholderText('Search in logs')
    expect(linkElement).toBeInTheDocument()
    expect(linkElement).toHaveValue('')
    userEvent.type(linkElement, 'test@mail.com')
    expect(linkElement).toHaveValue('test@mail.com')
  })
})
