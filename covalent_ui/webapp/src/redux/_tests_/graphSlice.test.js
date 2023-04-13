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

import { graphResults, graphSlice } from '../graphSlice'

describe('graph slice tests', () => {
  it('graph slice rendered rejected', () => {
    const action = { type: graphResults.rejected }
    const initialState = graphSlice.reducer(
      {
        graphList: {},
        graphResultsList: { isFetching: false, error: undefined },
      },
      action
    )
    expect(initialState).toEqual({
      graphList: {},
      graphResultsList: { isFetching: false, error: undefined },
    })
  })

  it('graph slice rendered pending', () => {
    const action = { type: graphResults.pending }
    const initialState = graphSlice.reducer(
      {
        graphList: {},
        graphResultsList: { isFetching: false, error: null },
      },
      action
    )
    expect(initialState).toEqual({
      graphList: {},
      graphResultsList: { isFetching: true, error: null },
    })
  })

  it('graph slice rendered fulfilled', () => {
    const action = {
      type: graphResults.fulfilled,
      payload: {
        links: [
          {
            arg_index: 0,
            edge_name: 'x',
            parameter_type: 'kwarg',
            source: 69,
            target: 82,
          },
          {
            arg_index: 0,
            edge_name: 'x',
            parameter_type: 'kwarg',
            source: 69,
            target: 90,
          },
          {
            arg_index: 0,
            edge_name: 'x',
            parameter_type: 'kwarg',
            source: 69,
            target: 98,
          },
        ],

        nodes: [
          {
            completed_at: '2022-08-09T06:19:32.183245',
            id: 69,
            name: 'identity',
            node_id: 0,
            started_at: '2022-08-09T06:19:31.969697',
            status: 'COMPLETED',
            type: 'function',
          },
          {
            completed_at: '2022-08-09T06:19:31.905793',
            id: 70,
            name: ':parameter:1',
            node_id: 1,
            started_at: '2022-08-09T06:19:31.905790',
            status: 'COMPLETED',
            type: 'parameter',
          },
          {
            completed_at: '2022-08-09T06:19:32.203227',
            id: 71,
            name: 'identity',
            node_id: 2,
            started_at: '2022-08-09T06:19:31.980171',
            status: 'COMPLETED',
            type: 'function',
          },
        ],
      },
    }
    const initialState = graphSlice.reducer(
      {
        graphResultsList: { isFetching: false, error: null },
      },
      action
    )
    expect(initialState).toEqual({
      graphResultsList: { isFetching: false, error: null },
    })
  })
})
