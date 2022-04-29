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

import { Box, LinearProgress, Tooltip, Typography } from '@mui/material'
import { createSelector } from '@reduxjs/toolkit'
import _ from 'lodash'
import { useSelector } from 'react-redux'

import { isParameter } from '../../utils/misc'

const STATUS_COLORS = {
  RUNNING: 'secondary',
  COMPLETED: 'success',
  FAILED: 'error',
  CANCELLED: 'error',
}

export const selectResultProgress = createSelector(
  (state, dispatchId) => state.results.cache[dispatchId],
  (result) => {
    return _.reduce(
      _.get(result, 'graph.nodes'),
      (progress, node) => {
        if (!isParameter(node)) {
          progress.total++
          progress.completed += node.status === 'COMPLETED' ? 1 : 0
          // record first electron error
          if (node.error && !progress.error) {
            progress.error = `${node.name}: ${node.error}`
          }
        }
        return progress
      },
      {
        total: 0,
        completed: 0,
        status: result.status,
        label: _.startCase(_.lowerCase(result.status)),
        color: STATUS_COLORS[result.status],
        error: result.error,
      }
    )
  }
)

const ResultProgress = ({ dispatchId }) => {
  const { completed, total, status, color } = useSelector((state) =>
    selectResultProgress(state, dispatchId)
  )

  return (
    <Tooltip title={status} placement="right">
      <Box sx={{ display: 'flex', alignItems: 'center' }}>
        <Box sx={{ width: '100%', mr: 1 }}>
          <LinearProgress
            variant="determinate"
            color={color}
            value={(completed * 100) / total}
          />
        </Box>

        <Box sx={{ minWidth: 35 }}>
          <Typography variant="body2" color={color}>
            {completed}/{total}
          </Typography>
        </Box>
      </Box>
    </Tooltip>
  )
}

export default ResultProgress
