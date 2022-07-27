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
  electronList:{},
  electronResult:{},
  electronFunctionString:{},
  electronInput:{},
  electronError:{},
  electronExecutor:{},
  electronDetailsList: { isFetching: false, error: null },
  electronResultList: { isFetching: false, error: null },
  electronFunctionStringList: { isFetching: false, error: null },
  electronInputList: { isFetching: false, error: null },
  electronErrorList: { isFetching: false, error: null },
  electronExecutorList: { isFetching: false, error: null },
}

export const electronDetails = createAsyncThunk(
  'electronResults/electronDetails',
  ({electronId,dispatchId}, thunkAPI) =>
  api.get(`dispatches/${dispatchId}/electron/${electronId}`).catch(thunkAPI.rejectWithValue)
)

export const electronResult = createAsyncThunk(
    'electronResults/electronResult',
    ({dispatchId,electronId,params}, thunkAPI) =>
    api.get(`dispatches/${dispatchId}/electron/${electronId}/details/${params}`).catch(thunkAPI.rejectWithValue)
)

export const electronFunctionString = createAsyncThunk(
    'electronResults/electronFunctionString',
    ({dispatchId,electronId,params}, thunkAPI) =>
    api.get(`dispatches/${dispatchId}/electron/${electronId}/details/${params}`).catch(thunkAPI.rejectWithValue)
)

export const electronInput = createAsyncThunk(
    'electronResults/electronInput',
    ({dispatchId,electronId,params}, thunkAPI) =>
    api.get(`dispatches/${dispatchId}/electron/${electronId}/details/${params}`).catch(thunkAPI.rejectWithValue)
)

export const electronError = createAsyncThunk(
    'electronResults/electronError',
    ({dispatchId,electronId,params}, thunkAPI) =>
    api.get(`dispatches/${dispatchId}/electron/${electronId}/details/${params}`).catch(thunkAPI.rejectWithValue)
)

export const electronExecutor = createAsyncThunk(
    'electronResults/electronExecutor',
    ({dispatchId,electronId,params}, thunkAPI) =>
    api.get(`dispatches/${dispatchId}/electron/${electronId}/details/${params}`).catch(thunkAPI.rejectWithValue)
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

  },
})

export const { resetElectronState } = electronSlice.actions
