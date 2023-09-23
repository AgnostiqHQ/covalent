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
