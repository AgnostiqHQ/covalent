import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'

import api from '../utils/api'

const initialState = {
  graphList:{},
  graphResultsList: { isFetching: false, error: null },
}

export const graphResults = createAsyncThunk(
  'results/graphResults',
  ({dispatchId}, thunkAPI) => api.get(`dispatches/${dispatchId}/graph`).catch(thunkAPI.rejectWithValue)
)

export const graphSlice = createSlice({
  name: 'results',
  initialState,
  reducers: {
    resetGraphState() {
      return initialState
    }
  },
  extraReducers: (builder) => {
    builder
       // graph Results
       .addCase(graphResults.fulfilled, (state, { payload }) => {
        state.graphResultsList.isFetching = false
        // update results cache
        state.graphList = payload.graph
      })
      .addCase(graphResults.pending, (state) => {
        state.graphResultsList.isFetching = true
        state.graphResultsList.error = null
      })
      .addCase(graphResults.rejected, (state, { payload }) => {
        state.graphResultsList.isFetching = false
        state.graphResultsList.error = payload.detail
      })

  },
})

export const { resetGraphState } = graphSlice.actions
