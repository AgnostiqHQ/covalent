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
import App from '../ResultSection'

describe('Result Section', () => {
  test('renders component with isFetching false', () => {
    render(
      <App
        results={{
          data: '"Hello, World!"',
          python_object:
            "import pickle\npickle.loads(b'\\x80\\x05\\x95\\x11\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x8c\\rHello, World!\\x94.')",
        }}
        isFetching={false}
      />
    )
    const headerElement = screen.getByTestId('resultSection')
    expect(headerElement).toBeInTheDocument()
    const tooltipElement = screen.getByLabelText('Copy python object')
    expect(tooltipElement).toBeInTheDocument()
  })

  test('renders component with isFetching true', () => {
    render(
      <App
        results={{
          data: '"Hello, World!"',
          python_object:
            "import pickle\npickle.loads(b'\\x80\\x05\\x95\\x11\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x8c\\rHello, World!\\x94.')",
        }}
        isFetching={true}
      />
    )
    const element = screen.getByTestId('skeleton')
    expect(element).toBeInTheDocument()
  })

  test('on clicking copy', () => {
    render(
      <App
        results={{
          data: '"Hello, World!"',
          python_object:
            "import pickle\npickle.loads(b'\\x80\\x05\\x95\\x11\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x8c\\rHello, World!\\x94.')",
        }}
        isFetching={false}
      />
    )
    const jsdomAlert = window.prompt
    window.prompt = () => {}
    const tooltipElement = screen.getByLabelText('Copy python object')
    expect(tooltipElement).toBeInTheDocument()
    fireEvent.click(tooltipElement)
    const text = screen.getByLabelText('Python object copied')
    expect(text).toBeInTheDocument()
    window.prompt = jsdomAlert
  })

  test('renders component with preview value', () => {
    render(
      <App
        results={{
          data: '"Hello, World!"',
          python_object:
            "import pickle\npickle.loads(b'\\x80\\x05\\x95\\x11\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x8c\\rHello, World!\\x94.')",
        }}
        isFetching={false}
        preview={true}
      />
    )
    const headerElement = screen.getByTestId('resultSection')
    expect(headerElement).toBeInTheDocument()
  })
})
