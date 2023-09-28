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
  electronList: {},
  electronResult: {},
  electronFunctionString: {},
  electronInput: {},
  electronError: {},
  electronExecutor: {},
  qelectronJobs: [],
  qelectronJobOverview: {},
  electronDetailsList: { isFetching: false, error: null },
  electronResultList: { isFetching: false, error: null },
  electronFunctionStringList: { isFetching: false, error: null },
  electronInputList: { isFetching: false, error: null },
  electronErrorList: { isFetching: false, error: null },
  electronExecutorList: { isFetching: false, error: null },
  qelectronJobsList: { isFetching: false, error: null },
  qelectronJobOverviewList: { isFetching: false, error: null },
}

export const electronDetails = createAsyncThunk(
  'electronResults/electronDetails',
  ({ electronId, dispatchId }, thunkAPI) =>
    api.get(`api/v1/dispatches/${dispatchId}/electron/${electronId}`).catch(thunkAPI.rejectWithValue)
)

export const electronResult = createAsyncThunk(
  'electronResults/electronResult',
  ({ dispatchId, electronId, params }, thunkAPI) =>
    api.get(`api/v1/dispatches/${dispatchId}/electron/${electronId}/details/${params}`).catch(thunkAPI.rejectWithValue)
)

export const electronFunctionString = createAsyncThunk(
  'electronResults/electronFunctionString',
  ({ dispatchId, electronId, params }, thunkAPI) =>
    api.get(`api/v1/dispatches/${dispatchId}/electron/${electronId}/details/${params}`).catch(thunkAPI.rejectWithValue)
)

export const electronInput = createAsyncThunk(
  'electronResults/electronInput',
  ({ dispatchId, electronId, params }, thunkAPI) =>
    api.get(`api/v1/dispatches/${dispatchId}/electron/${electronId}/details/${params}`).catch(thunkAPI.rejectWithValue)
)

export const electronError = createAsyncThunk(
  'electronResults/electronError',
  ({ dispatchId, electronId, params }, thunkAPI) =>
    api.get(`api/v1/dispatches/${dispatchId}/electron/${electronId}/details/${params}`).catch(thunkAPI.rejectWithValue)
)

export const electronExecutor = createAsyncThunk(
  'electronResults/electronExecutor',
  ({ dispatchId, electronId, params }, thunkAPI) =>
    api.get(`api/v1/dispatches/${dispatchId}/electron/${electronId}/details/${params}`).catch(thunkAPI.rejectWithValue)
)

export const qelectronJobs = createAsyncThunk(
  'electronResults/qelectronJobs',
  ({ dispatchId, electronId, bodyParams }, thunkAPI) =>
    api.get(`api/v1/dispatches/${dispatchId}/electron/${electronId}/jobs?&sort_by=${bodyParams.sort_by}&sort_direction=${bodyParams.direction}&offset=${bodyParams.offset}`).catch(thunkAPI.rejectWithValue)
)

export const qelectronJobOverview = createAsyncThunk(
  'electronResults/qelectronJobOverview',
  ({ dispatchId, electronId, jobId }, thunkAPI) =>
    api.get(`api/v1/dispatches/${dispatchId}/electron/${electronId}/jobs/${jobId}`).catch(thunkAPI.rejectWithValue)
)

export const electronSlice = createSlice({
  name: 'electronResults',
  initialState,
  reducers: {
    resetElectronState() {
      return initialState
    }
  },
  extraReducers: (builder) => {
    builder
      // electron Details
      .addCase(electronDetails.fulfilled, (state, { payload }) => {
        state.electronDetailsList.isFetching = false
        state.electronList = payload
      })
      .addCase(electronDetails.pending, (state) => {
        state.electronDetailsList.isFetching = true
        state.electronDetailsList.error = null
      })
      .addCase(electronDetails.rejected, (state, { payload }) => {
        state.electronDetailsList.isFetching = false
        state.electronDetailsList.error = payload
      })

      // electron Results
      .addCase(electronResult.fulfilled, (state, { payload }) => {
        state.electronResultList.isFetching = false
        state.electronResult = payload
      })
      .addCase(electronResult.pending, (state) => {
        state.electronResultList.isFetching = true
        state.electronResultList.error = null
      })
      .addCase(electronResult.rejected, (state, { payload }) => {
        state.electronResultList.isFetching = false
        state.electronResultList.error = payload
      })

      // electron function to string
      .addCase(electronFunctionString.fulfilled, (state, { payload }) => {
        state.electronFunctionStringList.isFetching = false
        state.electronFunctionString = payload
      })
      .addCase(electronFunctionString.pending, (state) => {
        state.electronFunctionStringList.isFetching = true
        state.electronFunctionStringList.error = null
      })
      .addCase(electronFunctionString.rejected, (state, { payload }) => {
        state.electronFunctionStringList.isFetching = false
        state.electronFunctionStringList.error = payload
      })

      // electron Input
      .addCase(electronInput.fulfilled, (state, { payload }) => {
        state.electronInputList.isFetching = false
        state.electronInput = payload
      })
      .addCase(electronInput.pending, (state) => {
        state.electronInputList.isFetching = true
        state.electronInputList.error = null
      })
      .addCase(electronInput.rejected, (state, { payload }) => {
        state.electronInputList.isFetching = false
        state.electronInputList.error = payload
      })

      // electron Error
      .addCase(electronError.fulfilled, (state, { payload }) => {
        state.electronErrorList.isFetching = false
        state.electronError = payload
      })
      .addCase(electronError.pending, (state) => {
        state.electronErrorList.isFetching = true
        state.electronErrorList.error = null
      })
      .addCase(electronError.rejected, (state, { payload }) => {
        state.electronErrorList.isFetching = false
        state.electronErrorList.error = payload
      })

      // electron Error
      .addCase(electronExecutor.fulfilled, (state, { payload }) => {
        state.electronExecutorList.isFetching = false
        state.electronExecutor = payload
      })
      .addCase(electronExecutor.pending, (state) => {
        state.electronExecutorList.isFetching = true
        state.electronExecutorList.error = null
      })
      .addCase(electronExecutor.rejected, (state, { payload }) => {
        state.electronExecutorList.isFetching = false
        state.electronExecutorList.error = payload
      })

      // qelectron Jobs
      .addCase(qelectronJobs.fulfilled, (state, { payload }) => {
        state.qelectronJobsList.isFetching = false
        state.qelectronJobs = payload
      })
      .addCase(qelectronJobs.pending, (state) => {
        state.qelectronJobsList.isFetching = true
        state.qelectronJobsList.error = null
      })
      .addCase(qelectronJobs.rejected, (state, { payload }) => {
        state.qelectronJobsList.isFetching = false
        state.qelectronJobsList.error = payload
      })

      // qelectron Job Overview
      .addCase(qelectronJobOverview.fulfilled, (state, { payload }) => {
        state.qelectronJobOverviewList.isFetching = false
        state.qelectronJobOverview = payload
      })
      .addCase(qelectronJobOverview.pending, (state) => {
        state.qelectronJobOverviewList.isFetching = true
        state.qelectronJobOverviewList.error = null
      })
      .addCase(qelectronJobOverview.rejected, (state, { payload }) => {
        state.qelectronJobOverviewList.isFetching = false
        state.qelectronJobOverviewList.error = payload
      })
  },
})

export const { resetElectronState } = electronSlice.actions
