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
import { Paper, Typography } from '@mui/material'
import Heading from './Heading'

const FETCH_INTERVAL_MS = 2000
const MAX_LINES = 80


export const LogOutput = ({latOutput}) => {
const outputResult = latOutput
return (
    <div>
      <Heading>{outputResult.head}</Heading>
      <Paper>
        <Typography
          sx={{
            fontSize: 'small',
            overflow: 'auto',
            maxHeight: 200,
            whiteSpace: 'nowrap',
            p: 1,
          }}
        >
          {outputResult.message}
        </Typography>
      </Paper>
    </div>
  )
}


export default LogOutput
