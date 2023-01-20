/**
 * Copyright 2021 Agnostiq Inc.
 *
 * This file is part of Covalent.
 *
 * Licensed under the GNU Affero General Public License 3.0 (the "License").
 * A copy of the License may be obtained with this software package or at
 *
 *      https://www.gnu.org/licenses/agpl-3.0.en.html
 *
 * Use of this file is prohibited except in compliance with the License. Any
 * modifications or derivative works of this file must retain this copyright
 * notice, and modified files must contain a notice indicating that they have
 * been altered from the originals.
 *
 * Covalent is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE. See the License for more details.
 *
 * Relief from the License may be granted by purchasing a commercial license.
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
