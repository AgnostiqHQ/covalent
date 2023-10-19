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

import { render, screen } from '@testing-library/react'
import App from '../ExecutorSection'

const metadata = {
  executor: {
    log_stdout: 'stdout.log',
    log_stderr: 'stderr.log',
    cache_dir: '/home/kamaleshsuresh/.cache/covalent',
    time_limit: '-1',
    retries: '0',
  },
  results_dir: '/home/kamaleshsuresh/Downloads/Dispatches/results',
  workflow_executor: 'local',
  deps: {},
  call_before: [],
  call_after: [],
  executor_data: {},
  workflow_executor_data: {},
  executor_name: 'local',
}

describe('executor section', () => {
  test('renders Executor section', () => {
    render(
      <App
        metadata={metadata}
        sx={(theme) => ({ bgcolor: theme.palette.background.outRunBg })}
      />
    )
    const linkElement = screen.getByTestId('executorSection')
    expect(linkElement).toBeInTheDocument()
  })
  test('renders Executor type', () => {
    render(
      <App
        metadata={metadata}
        sx={(theme) => ({ bgcolor: theme.palette.background.outRunBg })}
      />
    )
    const linkElement = screen.getByText('Executor:')
    expect(linkElement).toBeInTheDocument()
  })
  test('renders Executor details', () => {
    render(<App metadata={metadata} />)
    const linkElement = screen.getByText(/local/i)
    expect(linkElement).toBeInTheDocument()
  })
  test('renders preview section', () => {
    render(<App preview="dask" />)
    const linkElement = screen.getByTestId('executorSection')
    expect(linkElement).toBeInTheDocument()
  })
})
