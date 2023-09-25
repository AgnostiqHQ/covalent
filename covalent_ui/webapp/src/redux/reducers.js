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

import { commonSlice } from './commonSlice'
import { latticePreviewSlice } from './latticePreviewSlice'
import { dashboardSlice } from './dashboardSlice'
import { graphSlice } from './graphSlice'
import { latticeSlice } from './latticeSlice'
import { electronSlice } from './electronSlice'
import { settingsSlice } from './settingsSlice'
import { logsSlice } from './logsSlice'
import { popupSlice } from './popupSlice'

const reducers = {
  common: commonSlice.reducer,
  latticePreview: latticePreviewSlice.reducer,
  dashboard: dashboardSlice.reducer,
  graphResults: graphSlice.reducer,
  latticeResults: latticeSlice.reducer,
  electronResults: electronSlice.reducer,
  settingsResults: settingsSlice.reducer,
  dataRes: popupSlice.reducer,
  logs: logsSlice.reducer,
}

export default reducers
