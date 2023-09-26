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
  settingsList: {},
  updateSuccess: {},
  settingsResultsList: { isFetching: false, error: null },
  updateSuccessList: { isFetching: false, error: null }
}

export const settingsResults = createAsyncThunk(
  'settingsResult/settingsResults',
  (values, thunkAPI) =>
    api.get('api/v1/settings').catch(thunkAPI.rejectWithValue)
)

export const updateSettings = createAsyncThunk(
  'settingsResult/updateSettings',
  async (bodyParams, thunkAPI) =>
    await api
      .post('api/v1/settings?override_existing=true',
        bodyParams).catch(thunkAPI.rejectWithValue)
)

export const settingsSlice = createSlice({
  name: 'settingsResult',
  initialState,
  extraReducers: (builder) => {
    builder
      // settingslist
      .addCase(settingsResults.fulfilled, (state, { payload }) => {
        state.settingsResultsList.isFetching = false
        state.settingsList = payload
      })
      .addCase(settingsResults.pending, (state, { payload }) => {
        state.settingsResultsList.isFetching = true
        state.settingsResultsList.error = null
      })
      .addCase(settingsResults.rejected, (state, { payload }) => {
        state.settingsResultsList.isFetching = false
        state.settingsResultsList.error = payload
      })

      // updateSettings
      .addCase(updateSettings.fulfilled, (state, { payload }) => {
        state.updateSuccessList.isFetching = false
        state.updateSuccess = payload
      })
      .addCase(updateSettings.pending, (state, { payload }) => {
        state.updateSuccessList.isFetching = true
        state.updateSuccessList.error = null
      })
      .addCase(updateSettings.rejected, (state, { payload }) => {
        state.updateSuccessList.isFetching = false
        state.updateSuccessList.error = payload
      })
  },
})

export const { settingsDipatach } = settingsSlice.actions
