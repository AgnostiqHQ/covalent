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

import _ from 'lodash'
import demoDashboardListData from './dashboardDemoData'
import logsDemoData from './logsDemoData'
import latticeDetailsDemoData from './latticeDemoData'
import graphDemoData from './graphDemoData'
import latticePreview from './draw-a'

/**
 * Demo mode switch based on build-time environment variable (see package.json).
 */
export const isDemo = _.toLower(process.env.REACT_APP_DEMO) === 'true'

export const demoEnhancer =
  (createStore) => (reducer, initialState, enhancer) => {
    return createStore(reducer, demoState, enhancer)
  }

/**
 * Used as redux store preloaded state for static demo.
 *
 */
export const demoState = {
  dashboard: {
    dashboardOverview: demoDashboardListData.dashboardOverview,
    fetchDashboardList: { isFetching: false, error: null },
    fetchDashboardOverview: { isFetching: false, error: null },
    deleteResults: { isFetching: false, error: null },
    overallDashboardList: demoDashboardListData.dashboardList,
    dashboardList: demoDashboardListData.dashboardList,
    totalDispatches: demoDashboardListData.dashboardList.total_count
  },
  latticeResults: {
    latticeResultsData: latticeDetailsDemoData,
    latticeDetailsResults: { isFetching: false, error: null },
    latticeResultsList: { isFetching: false, error: null },
    latticeOutputList: { isFetching: false, error: null },
    latticeFunctionStringList: { isFetching: false, error: null },
    latticeInputList: { isFetching: false, error: null },
    latticeErrorList: { isFetching: false, error: null },
    latticeExecutorDetailList: { isFetching: false, error: null },
  },
  graphResults: graphDemoData,
  latticePreview,
  logs: {
    logList: logsDemoData.logList,
    fetchLogList: { isFetching: false, error: null },
    totalLogs:5
  }
}
