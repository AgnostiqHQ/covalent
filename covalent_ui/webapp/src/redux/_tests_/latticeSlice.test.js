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
  latticeDetails, latticeResults, latticeOutput, latticeFunctionString, latticeInput,
  latticeError, latticeExecutorDetail, latticeSlice
} from '../latticeSlice'

describe('LATTICE DETAILS SLICE TESTS', () => {

  it('lattice details is fullfilled', () => {
    const action = {
      type: latticeDetails.fulfilled,
    };
    const initialState = latticeSlice.reducer(
      {
        latticeDetailsResults: { isFetching: false },
      }, action);
    expect(initialState).toEqual({
      latticeDetailsResults: { isFetching: false },
    })
  })

  it('lattice details is pending', () => {
    const action = { type: latticeDetails.pending };
    const initialState = latticeSlice.reducer(
      {
        latticeDetailsResults: { isFetching: false, error: null },
      }, action);
    expect(initialState).toEqual({
      latticeDetailsResults: { isFetching: true, error: null },
    })
  })

  it('lattice details is rejected', () => {
    const action = { type: latticeDetails.rejected };
    const initialState = latticeSlice.reducer(
      {
        latticeDetailsResults: { isFetching: false, error: null },
      }, action);
    expect(initialState).toEqual({
      latticeDetailsResults: { isFetching: false, error: undefined },
    })
  })

})

describe('LATTICE RESULTS SLICE TESTS', () => {

  it('lattice results is fullfilled', () => {
    const action = {
      type: latticeResults.fulfilled,
    };
    const initialState = latticeSlice.reducer(
      {
        latticeResultsList: { isFetching: false },
      }, action);
    expect(initialState).toEqual({
      latticeResultsList: { isFetching: false },
    })
  })

  it('lattice results is pending', () => {
    const action = { type: latticeResults.pending };
    const initialState = latticeSlice.reducer(
      {
        latticeResultsList: { isFetching: false, error: null },
      }, action);
    expect(initialState).toEqual({
      latticeResultsList: { isFetching: true, error: null },
    })
  })

  it('lattice results is rejected', () => {
    const action = { type: latticeResults.rejected };
    const initialState = latticeSlice.reducer(
      {
        latticeResultsList: { isFetching: false, error: null },
      }, action);
    expect(initialState).toEqual({
      latticeResultsList: { isFetching: false, error: undefined },
    })
  })

})

describe('LATTICE OUTPUT SLICE TESTS', () => {

  it('lattice output is fullfilled', () => {
    const action = {
      type: latticeOutput.fulfilled,
    };
    const initialState = latticeSlice.reducer(
      {
        latticeOutputList: { isFetching: false },
      }, action);
    expect(initialState).toEqual({
      latticeOutputList: { isFetching: false },
    })
  })

  it('lattice output is pending', () => {
    const action = { type: latticeOutput.pending };
    const initialState = latticeSlice.reducer(
      {
        latticeOutputList: { isFetching: false, error: null },
      }, action);
    expect(initialState).toEqual({
      latticeOutputList: { isFetching: true, error: null },
    })
  })

  it('lattice output is rejected', () => {
    const action = { type: latticeOutput.rejected };
    const initialState = latticeSlice.reducer(
      {
        latticeOutputList: { isFetching: false, error: null },
      }, action);
    expect(initialState).toEqual({
      latticeOutputList: { isFetching: false, error: undefined },
    })
  })

})

describe('LATTICE FUNCTIONTOSTRING SLICE TESTS', () => {

  it('lattice function to string is fullfilled', () => {
    const action = {
      type: latticeFunctionString.fulfilled,
    };
    const initialState = latticeSlice.reducer(
      {
        latticeFunctionStringList: { isFetching: false },
      }, action);
    expect(initialState).toEqual({
      latticeFunctionStringList: { isFetching: false },
    })
  })

  it('lattice function to string is pending', () => {
    const action = { type: latticeFunctionString.pending };
    const initialState = latticeSlice.reducer(
      {
        latticeFunctionStringList: { isFetching: false, error: null },
      }, action);
    expect(initialState).toEqual({
      latticeFunctionStringList: { isFetching: true, error: null },
    })
  })

  it('lattice function to string is rejected', () => {
    const action = { type: latticeFunctionString.rejected };
    const initialState = latticeSlice.reducer(
      {
        latticeFunctionStringList: { isFetching: false, error: null },
      }, action);
    expect(initialState).toEqual({
      latticeFunctionStringList: { isFetching: false, error: undefined },
    })
  })

})

describe('LATTICE INPUT SLICE TESTS', () => {

  it('lattice input is fullfilled', () => {
    const action = {
      type: latticeInput.fulfilled,
    };
    const initialState = latticeSlice.reducer(
      {
        latticeInputList: { isFetching: false },
      }, action);
    expect(initialState).toEqual({
      latticeInputList: { isFetching: false },
    })
  })

  it('lattice input pending', () => {
    const action = { type: latticeInput.pending };
    const initialState = latticeSlice.reducer(
      {
        latticeInputList: { isFetching: false, error: null },
      }, action);
    expect(initialState).toEqual({
      latticeInputList: { isFetching: true, error: null },
    })
  })

  it('lattice input is rejected', () => {
    const action = { type: latticeInput.rejected };
    const initialState = latticeSlice.reducer(
      {
        latticeInputList: { isFetching: false, error: null },
      }, action);
    expect(initialState).toEqual({
      latticeInputList: { isFetching: false, error: undefined },
    })
  })

})

describe('LATTICE ERROR SLICE TESTS', () => {

  it('lattice error is fullfilled', () => {
    const action = {
      type: latticeError.fulfilled,
    };
    const initialState = latticeSlice.reducer(
      {
        latticeErrorList: { isFetching: false },
      }, action);
    expect(initialState).toEqual({
      latticeErrorList: { isFetching: false },
    })
  })

  it('lattice error pending', () => {
    const action = { type: latticeError.pending };
    const initialState = latticeSlice.reducer(
      {
        latticeErrorList: { isFetching: false, error: null },
      }, action);
    expect(initialState).toEqual({
      latticeErrorList: { isFetching: true, error: null },
    })
  })

  it('lattice error is rejected', () => {
    const action = { type: latticeError.rejected };
    const initialState = latticeSlice.reducer(
      {
        latticeErrorList: { isFetching: false, error: null },
      }, action);
    expect(initialState).toEqual({
      latticeErrorList: { isFetching: false, error: undefined },
    })
  })

})

describe('LATTICE ERROR SLICE TESTS', () => {

  it('lattice executor details is fullfilled', () => {
    const action = {
      type: latticeExecutorDetail.fulfilled,
    };
    const initialState = latticeSlice.reducer(
      {
        latticeExecutorDetailList: { isFetching: false },
      }, action);
    expect(initialState).toEqual({
      latticeExecutorDetailList: { isFetching: false },
    })
  })

  it('lattice executor details pending', () => {
    const action = { type: latticeExecutorDetail.pending };
    const initialState = latticeSlice.reducer(
      {
        latticeExecutorDetailList: { isFetching: false, error: null },
      }, action);
    expect(initialState).toEqual({
      latticeExecutorDetailList: { isFetching: true, error: null },
    })
  })

  it('lattice executor details is rejected', () => {
    const action = { type: latticeExecutorDetail.rejected };
    const initialState = latticeSlice.reducer(
      {
        latticeExecutorDetailList: { isFetching: false, error: null },
      }, action);
    expect(initialState).toEqual({
      latticeExecutorDetailList: { isFetching: false, error: undefined },
    })
  })

})
