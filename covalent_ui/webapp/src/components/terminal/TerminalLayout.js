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

import { Box } from '@mui/system'
import { Container, Grid, Chip,Typography } from '@mui/material';
import NavDrawer from '../common/NavDrawer'
import Terminal from '../terminal/Terminal'

const TerminalLayout = () => {
  return (
    <Box sx={{ display: 'flex' }} data-testid="dashboard">
      <NavDrawer />
      <Container maxWidth="xl" sx={{ mb: 4, mt: '32px' }}>
        <Grid xs={12} sx={{ mb: 4 }}>
          <Typography sx={{ fontSize: '2rem' }} component="h4" display="inline">
            Terminal
          </Typography>
          <Chip sx={{ height: '24px', ml: 1, mb: 1.5, fontSize: '0.75rem', color: '#FFFFFF' }} label='BETA' variant='outlined' />
        </Grid>
        <Terminal />
      </Container>
    </Box>
  )
}

export default TerminalLayout
