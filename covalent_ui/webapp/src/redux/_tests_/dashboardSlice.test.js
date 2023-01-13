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
  fetchDashboardList,
  fetchDashboardOverview,
  deleteDispatches,
  deleteAllDispatches,
  dashboardSlice,
} from '../dashboardSlice'

describe('Dashboard list slice', () => {
  it('dashboard list is fulfilled', () => {
    const action = {
      type: fetchDashboardList.fulfilled,
      payload: { count: 11 },
    }
    const initialState = dashboardSlice.reducer(
      {
        fetchDashboardList: { isFetching: false, error: null },
      },
      action
    )
    expect(initialState).toEqual({
      fetchDashboardList: { isFetching: false, error: null },
    })
  })

  it('dashboard list is pending', () => {
    const action = {
      type: fetchDashboardList.pending,
      payload: { count: 11 },
    }
    const initialState = dashboardSlice.reducer(
      {
        fetchDashboardList: { isFetching: false, error: null },
      },
      action
    )
    expect(initialState).toEqual({
      fetchDashboardList: { isFetching: true, error: null },
    })
  })

  it('dashboard list is rejected', () => {
    const action = {
      type: fetchDashboardList.rejected,
      payload: 'this',
    }
    const initialState = dashboardSlice.reducer(
      {
        fetchDashboardList: { isFetching: false, error: null },
      },
      action
    )
    expect(initialState).toEqual({
      fetchDashboardList: { isFetching: false, error: 'this' },
    })
  })

  it('fetchDashboardOverview list is fulfilled', () => {
    const action = {
      type: fetchDashboardOverview.fulfilled,
      payload: { count: 11 },
    }
    const initialState = dashboardSlice.reducer(
      {
        fetchDashboardOverview: { isFetching: false, error: null },
      },
      action
    )
    expect(initialState).toEqual({
      dashboardOverview: {
        count: 11,
      },
      fetchDashboardOverview: { isFetching: false, error: null },
    })
  })

  it('fetchDashboardOverview  is pending', () => {
    const action = {
      type: fetchDashboardOverview.pending,
      payload: { count: 11 },
    }
    const initialState = dashboardSlice.reducer(
      {
        fetchDashboardOverview: { isFetching: false, error: null },
      },
      action
    )
    expect(initialState).toEqual({
      fetchDashboardOverview: { isFetching: true, error: null },
    })
  })

  it('fetchDashboardOverview list is rejected', () => {
    const action = {
      type: fetchDashboardOverview.rejected,
      payload: 'this',
    }
    const initialState = dashboardSlice.reducer(
      {
        fetchDashboardOverview: { isFetching: false, error: null },
      },
      action
    )
    expect(initialState).toEqual({
      fetchDashboardOverview: { isFetching: false, error: 'this' },
    })
  })

  it('deleteDispatches list is fulfilled', () => {
    const action = {
      type: deleteDispatches.fulfilled,
      payload: { count: 11 },
    }
    const initialState = dashboardSlice.reducer(
      {
        deleteResults: { isFetching: false, isDeleted: false, error: null },
      },
      action
    )
    expect(initialState).toEqual({
      deleteResults: { isFetching: false, isDeleted: true, error: null },
    })
  })

  it('deleteDispatches  is pending', () => {
    const action = {
      type: deleteDispatches.pending,
      payload: { count: 11 },
    }
    const initialState = dashboardSlice.reducer(
      {
        deleteResults: { isFetching: false, error: null },
      },
      action
    )
    expect(initialState).toEqual({
      deleteResults: { isFetching: true, isDeleted: false, error: null },
    })
  })

  it('deleteDispatches list is rejected', () => {
    const action = {
      type: deleteDispatches.rejected,
      payload: 'this',
    }
    const initialState = dashboardSlice.reducer(
      {
        deleteResults: { isFetching: false, error: null },
      },
      action
    )
    expect(initialState).toEqual({
      deleteResults: { isFetching: false, isDeleted: false, error: 'this' },
    })
  })

  it('deleteAllDispatches list is fulfilled', () => {
    const action = {
      type: deleteAllDispatches.fulfilled,
      payload: { count: 11 },
    }
    const initialState = dashboardSlice.reducer(
      {
        deleteResults: { isFetching: false, isDeleted: false, error: null },
      },
      action
    )
    expect(initialState).toEqual({
      deleteResults: { isFetching: false, isDeleted: true, error: null },
    })
  })

  it('deleteAllDispatches  is pending', () => {
    const action = {
      type: deleteAllDispatches.pending,
      payload: { count: 11 },
    }
    const initialState = dashboardSlice.reducer(
      {
        deleteResults: { isFetching: false, error: null },
      },
      action
    )
    expect(initialState).toEqual({
      deleteResults: { isFetching: true, isDeleted: false, error: null },
    })
  })

  it('deleteAllDispatches list is rejected', () => {
    const action = {
      type: deleteAllDispatches.rejected,
      payload: 'this',
    }
    const initialState = dashboardSlice.reducer(
      {
        deleteResults: { isFetching: false, error: null },
      },
      action
    )
    expect(initialState).toEqual({
      deleteResults: { isFetching: false, isDeleted: false, error: 'this' },
    })
  })
})
