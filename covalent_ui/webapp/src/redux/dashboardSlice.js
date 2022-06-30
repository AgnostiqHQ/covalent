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
  dashboardList: [],
  dashboardOverview: {},
  fetchDashboardList: { isFetching: false, error: null },
  fetchDashboardOverview: { isFetching: false, error: null },
  deleteResults: { isFetching: false, error: null },
}

export const fetchDashboardList = createAsyncThunk(
  'summary/dispatches',
  ({ dispatchId }, thunkAPI) =>
    api.get(`/api/results/${dispatchId}`).catch(thunkAPI.rejectWithValue)
)

export const fetchDashboardOverview = createAsyncThunk(
  'summary/overview',
  (values, thunkAPI) =>
    api.get(`/api/v1/summary/overview/`).catch(thunkAPI.rejectWithValue)
)

export const deleteDispatch = createAsyncThunk(
  'summary/dispatches/delete',
  ({ dispatchId }, thunkAPI) =>
    api.get(`/api/results/${dispatchId}`).catch(thunkAPI.rejectWithValue)
)

export const dashboardSlice = createSlice({
  name: 'dashboard',
  initialState,
  extraReducers: (builder) => {
    builder
      // dashboardList
      .addCase(fetchDashboardList.fulfilled, (state, { payload }) => {
        // update dashboardList
        state.fetchDashboardList.isFetching = false
        state.dashboardList = _.keyBy(payload, 'dispatch_id')
      })
      .addCase(fetchDashboardList.pending, (state, { payload }) => {
        state.fetchDashboardList.isFetching = true
        state.fetchDashboardList.error = null
      })
      .addCase(fetchDashboardList.rejected, (state, { payload }) => {
        state.fetchDashboardList.isFetching = false
        state.fetchDashboardList.error = payload.message
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
        state.fetchDashboardOverview.error = payload.message
      })

      // deleteResults
      .addCase(deleteDispatch.fulfilled, (state, { meta }) => {
        state.deleteResults.isFetching = false
        // update results cache
        const dispatchIds = _.get(meta, 'arg.dispatchIds')
        _.each(dispatchIds, (key) => delete state.dashboardList[key])
      })
      .addCase(deleteDispatch.pending, (state, { payload }) => {
        state.deleteResults.isFetching = true
        state.deleteResults.error = null
      })
      .addCase(deleteDispatch.rejected, (state, { payload }) => {
        state.deleteResults.isFetching = false
        state.deleteResults.error = payload.message
      })
  },
})
