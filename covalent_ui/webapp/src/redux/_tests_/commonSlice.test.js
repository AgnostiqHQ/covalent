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

import { commonSlice } from '../commonSlice'

describe('common slice  tests', () => {
  it('common slice toggleLatticeDrawer rendered', () => {
    const action = { type: commonSlice.actions.toggleLatticeDrawer }
    const initialState = commonSlice.reducer(
      {
        latticeDrawerOpen: false,
        callSocketApi: false,
      },
      action
    )
    expect(initialState).toEqual({
      latticeDrawerOpen: true,
      callSocketApi: false,
    })
  })

  it('common slice socketAPI rendered', () => {
    const action = { type: commonSlice.actions.socketAPI }
    const initialState = commonSlice.reducer(
      {
        latticeDrawerOpen: false,
        callSocketApi: false,
      },
      action
    )
    expect(initialState).toEqual({
      latticeDrawerOpen: false,
      callSocketApi: true,
    })
  })
})
