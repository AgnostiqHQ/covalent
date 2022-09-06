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

import { createSlice, createAsyncThunk, current } from '@reduxjs/toolkit'
import _ from 'lodash'
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
    dispatchesDeleted(state, { payload: dispatchIds }) {
      const filteredData = current(state.dashboardList);
      const finalArray = filteredData.filter(object1 => {
        return !dispatchIds.some(object2 => {
          return object1.dispatch_id === object2;
        });
      });
      state.dashboardList = finalArray
      state.totalDispatches = finalArray.length
      const lastStatusArray = _.orderBy(finalArray, ['started_at'], ['desc']);
      const lastStatus = lastStatusArray.length ? lastStatusArray[0].status : 'N/A'
      const dashOverview = {
        "total_jobs": finalArray.length,
        "total_jobs_running": finalArray.filter(e => e.status === 'RUNNING').length,
        "total_jobs_completed": finalArray.filter(e => e.status === 'COMPLETED').length,
        "total_jobs_failed": finalArray.filter(e => e.status === 'FAILED').length,
        "latest_running_task_status": finalArray.length ? lastStatus : "N/A",
        "total_dispatcher_duration": finalArray.length ? finalArray?.map(obj => obj.runtime).reduce((partialSum, a) => partialSum + a, 0) : 'N/A'
      }
      state.dashboardOverview = dashOverview
    },
    allDispatchesDelete(state, { payload }) {
      const statusFilter = payload.status_filter;
      let filteredData = [];
      if (statusFilter === 'ALL') {
        filteredData = [];
      } else filteredData = current(state.dashboardList);
      const finalArray = filteredData?.filter(e => e.status !== payload.status_filter)
      state.dashboardList = finalArray
      state.totalDispatches = finalArray.length
      const lastStatusArray = _.orderBy(finalArray, ['started_at'], ['desc']);
      const lastStatus = lastStatusArray.length ? lastStatusArray[0].status : 'N/A'
      const dashOverview = {
        "total_jobs": finalArray.length,
        "total_jobs_running": finalArray.filter(e => e.status === 'RUNNING').length,
        "total_jobs_completed": finalArray.filter(e => e.status === 'COMPLETED').length,
        "total_jobs_failed": finalArray.filter(e => e.status === 'FAILED').length,
        "latest_running_task_status": finalArray.length ? lastStatus : "N/A",
        "total_dispatcher_duration": finalArray.length ? finalArray?.map(obj => obj.runtime).reduce((partialSum, a) => partialSum + a, 0) : 'N/A'
      }
      state.dashboardOverview = dashOverview
    },
    filterDispatches(state, { payload }) {
      const statusFilter = payload
      let filteredData = [];
      let finalArray=[];
      if (statusFilter === 'ALL') {
        filteredData = current(state.dashboardList)
        finalArray=filteredData
      } else {
        filteredData = current(state.dashboardList)
        finalArray = filteredData?.filter(e => e.status === payload.status_filter)
      }      
      state.dashboardList = finalArray
      state.totalDispatches = finalArray.length
      const lastStatusArray = _.orderBy(finalArray, ['started_at'], ['desc']);
      const lastStatus = lastStatusArray.length ? lastStatusArray[0].status : 'N/A'
      const dashOverview = {
        "total_jobs": finalArray.length,
        "total_jobs_running": finalArray.filter(e => e.status === 'RUNNING').length,
        "total_jobs_completed": finalArray.filter(e => e.status === 'COMPLETED').length,
        "total_jobs_failed": finalArray.filter(e => e.status === 'FAILED').length,
        "latest_running_task_status": finalArray.length ? lastStatus : "N/A",
        "total_dispatcher_duration": finalArray.length ? finalArray?.map(obj => obj.runtime).reduce((partialSum, a) => partialSum + a, 0) : 'N/A'
      }
      state.dashboardOverview = dashOverview
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

export const { dispatchesDeleted, allDispatchesDelete,filterDispatches } = dashboardSlice.actions
