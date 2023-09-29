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

import _ from 'lodash'
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'

import api from '../utils/api'

const initialState = {
  // results cache mapped by dispatch id
  cache: {
    // [dispatchId]: {<result object>}
  },

  // request status
  resultsSlice: { isFetching: false, error: null },
  fetchResults: { isFetching: false, error: null },
  deleteResults: { isFetching: false, error: null },
}

export const fetchResult = createAsyncThunk(
  'results/fetchResult',
  ({ dispatchId }, thunkAPI) =>
    api.get(`/api/results/${dispatchId}`).catch(thunkAPI.rejectWithValue)
)

export const fetchResults = createAsyncThunk(
  'results/fetchResults',
  (thunkAPI) => api.get('/api/results').catch(thunkAPI.rejectWithValue)
)

export const deleteResults = createAsyncThunk(
  'results/deleteResults',
  ({ dispatchIds }, thunkAPI) =>
    api
      .delete('/api/results', { data: { dispatchIds } })
      .catch(thunkAPI.rejectWithValue)
)

export const resultsSlice = createSlice({
  name: 'results',
  initialState,
  extraReducers: (builder) => {
    builder
      // fetchResult
      .addCase(fetchResult.fulfilled, (state, { payload }) => {
        state.fetchResult.isFetching = false
        // update results cache
        state.cache[payload.dispatch_id] = payload
      })
      .addCase(fetchResult.pending, (state) => {
        state.fetchResult.isFetching = true
        state.fetchResult.error = null
      })
      .addCase(fetchResult.rejected, (state, { payload }) => {
        state.fetchResult.isFetching = false
        state.fetchResult.error = payload.message
      })

      // fetchResults
      .addCase(fetchResults.fulfilled, (state, { payload }) => {
        state.fetchResults.isFetching = false
         // update results cache
        state.cache = _.keyBy(payload, 'dispatch_id')
      })
      .addCase(fetchResults.pending, (state) => {
        state.fetchResults.isFetching = true
        state.fetchResults.error = null
      })
      .addCase(fetchResults.rejected, (state, { payload }) => {
        state.fetchResults.isFetching = false
        state.fetchResults.error = payload.message
      })

      // deleteResults
      .addCase(deleteResults.fulfilled, (state, { meta }) => {
        state.deleteResults.isFetching = false
        // update results cache
        const dispatchIds = _.get(meta, 'arg.dispatchIds')
        _.each(dispatchIds, (key) => delete state.cache[key])
      })
      .addCase(deleteResults.pending, (state) => {
        state.deleteResults.isFetching = true
        state.deleteResults.error = null
      })
      .addCase(deleteResults.rejected, (state, { payload }) => {
        state.deleteResults.isFetching = false
        state.deleteResults.error = payload.message
      })
  },
})
