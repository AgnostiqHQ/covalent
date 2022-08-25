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

import { render, screen, fireEvent } from '@testing-library/react'
import React from 'react'
import App from '../DialogBox'
import '@testing-library/jest-dom'

const dialogboxCases = ['dialogbox', 'dialogIcon', 'closeIcon']
describe('dialog box', () => {
  test.each(dialogboxCases)('render %p', (firstArg) => {
    render(<App openDialogBox={true} />)
    const element = screen.getByTestId(firstArg)
    expect(element).toBeInTheDocument()
  })

  test('action button  is rendered', () => {
    render(<App openDialogBox={true} />)
    const linkElement = screen.getAllByTestId('primarybutton')
    expect(linkElement[1]).toBeInTheDocument()
  })

  test('dialogbox action is carried out', () => {
    const handler = jest.fn()
    render(<App openDialogBox={true} handler={handler} />)
    const linkElement = screen.getAllByTestId('primarybutton')
    expect(linkElement[1]).toBeInTheDocument()
    fireEvent.click(linkElement[1])
    expect(handler).toBeCalledTimes(1)
  })

  test('dialog close button is rendered', () => {
    render(<App openDialogBox={true} />)
    const linkElement = screen.getAllByTestId('primarybutton')
    expect(linkElement[0]).toBeInTheDocument()
  })
})
