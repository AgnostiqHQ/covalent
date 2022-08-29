// /**
//  * Copyright 2021 Agnostiq Inc.
//  *
//  * This file is part of Covalent.
//  *
//  * Licensed under the GNU Affero General Public License 3.0 (the "License").
//  * A copy of the License may be obtained with this software package or at
//  *
//  *      https://www.gnu.org/licenses/agpl-3.0.en.html
//  *
//  * Use of this file is prohibited except in compliance with the License. Any
//  * modifications or derivative works of this file must retain this copyright
//  * notice, and modified files must contain a notice indicating that they have
//  * been altered from the originals.
//  *
//  * Covalent is distributed in the hope that it will be useful, but WITHOUT
//  * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
//  * FITNESS FOR A PARTICULAR PURPOSE. See the License for more details.
//  *
//  * Relief from the License may be granted by purchasing a commercial license.
//  */

import {
  electronDetails, electronResult, electronFunctionString, electronInput, electronError,
  electronExecutor, electronSlice
} from '../electronSlice'

describe('ELECTRON DETAILS SLICE TESTS', () => {

  it('electron deatsils is fullfilled', () => {
    const action = {
      type: electronDetails.fulfilled,
    };
    const initialState = electronSlice.reducer(
      {
        electronDetailsList: { isFetching: false, error: null },
      }, action);
    expect(initialState).toEqual({
      electronDetailsList: { isFetching: false, error: null },
    })
  })

  it('electron deatsils is pending', () => {
    const action = { type: electronDetails.pending };
    const initialState = electronSlice.reducer(
      {
        electronDetailsList: { isFetching: false, error: null },
      }, action);
    expect(initialState).toEqual({
      electronDetailsList: { isFetching: true, error: null },
    })
  })

  it('electron deatsils is rejected', () => {
    const action = { type: electronDetails.rejected };
    const initialState = electronSlice.reducer(
      {
        electronDetailsList: { isFetching: false, error: null },
      }, action);
    expect(initialState).toEqual({
      electronDetailsList: { isFetching: false, error: undefined },
    })
  })

})

describe('ELECTRON RESULTS SLICE TESTS', () => {

  it('electron results is fullfilled', () => {
    const action = {
      type: electronResult.fulfilled,
    };
    const initialState = electronSlice.reducer(
      {
        electronResultList: { isFetching: false, error: null },
      }, action);
    expect(initialState).toEqual({
      electronResultList: { isFetching: false, error: null },
    })
  })

  it('electron results is pending', () => {
    const action = { type: electronResult.pending };
    const initialState = electronSlice.reducer(
      {
        electronResultList: { isFetching: false, error: null },
      }, action);
    expect(initialState).toEqual({
      electronResultList: { isFetching: true, error: null },
    })
  })

  it('electron results is rejected', () => {
    const action = { type: electronResult.rejected };
    const initialState = electronSlice.reducer(
      {
        electronResultList: { isFetching: false, error: null },
      }, action);
    expect(initialState).toEqual({
      electronResultList: { isFetching: false, error: undefined },
    })
  })

})

describe('ELECTRON FUNCTION TO STRING SLICE TESTS', () => {

  it('electron function to string is fullfilled', () => {
    const action = {
      type: electronFunctionString.fulfilled,
    };
    const initialState = electronSlice.reducer(
      {
        electronFunctionStringList: { isFetching: false, error: null },
      }, action);
    expect(initialState).toEqual({
      electronFunctionStringList: { isFetching: false, error: null },
    })
  })

  it('electron function to string is pending', () => {
    const action = { type: electronFunctionString.pending };
    const initialState = electronSlice.reducer(
      {
        electronFunctionStringList: { isFetching: false, error: null },
      }, action);
    expect(initialState).toEqual({
      electronFunctionStringList: { isFetching: true, error: null },
    })
  })

  it('electron function to string is rejected', () => {
    const action = { type: electronFunctionString.rejected };
    const initialState = electronSlice.reducer(
      {
        electronFunctionStringList: { isFetching: false, error: null },
      }, action);
    expect(initialState).toEqual({
      electronFunctionStringList: { isFetching: false, error: undefined },
    })
  })

})

describe('ELECTRON INPUT SLICE TESTS', () => {

  it('electron input is fullfilled', () => {
    const action = {
      type: electronInput.fulfilled,
    };
    const initialState = electronSlice.reducer(
      {
        electronInputList: { isFetching: false, error: null },
      }, action);
    expect(initialState).toEqual({
      electronInputList: { isFetching: false, error: null },
    })
  })

  it('electron input is pending', () => {
    const action = { type: electronInput.pending };
    const initialState = electronSlice.reducer(
      {
        electronInputList: { isFetching: false, error: null },
      }, action);
    expect(initialState).toEqual({
      electronInputList: { isFetching: true, error: null },
    })
  })

  it('electron input is rejected', () => {
    const action = { type: electronInput.rejected };
    const initialState = electronSlice.reducer(
      {
        electronInputList: { isFetching: false, error: null },
      }, action);
    expect(initialState).toEqual({
      electronInputList: { isFetching: false, error: undefined },
    })
  })

})

describe('ELECTRON ERROR SLICE TESTS', () => {

  it('electron error is fullfilled', () => {
    const action = {
      type: electronError.fulfilled,
    };
    const initialState = electronSlice.reducer(
      {
        electronErrorList: { isFetching: false, error: null },
      }, action);
    expect(initialState).toEqual({
      electronErrorList: { isFetching: false, error: null },
    })
  })

  it('electron error is pending', () => {
    const action = { type: electronError.pending };
    const initialState = electronSlice.reducer(
      {
        electronErrorList: { isFetching: false, error: null },
      }, action);
    expect(initialState).toEqual({
      electronErrorList: { isFetching: true, error: null },
    })
  })

  it('electron error is rejected', () => {
    const action = { type: electronError.rejected };
    const initialState = electronSlice.reducer(
      {
        electronErrorList: { isFetching: false, error: null },
      }, action);
    expect(initialState).toEqual({
      electronErrorList: { isFetching: false, error: undefined },
    })
  })

})

describe('ELECTRON EXECUTOR DETAILS TESTS', () => {

  it('electron executor is fullfilled', () => {
    const action = {
      type: electronExecutor.fulfilled,
    };
    const initialState = electronSlice.reducer(
      {
        electronExecutorList: { isFetching: false, error: null },
      }, action);
    expect(initialState).toEqual({
      electronExecutorList: { isFetching: false, error: null },
    })
  })

  it('electron executor is pending', () => {
    const action = { type: electronExecutor.pending };
    const initialState = electronSlice.reducer(
      {
        electronExecutorList: { isFetching: false, error: null },
      }, action);
    expect(initialState).toEqual({
      electronExecutorList: { isFetching: true, error: null },
    })
  })

  it('electron executor is rejected', () => {
    const action = { type: electronExecutor.rejected };
    const initialState = electronSlice.reducer(
      {
        electronExecutorList: { isFetching: false, error: null },
      }, action);
    expect(initialState).toEqual({
      electronExecutorList: { isFetching: false, error: undefined },
    })
  })

})
