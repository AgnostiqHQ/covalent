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

import { fetchLogsList, downloadCovalentLogFile, logsSlice } from '../logsSlice'

describe('LogsList slice', () => {
  it('fetchLogsList is pending', () => {
    const action = fetchLogsList.pending(
      // <-- THIS
      {
        fetchLogList: { isFetching: true, error: null },
      }
    )
    const initialState = {
      fetchLogList: { isFetching: false, error: null },
    }

    expect(logsSlice.reducer(initialState, action)).toEqual({
      fetchLogList: { isFetching: true, error: null },
    })
  })

  it('fetchLogsList is fulfilled', () => {
    const action = {
      type: fetchLogsList.fulfilled,
      payload: {
        total_count: 12,
        items: {},
      },
    }
    const initialState = logsSlice.reducer(
      {
        fetchLogList: { isFetching: false, error: null },
      },
      action
    )
    expect(initialState).toEqual({
      fetchLogList: { isFetching: false, error: null },
      logList: {},
      totalLogs: 12,
    })
  })

  it('fetchLogsList is rejected', () => {
    const action = {
      type: fetchLogsList.rejected,
      payload: 'value',
    }
    const initialState = logsSlice.reducer(
      {
        fetchLogList: { isFetching: false, error: null },
      },
      action
    )
    expect(initialState).toEqual({
      fetchLogList: { isFetching: false, error: 'value' },
    })
  })

  it('downloadCovalentLogFile is pending', () => {
    const action = downloadCovalentLogFile.pending(
      // <-- THIS
      {
        logFileList: { isFetching: true, error: null },
      }
    )
    const initialState = {
      logFileList: { isFetching: false, error: null },
    }

    expect(logsSlice.reducer(initialState, action)).toEqual({
      logFileList: { isFetching: true, error: null },
    })
  })

  it('downloadCovalentLogFile is fulfilled', () => {
    const action = {
      type: downloadCovalentLogFile.fulfilled,
      payload: {},
    }
    const initialState = logsSlice.reducer(
      {
        logFileList: { isFetching: false, error: null },
      },
      action
    )
    expect(initialState).toEqual({
      logFileList: { isFetching: false, error: null },
      logFile: {},
    })
  })

  it('downloadCovalentLogFile is rejected', () => {
    const action = {
      type: downloadCovalentLogFile.rejected,
      payload: 'value',
    }
    const initialState = logsSlice.reducer(
      {
        logFileList: { isFetching: false, error: null },
      },
      action
    )
    expect(initialState).toEqual({
      logFileList: { isFetching: false, error: 'value' },
    })
  })
})
