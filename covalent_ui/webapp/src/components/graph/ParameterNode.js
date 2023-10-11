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

import _ from 'lodash'
import { Typography, Tooltip, tooltipClasses, Grid, Paper } from '@mui/material'
import { Handle } from 'react-flow-renderer'
import { styled } from '@mui/material/styles'
import { nodeLabelIcon, truncateMiddle } from '../../utils/misc'

const ParameterTooltip = styled(({ className, ...props }) => (
  <Tooltip {...props} classes={{ popper: className }} />
))(() => ({
  [`& .${tooltipClasses.tooltip}`]: {
    // customize tooltip
  },
}))

const ParameterNode = ({
  data,
  sourcePosition,
  targetPosition,
  isConnectable,
}) => {
  return (
    <Grid
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      {!data.hideLabels && data.executor ? (
        <ParameterTooltip
          title={_.truncate(data.executor, { length: 70 })}
          arrow
          placement="bottom-end"
        >
          <Paper
            sx={{
              position: 'absolute',
              top: -15,
              zIndex: -100,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              borderRadius: '5px 5px 0px 0px',
              minWidth: '30%',
              overflow: 'hidden',
              color: (theme) => theme.palette.text.tertiary,
              cursor: 'default',
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
              {truncateMiddle(data.executor, 4, 0)}
            </Typography>
            <Handle
              type="source"
              position={sourcePosition}
              isConnectable={isConnectable}
            />
          </Paper>
        </ParameterTooltip>
      ) : null}

      <ParameterTooltip
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
          sx={(theme) => ({
            px: 1,
            py: 0,
            borderRadius: '100px',
            color: 'text.disabled',
            bgcolor: theme.palette.background.paper,
            fontSize: 12,
            display: 'flex',
            alignItems: 'center',
            justifyItems: 'space-between',
            cursor: 'default',
            '&:hover': {
              bgcolor: theme.palette.background.coveBlack02,
              color: theme.palette.primary.white,
            },
          })}
        >
          <Grid sx={{ height: '36px' }}>{nodeLabelIcon(data.nodeType)}</Grid>
          <Handle
            type="source"
            position={sourcePosition}
            isConnectable={isConnectable}
          />
          <Typography component="div" data-testid="para__typo">
            {data.label}
            <Handle
              data-testid="parameternode"
              type="source"
              position={sourcePosition}
              isConnectable={isConnectable}
            />
          </Typography>
        </Paper>
      </ParameterTooltip>
      {!data.hideLabels ? (
        <ParameterTooltip
          title={_.truncate(data.node_id, { length: 70 })}
          arrow
          placement="bottom-end"
        >
          <Paper
            sx={{
              position: 'absolute',
              top: 31,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              borderRadius: '16px',
              minWidth: '20%',
              bgcolor: (theme) => theme.palette.background.paper,

              // bgcolor: !selected ? theme.palette.background.paper : '#1B2632',
              color: (theme) => theme.palette.text.tertiary,
              cursor: 'default',
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
        </ParameterTooltip>
      ) : null}
    </Grid>
  )
}

export default ParameterNode
