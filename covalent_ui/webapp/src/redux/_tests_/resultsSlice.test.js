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
      type: fetchResult.fulfilled,
      payload: {
        dispatch_id: 'dsdsdsdsds23232',
      },
    }
    const initialState = resultsSlice.reducer(
      {
        cache: {},
        fetchResult: { isFetching: false, error: null },
      },
      action
    )
    expect(initialState).toEqual({
      cache: {
        dsdsdsdsds23232: {
          dispatch_id: 'dsdsdsdsds23232',
        },
      },
      fetchResult: { isFetching: false, error: null },
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
