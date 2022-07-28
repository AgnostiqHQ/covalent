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
        `api/v1/dispatches/list?count=${bodyParams.count}&offset=${bodyParams.offset}&search=${bodyParams.search}&sort_by=${bodyParams.sort_by}&sort_direction=${bodyParams.direction}`
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
  },
})

export const { dispatchesDeleted } = dashboardSlice.actions
