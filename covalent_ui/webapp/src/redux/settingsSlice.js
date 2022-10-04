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
