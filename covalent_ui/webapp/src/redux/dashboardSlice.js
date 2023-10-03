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
  // results cache mapped by dispatch id
  dashboardList: [],
  totalDispatches: 0,
  runningDispatches: 0,
  completedDispatches: 0,
  failedDispatches: 0,
  dashboardOverview: {},
  fetchDashboardList: { isFetching: false, error: null },
  fetchDashboardOverview: { isFetching: false, error: null },
  deleteResults: { isFetching: false, error: null },
  dispatchesDeleted: false,
}

export const fetchDashboardList = createAsyncThunk(
  'dashboard/fetchList',
  async (bodyParams, thunkAPI) =>
    await api
      .get(
        `api/v1/dispatches/list?count=${bodyParams.count}&offset=${bodyParams.offset}&search=${bodyParams.search}&sort_by=${bodyParams.sort_by}&sort_direction=${bodyParams.direction}&status_filter=${bodyParams.status_filter}`
      )
      .catch(thunkAPI.rejectWithValue)
)

export const fetchDashboardOverview = createAsyncThunk(
  'dashboard/overview',
  (values, thunkAPI) =>
    api.get('api/v1/dispatches/overview').catch(thunkAPI.rejectWithValue)
)

export const deleteDispatches = createAsyncThunk(
  'dashboard/deleteDispatches',
  async (bodyParams, thunkAPI) =>
    await api
      .post('api/v1/dispatches/delete', bodyParams)
      .catch(thunkAPI.rejectWithValue)
)

export const deleteAllDispatches = createAsyncThunk(
  'dashboard/deleteAllDispatches',
  async (bodyParams, thunkAPI) =>
    await api
      .post('api/v1/dispatches/delete-all', bodyParams)
      .catch(thunkAPI.rejectWithValue)
)

export const dashboardSlice = createSlice({
  name: 'dashboard',
  initialState,
  reducers: {
    dispatchesDeleted(state) {
      state.dispatchesDeleted = !state.dispatchesDeleted
    },
  },
  extraReducers: (builder) => {
    builder
      // dashboardList
      .addCase(fetchDashboardList.fulfilled, (state, { payload }) => {
        // update dashboardList
        state.fetchDashboardList.isFetching = false
        state.totalDispatches = payload.total_count
        state.dashboardList = payload.items
      })
      .addCase(fetchDashboardList.pending, (state, { payload }) => {
        state.fetchDashboardList.isFetching = true
        state.fetchDashboardList.error = null
      })
      .addCase(fetchDashboardList.rejected, (state, { payload }) => {
        state.fetchDashboardList.isFetching = false
        state.fetchDashboardList.error = payload
      })

      // dashboardOverview
      .addCase(fetchDashboardOverview.fulfilled, (state, { payload }) => {
        state.fetchDashboardOverview.isFetching = false
        // update dashboardOverview
        state.dashboardOverview = payload
      })
      .addCase(fetchDashboardOverview.pending, (state, { payload }) => {
        state.fetchDashboardOverview.isFetching = true
        state.fetchDashboardOverview.error = null
      })
      .addCase(fetchDashboardOverview.rejected, (state, { payload }) => {
        state.fetchDashboardOverview.isFetching = false
        state.fetchDashboardOverview.error = payload
      })

      // deleteResults
      .addCase(deleteDispatches.fulfilled, (state, { meta }) => {
        state.deleteResults.isFetching = false
        state.deleteResults.isDeleted = true
      })
      .addCase(deleteDispatches.pending, (state, { payload }) => {
        state.deleteResults.isFetching = true
        state.deleteResults.isDeleted = false
        state.deleteResults.error = null
      })
      .addCase(deleteDispatches.rejected, (state, { payload }) => {
        state.deleteResults.isFetching = false
        state.deleteResults.isDeleted = false
        state.deleteResults.error = payload
      })

      //deleteAllResults
      .addCase(deleteAllDispatches.fulfilled, (state, { meta }) => {
        state.deleteResults.isFetching = false
        state.deleteResults.isDeleted = true
      })
      .addCase(deleteAllDispatches.pending, (state, { payload }) => {
        state.deleteResults.isFetching = true
        state.deleteResults.isDeleted = false
        state.deleteResults.error = null
      })
      .addCase(deleteAllDispatches.rejected, (state, { payload }) => {
        state.deleteResults.isFetching = false
        state.deleteResults.isDeleted = false
        state.deleteResults.error = payload
      })
  },
})

export const { dispatchesDeleted } = dashboardSlice.actions
