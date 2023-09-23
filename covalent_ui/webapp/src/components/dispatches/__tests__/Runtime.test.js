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
import App from '../Runtime'

describe('Runtime', () => {
  test('renders runtime section', () => {
    render(
      <App startTime="2022-08-09T11:25:30" endTime="2022-08-09T11:28:30" />
    )
    const linkElement = screen.getByTestId('runTime')
    expect(linkElement).toBeInTheDocument()
  })
  test('renders runtime data', () => {
    render(
      <App startTime="2021-08-09T11:25:30" endTime="2022-08-09T11:28:30" />
    )
    const linkElement = screen.getByText('8760h 3m')
    expect(linkElement).toBeInTheDocument()
  })
  test('renders runtime on running', () => {
    render(<App startTime="2022-08-09T11:25:30" />)
    const linkElement = screen.getByTestId('runTime')
    expect(linkElement).toBeInTheDocument()
  })

  test('renders invalid', () => {
    render(<App />)
    const linkElement = screen.queryByTestId('runTime')
    expect(linkElement).not.toBeInTheDocument()
  })
})
