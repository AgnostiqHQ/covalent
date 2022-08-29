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
import '@testing-library/jest-dom'
import { render, screen, fireEvent } from '@testing-library/react'
import copy from 'copy-to-clipboard'
import App from '../CopyButton'

document.execCommand = jest.fn()

describe('copy button', () => {
  test('renders copy button', () => {
    render(<App />)
    const element = screen.getByLabelText(/Copy/)
    expect(element).toBeInTheDocument()
  })

  test('copy icon is present', () => {
    render(<App />)
    const element = screen.getByTestId('copyIcon')
    expect(element).toBeInTheDocument()
  })

  test('copy button clicked', () => {
    render(<App title={'Copy'} />)
    const element = screen.getByLabelText('Copy')
    expect(element).toBeInTheDocument()
    fireEvent.click(element)
    const text = screen.getByLabelText('Copied!')
    expect(text).toBeInTheDocument()
  })

  test('copy icon changes after clicked', () => {
    render(<App title={'Copy'} copy={copy} />)
    const element = screen.getByLabelText('Copy')
    expect(element).toBeInTheDocument()
    fireEvent.click(element)
    expect(document.execCommand).toHaveBeenCalledWith('copy')
    const icon = screen.getByTestId('copiedIcon')
    expect(icon).toBeInTheDocument()
  })

  test('copy function carried out', () => {
    render(<App title={'Copy'} copy={copy} />)
    const element = screen.getByLabelText('Copy')
    expect(element).toBeInTheDocument()
    fireEvent.click(element)
    expect(document.execCommand).toHaveBeenCalledWith('copy')
  })
})
