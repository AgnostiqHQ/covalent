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
  latticeDetails: {},
  latticeError: {},
  latticeOutput: {},
  latticeResult: {},
  latticeInput: {},
  latticeFunctionString: {},
  latticeExecutorDetail: {},
  sublatticesList:[],
  latticeDetailsResults: { isFetching: false, error: null },
  latticeResultsList: { isFetching: false, error: null },
  latticeOutputList: { isFetching: false, error: null },
  latticeFunctionStringList: { isFetching: false, error: null },
  latticeInputList: { isFetching: false, error: null },
  latticeErrorList: { isFetching: false, error: null },
  latticeExecutorDetailList: { isFetching: false, error: null },
  sublatticesListResults: { isFetching: false, error: null },
}

export const latticeDetails = createAsyncThunk(
  'latticeResults/latticeDetails',
  ({ dispatchId }, thunkAPI) =>
    api.get(`api/v1/dispatches/${dispatchId}`).catch(thunkAPI.rejectWithValue)
)

export const latticeResults = createAsyncThunk(
  'latticeResults/latticeResults',
  ({ dispatchId, params }, thunkAPI) =>
    api
      .get(`api/v1/dispatches/${dispatchId}/details/${params}`)
      .catch(thunkAPI.rejectWithValue)
)

export const latticeOutput = createAsyncThunk(
  'latticeResults/latticeOutput',
  ({ dispatchId, params }, thunkAPI) =>
    api
      .get(`api/v1/dispatches/${dispatchId}/details/${params}`)
      .catch(thunkAPI.rejectWithValue)
)

export const latticeFunctionString = createAsyncThunk(
  'latticeResults/latticeFunctionString',
  ({ dispatchId, params }, thunkAPI) =>
    api
      .get(`api/v1/dispatches/${dispatchId}/details/${params}`)
      .catch(thunkAPI.rejectWithValue)
)

export const latticeInput = createAsyncThunk(
  'latticeResults/latticeInput',
  ({ dispatchId, params }, thunkAPI) =>
    api
      .get(`api/v1/dispatches/${dispatchId}/details/${params}`)
      .catch(thunkAPI.rejectWithValue)
)

export const latticeError = createAsyncThunk(
  'latticeResults/latticeError',
  ({ dispatchId, params }, thunkAPI) =>
    api
      .get(`api/v1/dispatches/${dispatchId}/details/${params}`)
      .catch(thunkAPI.rejectWithValue)
)

export const latticeExecutorDetail = createAsyncThunk(
  'latticeResults/latticeExecutorDetail',
  ({ dispatchId, params }, thunkAPI) =>
    api
      .get(`api/v1/dispatches/${dispatchId}/details/${params}`)
      .catch(thunkAPI.rejectWithValue)
)

export const sublatticesListDetails = createAsyncThunk(
  'latticeResults/sublatticesList',
  async (bodyParams, thunkAPI) =>
    await api
      .get(
        `api/v1/dispatches/${bodyParams.dispatchId}/sublattices?sort_by=${bodyParams.sort_by}&sort_direction=${bodyParams.direction}`
      )
      .catch(thunkAPI.rejectWithValue)
)


export const latticeSlice = createSlice({
  name: 'latticeResults',
  initialState,
  reducers: {
    resetLatticeState() {
      return initialState
    },
  },
  extraReducers: (builder) => {
    builder
      // latticeDeatils
      .addCase(latticeDetails.fulfilled, (state, { payload }) => {
        state.latticeDetailsResults.isFetching = false
        state.latticeDetails = payload
      })
      .addCase(latticeDetails.pending, (state) => {
        state.latticeDetailsResults.isFetching = true
        state.latticeDetailsResults.error = null
      })
      .addCase(latticeDetails.rejected, (state, { payload }) => {
        state.latticeDetailsResults.isFetching = false
        state.latticeDetailsResults.error = payload
      })

      // latticeResults
      .addCase(latticeResults.fulfilled, (state, { payload }) => {
        state.latticeResultsList.isFetching = false
        state.latticeResult = payload
      })
      .addCase(latticeResults.pending, (state) => {
        state.latticeResultsList.isFetching = true
        state.latticeResultsList.error = null
      })
      .addCase(latticeResults.rejected, (state, { payload }) => {
        state.latticeResultsList.isFetching = false
        state.latticeResultsList.error = payload
      })

      // latticeOutput
      .addCase(latticeOutput.fulfilled, (state, { payload }) => {
        state.latticeOutputList.isFetching = false
        state.latticeOutput = payload
      })
      .addCase(latticeOutput.pending, (state) => {
        state.latticeOutputList.isFetching = true
        state.latticeOutputList.error = null
      })
      .addCase(latticeOutput.rejected, (state, { payload }) => {
        state.latticeOutputList.isFetching = false
        state.latticeOutputList.error = payload
      })

      // latticeFunctiontostring
      .addCase(latticeFunctionString.fulfilled, (state, { payload }) => {
        state.latticeFunctionStringList.isFetching = false
        state.latticeFunctionString = payload
      })
      .addCase(latticeFunctionString.pending, (state) => {
        state.latticeFunctionStringList.isFetching = true
        state.latticeFunctionStringList.error = null
      })
      .addCase(latticeFunctionString.rejected, (state, { payload }) => {
        state.latticeFunctionStringList.isFetching = false
        state.latticeFunctionStringList.error = payload
      })

      // latticeInput
      .addCase(latticeInput.fulfilled, (state, { payload }) => {
        state.latticeInputList.isFetching = false
        state.latticeInput = payload
      })
      .addCase(latticeInput.pending, (state) => {
        state.latticeInputList.isFetching = true
        state.latticeInputList.error = null
      })
      .addCase(latticeInput.rejected, (state, { payload }) => {
        state.latticeInputList.isFetching = false
        state.latticeInputList.error = payload
      })

      // latticeError
      .addCase(latticeError.fulfilled, (state, { payload }) => {
        state.latticeErrorList.isFetching = false
        state.latticeError = payload
      })
      .addCase(latticeError.pending, (state) => {
        state.latticeErrorList.isFetching = true
        state.latticeErrorList.error = null
      })
      .addCase(latticeError.rejected, (state, { payload }) => {
        state.latticeErrorList.isFetching = false
        state.latticeErrorList.error = payload
      })

      // latticeExecutorDetails
      .addCase(latticeExecutorDetail.fulfilled, (state, { payload }) => {
        state.latticeExecutorDetailList.isFetching = false
        state.latticeExecutorDetail = payload
      })
      .addCase(latticeExecutorDetail.pending, (state) => {
        state.latticeExecutorDetailList.isFetching = true
        state.latticeExecutorDetailList.error = null
      })
      .addCase(latticeExecutorDetail.rejected, (state, { payload }) => {
        state.latticeExecutorDetailList.isFetching = false
        state.latticeExecutorDetailList.error = payload
      })

      //sublatticesList
      .addCase(sublatticesListDetails.fulfilled, (state, { payload }) => {
        state.sublatticesListResults.isFetching = false
        state.sublatticesList = payload.sub_lattices
      })
      .addCase(sublatticesListDetails.pending, (state, { payload }) => {
        state.sublatticesListResults.isFetching = true
        state.sublatticesListResults.error = null
      })
      .addCase(sublatticesListDetails.rejected, (state, { payload }) => {
        state.sublatticesListResults.isFetching = false
        state.sublatticesListResults.error = payload
      })
  },
})

export const { resetLatticeState } = latticeSlice.actions
