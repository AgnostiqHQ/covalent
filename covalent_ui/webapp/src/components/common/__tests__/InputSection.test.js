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

import { fireEvent, render, screen } from '@testing-library/react'
import App from '../InputSection'

jest.mock('copy-to-clipboard')

const data = {
  data: {
    args: [],
    kwargs: { n: '15', serial: 'True', parallel: 'True' },
  },
  python_object: 'import pickle',
}

test('renders input section', () => {
  render(<App inputs={data} preview />)
  const linkElement = screen.getByTestId('inputSection')
  expect(linkElement).toBeInTheDocument()
})

const inputSectionCases = [
  ['input', 'Input'],
  ['code', 'args:'],
]

test.each(inputSectionCases)('render %p data', (firstArgs, secongArgs) => {
  render(<App inputs={data} preview />)
  const element = screen.getByText(secongArgs)
  expect(element).toBeInTheDocument()
})

test('renders skeleton section', () => {
  render(<App isFetching />)
  const element = screen.getByTestId('inputSectionSkeleton')
  expect(element).toBeInTheDocument()
})

test('renders copy section', () => {
  render(<App inputs={data} preview />)
  const element = screen.getByTestId('copySection')
  expect(element).toBeInTheDocument()
})

test('input section copy works', () => {
  jest.mock('../InputSection', () => ({
    copy: jest.fn(),
  }))

  render(<App inputs={data} preview />)
  const element = screen.getByTestId('copySection')
  expect(element).toBeInTheDocument()
  fireEvent.click(element)
  // fireEvent(element, new MouseEvent('click', { copied: true }))
  // const findText = screen.getByText('Python object copied')
  // expect(findText).toBeInTheDocument()
})
test('renders preview section', () => {
  render(<App preview />)
})
