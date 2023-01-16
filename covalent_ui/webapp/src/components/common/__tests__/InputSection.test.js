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
