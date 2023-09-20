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

import { render, screen } from '@testing-library/react'
import App from '../ErrorCard'

const errorCardCases = ['errorCard', 'electronIcon']

describe('error card', () => {
  test.each(errorCardCases)('render %p', (firstArg) => {
    render(<App error="this is a error" showElectron />)
    const element = screen.getByTestId(firstArg)
    expect(element).toBeInTheDocument()
  })

  test('renders error message', () => {
    render(<App error="this is a error" showElectron />)
    const linkElement = screen.getByText('this is a error')
    expect(linkElement).toBeInTheDocument()
  })

  test('if error null', () => {
    render(<App />)
  })
})
