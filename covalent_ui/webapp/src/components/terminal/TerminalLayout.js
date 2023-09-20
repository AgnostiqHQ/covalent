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
import React, { Suspense, lazy } from 'react'
import { Box } from '@mui/system'
import { Container, Grid, Chip, Typography } from '@mui/material'
import NavDrawer from '../common/NavDrawer'
import PageLoading from '../common/PageLoading'
const TerminalUI = lazy(() => import('../terminal/Terminal'));
const TerminalLayout = () => {
  return (
    <Box sx={{ display: 'flex' }} data-testid="dashboard">
      <NavDrawer />
      <Container maxWidth="xl" sx={{ mb: 4, mt: '32px' }}>
        <Grid xs={12} sx={{ mb: 4 }}>
          <Typography
            sx={{
              fontSize: '2rem',
              color: (theme) => theme.palette.primary.white,
            }}
            component="h4"
            display="inline"
          >
            Terminal
          </Typography>
          <Chip
            sx={{
              height: '24px',
              ml: 1,
              mb: 1.5,
              fontSize: '0.75rem',
              color: '#FFFFFF',
            }}
            label="BETA"
            variant="outlined"
          />
        </Grid>
        <Suspense fallback={<PageLoading />}>
          <TerminalUI />
        </Suspense>
      </Container>
    </Box>
  )
}
export default TerminalLayout
