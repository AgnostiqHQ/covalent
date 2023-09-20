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

import NavDrawer from '../common/NavDrawer'
import { Container, Typography } from '@mui/material'
import { Box } from '@mui/system'
import LogsListing from './LogsListing'

const LogsLayout = () => {
  return (
    <Box sx={{ display: 'flex' }} data-testid="dashboard">
      <NavDrawer />
      <Container maxWidth="xl" sx={{ mb: 4, mt: '32px' }}>
        <Typography
          fontSize="32px"
          sx={{ color: (theme) => theme.palette.primary.white, mb: 4 }}
        >
          Logs{' '}
        </Typography>
        <LogsListing />
      </Container>
    </Box>
  )
}

export default LogsLayout
