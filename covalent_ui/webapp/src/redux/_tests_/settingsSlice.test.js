// /**
//  * Copyright 2021 Agnostiq Inc.
//  *
//  * This file is part of Covalent.
//  *
//  * Licensed under the GNU Affero General Public License 3.0 (the "License").
//  * A copy of the License may be obtained with this software package or at
//  *
//  *      https://www.gnu.org/licenses/agpl-3.0.en.html
//  *
//  * Use of this file is prohibited except in compliance with the License. Any
//  * modifications or derivative works of this file must retain this copyright
//  * notice, and modified files must contain a notice indicating that they have
//  * been altered from the originals.
//  *
//  * Covalent is distributed in the hope that it will be useful, but WITHOUT
//  * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
//  * FITNESS FOR A PARTICULAR PURPOSE. See the License for more details.
//  *
//  * Relief from the License may be granted by purchasing a commercial license.
//  */

import {
  settingsResults,
  updateSettings,
  settingsSlice,
} from '../settingsSlice'

describe('results slice', () => {
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
