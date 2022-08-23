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
  Grid,
  Paper,
  SvgIcon,
  Tooltip,
  tooltipClasses,
  Typography,
} from '@mui/material'
import { styled } from '@mui/material/styles'
import { Handle } from 'react-flow-renderer'

import { ReactComponent as AtomSvg } from '../../assets/status/activity.svg'
import { ReactComponent as CheckSvg } from '../../assets/status/checkmark.svg'
import { ReactComponent as ErrorSvg } from '../../assets/status/error.svg'
import { ReactComponent as CancelSvg } from '../../assets/status/stop.svg'
import { statusColor, truncateMiddle } from '../../utils/misc'
import { ReactComponent as LoaderSvg } from '../../assets/loader.svg'

export const NODE_TEXT_COLOR = 'rgba(250, 250, 250, 0.6)'

const ElectronTooltip = styled(({ className, ...props }) => (
  <Tooltip {...props} classes={{ popper: className }} />
))(() => ({
  [`& .${tooltipClasses.tooltip}`]: {
    // customize tooltip
    maxWidth: 500,
  },
}))

const ElectronNode = ({
  data,
  selected,
  sourcePosition,
  targetPosition,
  isConnectable,
}) => {
  const color = statusColor(data.status)
  const hasBorder = data.status !== 'NEW_OBJECT'
  return (
    <>
      <Grid
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        {' '}
        {!data.hideLabels ? (
          <ElectronTooltip title={data.executor} arrow placement="bottom-end">
            <Paper
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                borderRadius: '5px 5px 0px 0px',
                width: '50%',
                overflow: 'hidden',
                background: (theme) => theme.palette.background.executorBg,
                // bgcolor: !selected ? theme.palette.background.paper : '#1B2632',
                color: (theme) => theme.palette.text.tertiary,
                borderColor: (theme) => theme.palette.primary.highlightBlue,
                borderStyle: 'solid',
                borderWidth: hasBorder ? 1 : 0,
              }}
            >
              <Handle
                type="target"
                position={targetPosition}
                isConnectable={isConnectable}
              />
              <Typography sx={{ fontSize: '0.625rem' }}>
                {truncateMiddle(data.executor, 6,0)}
              </Typography>
              <Handle
                type="source"
                position={sourcePosition}
                isConnectable={isConnectable}
              />
            </Paper>
          </ElectronTooltip>
        ) : null}
        <ElectronTooltip
          title={
            data.hideLabels ? (
              <>
                <Typography color="inherit">name : {data.fullName}</Typography>
                <Typography color="inherit">
                  executor_label : {data.executor}
                </Typography>
                <Typography color="inherit">
                  node_id : {data.node_id}
                </Typography>
              </>
            ) : (
              data.fullName
            )
          }
          arrow
          placement="bottom-end"
        >
          <Paper
            elevation={!selected ? 1 : 5}
            sx={{
              display: 'flex',
              alignItems: 'center',
              px: 1,
              py: 0.5,
              borderRadius: '16px',
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
                    <SvgIcon
                      sx={{ mt: 0.5, mr: 0.5, fontSize: 14, fill: color }}
                    >
                      <AtomSvg />
                    </SvgIcon>
                  )
                case 'RUNNING':
                  return (
                    <SvgIcon
                      sx={{ mt: 0.1, mr: 0.5, fontSize: 10, fill: color }}
                    >
                      <LoaderSvg />
                    </SvgIcon>
                  )
                case 'COMPLETED':
                  return (
                    <SvgIcon
                      sx={{ mr: 0.1, fontSize: 14, fill: color, mt: 0.6 }}
                    >
                      <CheckSvg />
                    </SvgIcon>
                  )
                case 'FAILED':
                  return (
                    <SvgIcon sx={{ mt: 0.8, fontSize: 14, fill: color }}>
                      <ErrorSvg />
                    </SvgIcon>
                  )
                case 'CANCELLED':
                  return (
                    <SvgIcon sx={{ mt: 0.8, fontSize: 14, fill: color }}>
                      <CancelSvg />
                    </SvgIcon>
                  )
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
        {!data.hideLabels ? (
          <ElectronTooltip title={data.node_id} arrow placement="bottom-end">
            <Paper
              elevation={!selected ? 1 : 5}
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                borderRadius: '16px',
                width: '25%',
                // bgcolor: !selected ? theme.palette.background.paper : '#1B2632',
                color: (theme) => theme.palette.text.tertiary,
              }}
            >
              <Handle
                type="target"
                position={targetPosition}
                isConnectable={isConnectable}
              />
              <Typography sx={{ fontSize: '0.625rem' }}>
                {data.node_id}
              </Typography>
              <Handle
                type="source"
                position={sourcePosition}
                isConnectable={isConnectable}
              />
            </Paper>
          </ElectronTooltip>
        ) : null}
      </Grid>
    </>
  )
}

export default ElectronNode
