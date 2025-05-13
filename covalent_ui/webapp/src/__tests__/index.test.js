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

import configureMockStore from 'redux-mock-store'
import thunk from 'redux-thunk'


describe('testing index', () => {
  test('mock store', () => {
    const mockStore = configureMockStore([thunk])
    expect(mockStore).toBeDefined()
  })
  test('rendering react dom', () => {
    const mockRender = jest.fn()
    const mockCreateRoot = jest.fn(() => ({ render: mockRender }))
    jest.mock('react-dom/client', () => ({ createRoot: mockCreateRoot }))

    const div = document.createElement('div')
    div.id = 'root'
    document.body.appendChild(div)
    require('../index')
    expect(mockCreateRoot).toHaveBeenCalled()
  })
})
