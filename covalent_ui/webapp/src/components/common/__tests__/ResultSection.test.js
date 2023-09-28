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
