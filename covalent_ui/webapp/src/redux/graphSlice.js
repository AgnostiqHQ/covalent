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
  graphList: {},
  graphResultsList: { isFetching: false, error: null },
}

export const graphResults = createAsyncThunk(
  'results/graphResults',
  ({ dispatchId }, thunkAPI) =>
    api.get(`dispatches/${dispatchId}/graph`).catch(thunkAPI.rejectWithValue)
)

export const graphSlice = createSlice({
  name: 'results',
  initialState,
  reducers: {
    resetGraphState() {
      return initialState
    },
  },
  extraReducers: (builder) => {
    builder
      // graph Results
      .addCase(graphResults.fulfilled, (state, { payload }) => {
        state.graphResultsList.isFetching = false
        // update results cache
        state.graphList = payload.graph
      })
      .addCase(graphResults.pending, (state) => {
        state.graphResultsList.isFetching = true
        state.graphResultsList.error = null
      })
      .addCase(graphResults.rejected, (state, { payload }) => {
        state.graphResultsList.isFetching = false
        state.graphResultsList.error = payload
      })
  },
})

export const { resetGraphState } = graphSlice.actions
