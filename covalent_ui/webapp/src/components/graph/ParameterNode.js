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
import { Typography,Tooltip,  tooltipClasses, Grid,Paper} from '@mui/material'
import { Handle } from 'react-flow-renderer'
import { styled } from '@mui/material/styles'
import {nodeLabelIcon ,truncateMiddle} from '../../utils/misc'


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
  isConnectable
}) => {
  return (
    <Grid sx={{ display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',}}>
      {!data.hideLabels?<ParameterTooltip title={_.truncate(data.executor, { length: 70 })} arrow placement="bottom-end">
     <Paper
              sx={{
                position:"absolute",
                top:-16,
                zIndex:-100,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                borderRadius: '5px 5px 0px 0px',
                minWidth: '30%',
                overflow: 'hidden',
                background: (theme) => theme.palette.background.executorBg,
                // bgcolor: !selected ? theme.palette.background.paper : '#1B2632',
                color: (theme) => theme.palette.text.tertiary,
                borderColor: (theme) => theme.palette.primary.highlightBlue,
                borderStyle: 'solid',
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
     </ParameterTooltip>:null}

    <ParameterTooltip title={ data.hideLabels ? (
              <>
                <Typography color="inherit">name : {data.fullName}</Typography>
                <Typography color="inherit">
                  executor : {data.executor}
                </Typography>
                <Typography color="inherit">
                  node_id : {data.node_id}
                </Typography>
              </>
            ) : (
              data.fullName
            )} arrow placement="bottom-end">
      <Grid   sx={(theme) => ({
       px: 1,
       borderRadius: '100px',
       color: 'text.disabled',
       bgcolor: theme.palette.background.paper,
       fontSize: 12,
       display:'flex',
       alignItems:'center',
       justifyItems:'space-between',
     })}>
     { nodeLabelIcon(data.nodeType)}
     <Handle
       type="source"
       position={sourcePosition}
       isConnectable={isConnectable}
     />
    <Typography
     component="div"

   >
     {data.label}
     <Handle
       type="source"
       position={sourcePosition}
       isConnectable={isConnectable}
     />
   </Typography>
      </Grid>
   </ParameterTooltip>
   {!data.hideLabels? <ParameterTooltip title={_.truncate(data.node_id, { length: 70 })} arrow placement="bottom-end">
   <Paper
              sx={{
                position: 'absolute',
                top: data.preview?20:34,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                borderRadius: '16px',
                minWidth: '20%',
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
   </ParameterTooltip>:null}

    </Grid>


  )
}

export default ParameterNode
