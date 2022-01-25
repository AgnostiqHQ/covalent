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

import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'

import api from '../utils/api'

const initialState = {
  // results cache mapped by dispatch id
  cache: {
    // [dispatchId]: {<result object>}
  },

  // request status
  fetchResult: { isFetching: false, error: null },
}

export const fetchResult = createAsyncThunk(
  'results/fetchResult',
  ({ resultsDir, dispatchId }, thunkAPI) => {
    return api
      .get(`/api/results/${dispatchId}`, { params: { resultsDir } })
      .catch(thunkAPI.rejectWithValue)
  }
)

export const resultsSlice = createSlice({
  name: 'results',
  initialState,
  reducers: {
    removeResult(state, { payload: dispatchIds }) {
      for (const dispatchId of dispatchIds) {
        delete state.cache[dispatchId]
      }
    },
  },
  extraReducers: (builder) => {
    builder
      // fetchResult
      .addCase(fetchResult.fulfilled, (state, { payload }) => {
        state.fetchResult.isFetching = false
        // update results cache
        state.cache[payload.dispatch_id] = payload
      })
      .addCase(fetchResult.pending, (state, { payload }) => {
        state.fetchResult.isFetching = true
        state.fetchResult.error = null
      })
      .addCase(fetchResult.rejected, (state, { payload }) => {
        state.fetchResult.isFetching = false
        state.fetchResult.error = payload.message
      })
  },
})

export const { removeResult } = resultsSlice.actions
