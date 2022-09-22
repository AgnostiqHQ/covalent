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

import { commonSlice } from './commonSlice'
import { latticePreviewSlice } from './latticePreviewSlice'
import { dashboardSlice } from './dashboardSlice'
import { graphSlice } from './graphSlice'
import { latticeSlice } from './latticeSlice'
import { electronSlice } from './electronSlice'
import { settingsSlice } from './settingsSlice'
import { logsSlice } from './logsSlice'

const reducers = {
  common: commonSlice.reducer,
  latticePreview: latticePreviewSlice.reducer,
  dashboard: dashboardSlice.reducer,
  graphResults: graphSlice.reducer,
  latticeResults: latticeSlice.reducer,
  electronResults: electronSlice.reducer,
  settingsResults: settingsSlice.reducer,
  logs: logsSlice.reducer,
}

export default reducers
