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
import { useSelector } from 'react-redux'
import { CheckCircleOutline, Close, WarningAmber } from '@mui/icons-material'
import {
  Box,
  CircularProgress,
  Divider,
  Drawer,
  IconButton,
  Paper,
  Typography,
} from '@mui/material'
import { useStoreActions } from 'react-flow-renderer'

import { formatDate, statusColor, statusLabel } from '../../utils/misc'
import Runtime from '../results/Runtime'
import SyntaxHighlighter from '../SyntaxHighlighter'
import Heading from './Heading'

export const nodeDrawerWidth = 360

const NodeDrawer = ({ dispatchId, nodeId }) => {
  const node = useSelector((state) =>
    _.find(
      _.get(state.results.cache[dispatchId], 'graph.nodes'),
      (node) => nodeId === String(_.get(node, 'id'))
    )
  )

  // unselect on close
  const setSelectedElements = useStoreActions(
    (actions) => actions.setSelectedElements
  )
  const handleClose = () => {
    setSelectedElements([])
  }

  const src = _.get(node, 'function_string', '# source unavailable')
  const hasStarted = !!_.get(node, 'start_time')
  const hasEnded = !!_.get(node, 'end_time')

  return (
    <Drawer
      sx={{
        width: nodeDrawerWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: nodeDrawerWidth,
          boxSizing: 'border-box',
          border: 'none',
          p: 2,
        },
      }}
      anchor="right"
      variant="persistent"
      open={!!nodeId}
      onClose={handleClose}
    >
      {!!node && (
        <>
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'space-between',
              mb: 3,
            }}
          >
            <Typography sx={{ color: '#A5A6F6', overflowWrap: 'anywhere' }}>
              {node.name}
            </Typography>
            <Box>
              <IconButton onClick={handleClose}>
                <Close />
              </IconButton>
            </Box>
          </Box>

          <Typography color="text.secondary" variant="body2">
            Status
          </Typography>

          <Box
            sx={{
              mt: 1,
              color: statusColor(node.status),
              display: 'flex',
              alignItems: 'center',
            }}
          >
            {(() => {
              switch (node.status) {
                case 'RUNNING':
                  return <CircularProgress size="1rem" />
                case 'COMPLETED':
                  return <CheckCircleOutline />
                case 'FAILED':
                  return <WarningAmber />
                default:
                  return null
              }
            })()}
            &nbsp;
            {statusLabel(node.status)}
          </Box>

          {node.doc && (
            <>
              <Heading>Description</Heading>
              <Typography>{node.doc}</Typography>
            </>
          )}

          {hasStarted && (
            <>
              <Heading>Started{hasEnded ? ' - Ended' : ''}</Heading>
              <Typography>
                {formatDate(node.start_time)}
                {hasEnded && `- ${formatDate(node.end_time)}`}
              </Typography>
            </>
          )}

          <Heading />
          <Paper elevation={4}>
            <SyntaxHighlighter src={src} />
          </Paper>

          <Divider sx={{ my: 2 }} />

          {node.status !== 'NEW_OBJECT' && (
            <>
              <Heading>Runtime</Heading>
              <Runtime startTime={node.start_time} endTime={node.end_time} />
            </>
          )}

          {node.status === 'COMPLETED' && (
            <>
              <Heading>Result</Heading>
              <Paper elevation={4}>
                <SyntaxHighlighter language="json" src={node.output} />
              </Paper>
            </>
          )}
        </>
      )}
    </Drawer>
  )
}

export default NodeDrawer
