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
import { render, screen } from '../../../testHelpers/testUtils'
import { fireEvent } from '@testing-library/react'
import App from '../SettingsCard.js'
import { BrowserRouter } from 'react-router-dom'
import { Provider } from 'react-redux'
import configureMockStore from 'redux-mock-store'
import thunk from 'redux-thunk'
import theme from '../../../utils/theme'
import ThemeProvider from '@mui/system/ThemeProvider'

const mockStore = configureMockStore([thunk])

function mockRender(renderedComponent) {
  const store = mockStore({
    dataRes: { popupData: 'covalent' },
    settingsResults: {
      settingsList: {
        client: {
          sdk: {
            config_file: '/home/kamaleshsuresh/.config/covalent/covalent.conf',
            log_dir: '/home/kamaleshsuresh/.cache/covalent',
            log_level: 'warning',
            enable_logging: 'false',
            executor_dir:
              '/home/kamaleshsuresh/.config/covalent/executor_plugins',
            no_cluster: 'false',
          },
          executors: {
            dask: {
              log_stdout: 'stdout.log',
              log_stderr: 'stderr.log',
              cache_dir: '/home/kamaleshsuresh/.cache/covalent',
            },
            remote_executor: {
              poll_freq: 15,
              remote_cache: '.cache/covalent',
              credentials_file: '',
            },
            local: {
              log_stdout: 'stdout.log',
              log_stderr: 'stderr.log',
              cache_dir: '/home/kamaleshsuresh/.cache/covalent',
            },
          },
        },
        server: {
          dispatcher: {
            address: 'localhost',
            port: 48008,
            cache_dir: '/home/kamaleshsuresh/.cache/covalent',
            results_dir: 'results',
            log_dir: '/home/kamaleshsuresh/.cache/covalent',
            db_path:
              '/home/kamaleshsuresh/.local/share/covalent/dispatcher_db.sqlite',
          },
          dask: {
            cache_dir: '/home/kamaleshsuresh/.cache/covalent',
            log_dir: '/home/kamaleshsuresh/.cache/covalent',
            mem_per_worker: 'auto',
            threads_per_worker: 1,
            num_workers: 8,
            scheduler_address: 'tcp://127.0.0.1:44409',
            dashboard_link: 'http://127.0.0.1:8787/status',
            process_info:
              "<DaskCluster name='LocalDaskCluster' parent=7676 started>",
            pid: 7704,
            admin_host: '127.0.0.1',
            admin_port: 39797,
          },
          workflow_data: {
            storage_type: 'local',
            base_dir:
              '/home/kamaleshsuresh/.local/share/covalent/workflow_data',
          },
          user_interface: {
            address: 'localhost',
            port: 48008,
            dev_port: 49009,
            log_dir: '/home/kamaleshsuresh/.cache/covalent',
          },
        },
      },
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

describe('Settings card', () => {
  test('renders settings layout section', () => {
    mockRender(<App />)
    const linkElement = screen.getByText('Settings')
    expect(linkElement).toBeInTheDocument()
  })

  test('renders menu section', () => {
    mockRender(<App />)
    const linkElement1 = screen.getAllByText('SDK')
    const linkElement2 = screen.getByText('Executors')
    const linkElement3 = screen.getByText('Dispatcher')
    const linkElement4 = screen.getByText('Dask cluster')
    const linkElement5 = screen.getByText('Workflow Data')
    const linkElement6 = screen.getByText('User Interface')

    expect(linkElement1).toHaveLength(2)
    expect(linkElement2).toBeInTheDocument()
    expect(linkElement3).toBeInTheDocument()
    expect(linkElement4).toBeInTheDocument()
    expect(linkElement5).toBeInTheDocument()
    expect(linkElement6).toBeInTheDocument()
  })

  test('renders menu child section', () => {
    mockRender(<App />)
    const linkElement = screen.getByText('Executors')
    expect(linkElement).toBeInTheDocument()
    fireEvent.click(linkElement)
    const executorMenus = [
      { name: 'Dask cluster', length: 3 },
      { name: 'Remote Executor', length: 2 },
      { name: 'Local', length: 2 },
    ]

    for (let i = 0; i < executorMenus.length; i++) {
      const linkElement = screen.getAllByText(executorMenus[i].name)
      expect(linkElement).toHaveLength(executorMenus[i].length)
    }

  })
})
