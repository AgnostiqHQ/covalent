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

  test('rendering by passing props', () => {
    render(
      <App
        title={'Copy'}
        copy={copy}
        borderRadius={10}
        width="10px"
        height="10px"
      />
    )
    const jsdomAlert = window.prompt
    window.prompt = () => {}
    const element = screen.getByLabelText('Copy')
    expect(element).toBeInTheDocument()
    fireEvent.click(element)
    expect(document.execCommand).toHaveBeenCalledWith('copy')
    window.prompt = jsdomAlert
  })
})
