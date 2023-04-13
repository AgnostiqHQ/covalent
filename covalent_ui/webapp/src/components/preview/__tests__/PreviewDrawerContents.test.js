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

import App from '../PreviewDrawerContents'
import React from 'react'
import { render, screen } from '../../../testHelpers/testUtils'
import { BrowserRouter } from 'react-router-dom'
import reducers from '../../../redux/reducers'
import { configureStore } from '@reduxjs/toolkit'
import * as redux from 'react-redux'

function mockRender(renderedComponent) {
  const store = configureStore({
    reducer: reducers,
  })
  return render(
    <redux.Provider store={store}>
      <BrowserRouter>{renderedComponent}</BrowserRouter>
    </redux.Provider>
  )
}

const previewCases = [
  ['previewdrawer', 'Status'],
  ['Description', 'covalent'],
  ['status', 'Status'],
  ['Executor', 'dask'],
  ['Input', 'args:'],
  ['Syntax highlighter', '# source unavailable'],
]
describe('preview drawer section', () => {
  test.each(previewCases)('renders  %p section', (firstArgs, secongArgs) => {
    const spy = jest.spyOn(redux, 'useSelector')
    spy.mockReturnValue({
      lattice: {
        doc: 'covalent',
        inputs: {
          data: {
            args: [],
            kwargs: { n: '15', serial: 'True', parallel: 'True' },
          },
          python_object: 'import pickle',
        },
        metadata: {
          executor_name: 'dask',
          executor_details: {
            attributes: {
              log_stdout: 'log_stdout.txt',
              log_stderr: 'log_stderr.txt',
            },
          },
        },
        src: '',
      },
    })
    mockRender(<App />)
    const linkElement = screen.getByText(secongArgs)
    expect(linkElement).toBeInTheDocument()
  })
})
