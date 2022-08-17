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
import { Close } from '@mui/icons-material'
import {
  Box,
  Divider,
  Drawer,
  IconButton,
  Paper,
  Typography,
} from '@mui/material'
import { useStoreActions } from 'react-flow-renderer'
import { alpha } from '@mui/material/styles'

import {
  statusColor,
  statusIcon,
  statusLabel,
} from '../../utils/misc'
import InputSection from '../common/InputSection'
import SyntaxHighlighter from '../common/SyntaxHighlighter'
import Heading from '../common/Heading'
import ErrorCard from '../common/ErrorCard'
import ExecutorSection from './ExecutorSection'

export const nodeDrawerWidth = 360

const NodeDrawer = ({ node }) => {
  const preview = useSelector((state) => state.latticePreview.lattice)   // unselect on close
  const setSelectedElements = useStoreActions(
    (actions) => actions.setSelectedElements
  )
  const handleClose = () => {
    setSelectedElements([])
  }

  const src = _.get(node, 'function_string', '# source unavailable')
  return (
    <Drawer
      sx={(theme) => ({
        width: nodeDrawerWidth,
        '& .MuiDrawer-paper': {
          width: nodeDrawerWidth,
          boxSizing: 'border-box',
          border: 'none',
          p: 3,
          bgcolor: alpha(theme.palette.background.default),
        },
      })}
      anchor="right"
      variant="persistent"
      open={!!node}
      onClose={handleClose}
    >
      {!!node && (
        <>
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              mb: 2,
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

          {/* Status */}
          {node.status && (
            <>
              <Heading>Status</Heading>
              <Box
                sx={{
                  mt: 1,
                  color: statusColor(node.status),
                  display: 'flex',
                  alignItems: 'center',
                }}
              >
                {statusIcon(node.status)}
                &nbsp;
                {statusLabel(node.status)}
              </Box>
            </>
          )}

          <ErrorCard error={node.error} />

          {/* Description */}
          {node.doc && (
            <>
              <Heading>Description</Heading>
              <Typography fontSize="body2.fontSize" color='text.tertiary'>{node.doc}</Typography>
            </>
          )}
          <InputSection preview inputs={node.kwargs} />
          {/* Executor */}
          <ExecutorSection preview metadata={_.get(preview, 'lattice.metadata')} sx={(theme) => ({ bgcolor: theme.palette.background.darkblackbg })} />

          <Divider sx={{ my: 2 }} />

          {/* Source */}
          <Heading />
          <Paper elevation={0} sx={(theme) => ({ bgcolor: theme.palette.background.darkblackbg })}>
            <SyntaxHighlighter src={src} />
          </Paper>
        </>
      )}
    </Drawer>
  )
}
export default NodeDrawer
