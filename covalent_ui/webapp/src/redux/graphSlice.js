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

import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'

import api from '../utils/api'

const initialState = {
  graphList: {},
  graphResultsList: { isFetching: false, error: null },
}

export const graphResults = createAsyncThunk(
  'results/graphResults',
  ({ dispatchId }, thunkAPI) =>
    api.get(`api/v1/dispatches/${dispatchId}/graph`).catch(thunkAPI.rejectWithValue)
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
