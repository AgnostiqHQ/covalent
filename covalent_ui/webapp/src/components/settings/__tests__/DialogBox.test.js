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
})
