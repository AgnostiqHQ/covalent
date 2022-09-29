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

import { Grid, Paper, Tooltip, tooltipClasses, Typography } from '@mui/material'
import { styled } from '@mui/material/styles'
import { Handle } from 'react-flow-renderer'
import CopyButton from '../common/CopyButton'
import { truncateMiddle, nodeLabelIcon, statusIcon } from '../../utils/misc'

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
        {!data.hideLabels && data.executor ? (
          <ElectronTooltip title={data.executor} arrow placement="bottom-end">
            <Paper
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                borderRadius: '5px 5px 0px 0px',
                minWidth: '30%',
                overflow: 'hidden',
                // bgcolor: !selected ? theme.palette.background.paper : '#1B2632',
                borderColor: (theme) => theme.palette.primary.highlightBlue,
                borderStyle: 'solid',
                borderWidth: hasBorder ? 1 : 0,
                color: (theme) =>
                  !selected
                    ? theme.palette.text.tertiary
                    : theme.palette.text.primary,
                '&:hover': {
                  color: (theme) => theme.palette.text.primary,
                },
              }}
            >
              <Handle
                type="target"
                position={targetPosition}
                isConnectable={isConnectable}
              />
              <Typography sx={{ fontSize: '0.625rem' }}>
                {truncateMiddle(data.executor, 6, 0)}
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
                <Typography sx={{ fontSize: '0.75rem' }} color="inherit">
                  name : {data.fullName}
                </Typography>
                <Typography sx={{ fontSize: '0.75rem' }} color="inherit">
                  executor : {data.executor}
                </Typography>
                <Typography sx={{ fontSize: '0.75rem' }} color="inherit">
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
            data-testid="electronNode"
            elevation={!selected ? 1 : 5}
            sx={{
              height: '34px',
              display: 'flex',
              alignItems: 'center',
              px: 1,
              py: 0.5,
              borderRadius: '100px',
              bgcolor: !selected
                ? (theme) => theme.palette.background.paper
                : (theme) => theme.palette.primary.dark,
              color: !selected ? NODE_TEXT_COLOR : '#FAFAFA',
              borderColor: !selected
                ? (theme) => theme.palette.primary.highlightBlue
                : (theme) => theme.palette.background.paper,
              borderStyle: 'solid',
              borderWidth: hasBorder ? 1 : 0,
              '&:hover': {
                bgcolor: (theme) => theme.palette.background.coveBlack02,
                color: (theme) => theme.palette.primary.white,
              },
            }}
          >
            <Handle
              type="target"
              position={targetPosition}
              isConnectable={isConnectable}
              data-testid="handleelectronNode"
            />
            {nodeLabelIcon(data.nodeType)}
            {statusIcon(data.status)}
            <Typography sx={{ fontSize: 14, mb: 0.3 }}>{data.label}</Typography>
            <Handle
              data-testid="sourcehandleelectronNode"
              type="source"
              position={sourcePosition}
              isConnectable={isConnectable}
            />
            {data.nodeType === 'sublattice' && (
              <CopyButton
                sx={{ ml: 1, color: 'text.tertiary' }}
                fontSize="10"
                content={data.sublattices_id}
                size="small"
                className="copy-btn"
                title="Copy ID"
                width={17}
                height={17}
                isBorderPresent={true}
                borderRadius="4px"
              />
            )}
          </Paper>
        </ElectronTooltip>
        {!data.hideLabels ? (
          <ElectronTooltip title={data.node_id} arrow placement="bottom-end">
            <Paper
              elevation={!selected ? 1 : 5}
              sx={{
                position: 'absolute',
                top: data.executor ? 48 : 30,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                borderRadius: '16px',
                minWidth: '20%',
                // bgcolor: !selected ? theme.palette.background.paper : '#1B2632',
                color: (theme) =>
                  !selected
                    ? theme.palette.text.tertiary
                    : theme.palette.text.primary,

                '&:hover': {
                  color: (theme) => theme.palette.text.primary,
                },
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
