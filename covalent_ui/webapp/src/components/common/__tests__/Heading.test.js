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
import App from '../Heading'

test('renders heading', () => {
  render(<App> Executor: Ram</App>)
  const linkElement = screen.getByTestId('heading')
  expect(linkElement).toBeInTheDocument()
})
test('renders heading title', () => {
  render(<App> Executor: Ram</App>)
  const linkElement = screen.getByText('Executor: Ram')
  expect(linkElement).toBeInTheDocument()
})
