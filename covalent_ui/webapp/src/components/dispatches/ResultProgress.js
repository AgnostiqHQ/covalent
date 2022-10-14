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

import { Box, LinearProgress, Tooltip } from '@mui/material'
import { statusLabel } from '../../utils/misc'

const STATUS_COLORS = {
  RUNNING: 'running',
  COMPLETED: 'success',
  FAILED: 'error',
  CANCELLED: 'error',
  POSTPROCESSING: 'success',
  PENDING_POSTPROCESSING: 'success',
  POSTPROCESSING_FAILED: 'success',
}

const ResultProgress = (props) => {
  const { status, totalElectronsCompleted, totalElectrons } = props.result
  return (
    <Tooltip title={statusLabel(status)} placement="right">
      <Box sx={{ display: 'flex', alignItems: 'center', width: '120px' }}>
        <Box data-testid="resultProgress" sx={{ width: '50%', mr: 1 }}>
          <LinearProgress
            variant="determinate"
            color={STATUS_COLORS[status.toUpperCase()]}
            value={(totalElectronsCompleted * 100) / totalElectrons}
          />
        </Box>
        <Box sx={{ width: '50%' }}>
          <Box
            component="div"
            display="inline"
            sx={{
              color: `${STATUS_COLORS[status.toUpperCase()]}.main`,
              fontSize: '1rem',
            }}
          >
            {totalElectronsCompleted}
          </Box>
          <Box
            component="div"
            display="inline"
            sx={{
              color: `${STATUS_COLORS[status.toUpperCase()]}.main`,
              fontSize: '1rem',
            }}
          >
            /{totalElectrons}
          </Box>
        </Box>
      </Box >
    </Tooltip >
  )
}

export default ResultProgress
