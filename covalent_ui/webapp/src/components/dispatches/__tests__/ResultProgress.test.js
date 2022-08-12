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
