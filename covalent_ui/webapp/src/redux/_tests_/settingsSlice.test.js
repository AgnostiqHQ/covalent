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

import {
  settingsResults,
  updateSettings,
  settingsSlice,
} from '../settingsSlice'

describe('settings slice', () => {
  it('settingsResults is pending', () => {
    const action = settingsResults.pending(
      // <-- THIS
      {
        settingsResultsList: { isFetching: true, error: null },
      }
    )
    const initialState = {
      settingsResultsList: { isFetching: false, error: null },
    }

    expect(settingsSlice.reducer(initialState, action)).toEqual({
      settingsResultsList: { isFetching: true, error: null },
    })
  })

  it('settingsResults is fulfilled', () => {
    const action = {
      type: settingsResults.fulfilled,
    }
    const initialState = settingsSlice.reducer(
      {
        settingsResultsList: { isFetching: true, error: null },
      },
      action
    )
    expect(initialState).toEqual({
      settingsResultsList: { isFetching: false, error: null },
    })
  })

  it('settingsResults is rejected', () => {
    const action = {
      type: settingsResults.rejected,
      payload: 'value',
    }
    const initialState = settingsSlice.reducer(
      {
        settingsResultsList: { isFetching: false, error: null },
      },
      action
    )
    expect(initialState).toEqual({
      settingsResultsList: { isFetching: false, error: 'value' },
    })
  })

  it('updateSettings is pending', () => {
    const action = updateSettings.pending(
      // <-- THIS
      {
        updateSuccessList: { isFetching: true, error: null },
      }
    )
    const initialState = {
      updateSuccessList: { isFetching: false, error: null },
    }

    expect(settingsSlice.reducer(initialState, action)).toEqual({
      updateSuccessList: { isFetching: true, error: null },
    })
  })

  it('updateSettings is fulfilled', () => {
    const action = {
      type: updateSettings.fulfilled,
    }
    const initialState = settingsSlice.reducer(
      {
        updateSuccessList: { isFetching: true, error: null },
      },
      action
    )
    expect(initialState).toEqual({
      updateSuccessList: { isFetching: false, error: null },
    })
  })

  it('updateSettings is rejected', () => {
    const action = {
      type: updateSettings.rejected,
      payload: 'value',
    }
    const initialState = settingsSlice.reducer(
      {
        updateSuccessList: { isFetching: false, error: null },
      },
      action
    )
    expect(initialState).toEqual({
      updateSuccessList: { isFetching: false, error: 'value' },
    })
  })
})
