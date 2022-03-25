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

import {
  Paper,
  SvgIcon,
  Tooltip,
  tooltipClasses,
  Typography,
} from '@mui/material'
import { styled } from '@mui/material/styles'
import { Handle } from 'react-flow-renderer'

import { ReactComponent as AtomSvg } from '../../assets/atom.svg'
import { statusColor } from '../../utils/misc'
import { Check, WarningAmber } from '@mui/icons-material'

export const NODE_TEXT_COLOR = 'rgba(250, 250, 250, 0.6)'

const ElectronTooltip = styled(({ className, ...props }) => (
  <Tooltip {...props} classes={{ popper: className }} />
))(({ theme }) => ({
  [`& .${tooltipClasses.tooltip}`]: {
    // customize tooltip
  },
}))

const ElectronNode = ({
  id,
  data,
  type,
  selected,
  sourcePosition,
  targetPosition,
  isConnectable,
}) => {
  const color = statusColor(data.status)
  const hasBorder = data.status !== 'NEW_OBJECT'

  return (
    <ElectronTooltip title={data.fullName} arrow placement="bottom-end">
      <Paper
        elevation={!selected ? 1 : 5}
        sx={{
          display: 'flex',
          alignItems: 'center',
          px: 1,
          py: 0.5,
          borderRadius: 1,
          // bgcolor: !selected ? theme.palette.background.paper : '#1B2632',
          color: !selected ? NODE_TEXT_COLOR : '#FAFAFA',
          borderColor: color,
          borderStyle: 'solid',
          borderWidth: hasBorder ? 1 : 0,
        }}
      >
        <Handle
          type="target"
          position={targetPosition}
          isConnectable={isConnectable}
        />
        {(() => {
          switch (data.status) {
            case 'NEW_OBJECT':
              return (
                <SvgIcon sx={{ mr: 1, fontSize: 12, fill: color }}>
                  <AtomSvg />
                </SvgIcon>
              )
            case 'RUNNING':
              return (
                <SvgIcon
                  sx={{ mr: 1, fontSize: 12, fill: color }}
                  className="spin-electron"
                >
                  <AtomSvg />
                </SvgIcon>
              )
            case 'COMPLETED':
              return <Check sx={{ mr: 1, fontSize: 12, fill: color }} />
            case 'FAILED':
              return <WarningAmber sx={{ mr: 1, fontSize: 12, color: color }} />
            default:
              return null
          }
        })()}

        <Typography sx={{ fontSize: 12 }}>{data.label}</Typography>
        <Handle
          type="source"
          position={sourcePosition}
          isConnectable={isConnectable}
        />
      </Paper>
    </ElectronTooltip>
  )
}

export default ElectronNode
