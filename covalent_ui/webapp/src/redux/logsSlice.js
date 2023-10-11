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
  logList: [],
  logFile: '',
  fetchLogList: { isFetching: false, error: null },
  logFileList: { isFetching: false, error: null },
  totalLogs: 0,
}

export const fetchLogsList = createAsyncThunk(
  'logs/fetchList',
  async (bodyParams, thunkAPI) =>
    await api
      .get(
        `api/v1/logs/?&count=${bodyParams.count}&offset=${bodyParams.offset}&search=${bodyParams.search}&sort_by=${bodyParams.sort_by}&sort_direction=${bodyParams.direction}`
      )
      .catch(thunkAPI.rejectWithValue)
)

export const downloadCovalentLogFile = createAsyncThunk(
  'logs/download',
  async (bodyParams, thunkAPI) =>
    await api
      .get(
        `api/v1/logs/download`
      )
      .catch(thunkAPI.rejectWithValue)
)

export const logsSlice = createSlice({
  name: 'logs',
  initialState,
  reducers: {
    resetLogs(state) {
      state.logFile = ''
    },
  },
  extraReducers: (builder) => {
    builder
      // dashboardList
      .addCase(fetchLogsList.fulfilled, (state, { payload }) => {
        // update dashboardList
        state.fetchLogList.isFetching = false
        state.totalLogs = payload.total_count
        state.logList = payload.items
      })
      .addCase(fetchLogsList.pending, (state, { payload }) => {
        state.fetchLogList.isFetching = true
        state.fetchLogList.error = null
      })
      .addCase(fetchLogsList.rejected, (state, { payload }) => {
        state.fetchLogList.isFetching = false
        state.fetchLogList.error = payload
      })
      .addCase(downloadCovalentLogFile.fulfilled, (state, { payload }) => {
        // log file download
        state.logFileList.isFetching = false
        state.logFile = payload
      })
      .addCase(downloadCovalentLogFile.pending, (state, { payload }) => {
        state.logFileList.isFetching = true
        state.logFileList.error = null
      })
      .addCase(downloadCovalentLogFile.rejected, (state, { payload }) => {
        state.logFileList.isFetching = false
        state.logFileList.error = payload
      })
  },
})

export const { resetLogs } = logsSlice.actions
