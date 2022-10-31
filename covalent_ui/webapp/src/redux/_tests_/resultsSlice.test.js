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
  fetchResult,
  fetchResults,
  deleteResults,
  resultsSlice,
} from '../resultsSlice'

describe('results slice', () => {
  it('fetch result is pending', () => {
    const action = fetchResult.pending(
      // <-- THIS
      {
        fetchResult: { isFetching: true, error: null },
      }
    )
    const initialState = {
      cache: {},
      fetchResult: { isFetching: false, error: null },
    }

    expect(resultsSlice.reducer(initialState, action)).toEqual({
      cache: {},
      fetchResult: { isFetching: true, error: null },
    })
  })

  it('fetch result is fulfilled', () => {
    const action = {
      type: fetchResult.pending,
      payload: { dispatch: '32323232' },
    }
    const initialState = resultsSlice.reducer(
      {
        fetchResult: { isFetching: false, error: null },
      },
      action
    )
    expect(initialState).toEqual({
      fetchResult: { isFetching: true, error: null },
    })
  })

  it('fetch result is rejected', () => {
    const action = { type: fetchResult.rejected, payload: { message: 'value' } }
    const initialState = resultsSlice.reducer(
      {
        fetchResult: { isFetching: false, error: null },
      },
      action
    )
    expect(initialState).toEqual({
      fetchResult: { isFetching: false, error: 'value' },
    })
  })

  it('fetchResults is pending', () => {
    const action = fetchResults.pending(
      // <-- THIS
      {
        fetchResults: { isFetching: true, error: null },
      }
    )
    const initialState = {
      cache: {},
      fetchResults: { isFetching: false, error: null },
    }

    expect(resultsSlice.reducer(initialState, action)).toEqual({
      cache: {},
      fetchResults: { isFetching: true, error: null },
    })
  })

  it('fetchResults is fulfilled', () => {
    const action = { type: fetchResults.fulfilled }
    const initialState = resultsSlice.reducer(
      {
        fetchResults: { isFetching: false, error: null },
      },
      action
    )
    expect(initialState).toEqual({
      cache: {},
      fetchResults: { isFetching: false, error: null },
    })
  })

  it('fetchResults  is rejected', () => {
    const action = {
      type: fetchResults.rejected,
      payload: { message: 'value' },
    }
    const initialState = resultsSlice.reducer(
      {
        fetchResults: { isFetching: false, error: null },
      },
      action
    )
    expect(initialState).toEqual({
      fetchResults: { isFetching: false, error: 'value' },
    })
  })

  it('deleteResults is pending', () => {
    const action = deleteResults.pending(
      // <-- THIS
      {
        deleteResults: { isFetching: true, error: null },
      }
    )
    const initialState = {
      cache: {},
      deleteResults: { isFetching: false, error: null },
    }

    expect(resultsSlice.reducer(initialState, action)).toEqual({
      cache: {},
      deleteResults: { isFetching: true, error: null },
    })
  })

  it('deleteResults is fulfilled', () => {
    const action = { type: deleteResults.fulfilled }
    const initialState = resultsSlice.reducer(
      {
        deleteResults: { isFetching: false, error: null },
      },
      action
    )
    expect(initialState).toEqual({
      deleteResults: { isFetching: false, error: null },
    })
  })

  it('deleteResults  is rejected', () => {
    const action = {
      type: deleteResults.rejected,
      payload: { message: 'value' },
    }
    const initialState = resultsSlice.reducer(
      {
        deleteResults: { isFetching: false, error: null },
      },
      action
    )
    expect(initialState).toEqual({
      deleteResults: { isFetching: false, error: 'value' },
    })
  })
})
