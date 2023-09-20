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
