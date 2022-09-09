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
