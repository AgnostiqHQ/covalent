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
import React from 'react'
import { render, screen } from '@testing-library/react'
import App from '../ResultProgress'

const result = {
  dispatchId: '788a2b4b-8cf0-4e2f-8591-b7135032dcde',
  endTime: '2022-08-05T17:47:55',
  error: undefined,
  latticeName: 'workflow',
  resultsDir: undefined,
  runTime: 0,
  startTime: '2022-08-05T17:47:55',
  status: 'COMPLETED',
  totalElectrons: 7,
  totalElectronsCompleted: 7,
}

describe('Result progress', () => {
  test('renders result progress section', () => {
    render(<App result={result} />)
    const linkElement = screen.getByTestId('resultProgress')
    expect(linkElement).toBeInTheDocument()
  })
  test('renders result  status', () => {
    render(<App result={result} />)
    const linkElement = screen.getByText('7')
    expect(linkElement).toBeInTheDocument()
  })
})
