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
import { Typography,Tooltip,  tooltipClasses} from '@mui/material'
import { Handle } from 'react-flow-renderer'
import { styled } from '@mui/material/styles'

const ParameterTooltip = styled(({ className, ...props }) => (
  <Tooltip {...props} classes={{ popper: className }} />
))(() => ({
  [`& .${tooltipClasses.tooltip}`]: {
    // customize tooltip
  },
}))

const ParameterNode = ({
  id,
  data,
  type,
  selected,
  sourcePosition,
  targetPosition,
  isConnectable
}) => {
  return (
    <ParameterTooltip title={_.truncate(data.fullName, { length: 70 })} arrow placement="bottom-end">
     <Typography
      component="div"
      sx={(theme) => ({
        px: 2,
        py: 0.5,
        borderRadius: 3,
        color: 'text.disabled',
        bgcolor: theme.palette.background.paper,
        fontSize: 12,
      })}
    >
      {data.label}
      <Handle
        type="source"
        position={sourcePosition}
        isConnectable={isConnectable}
      />
    </Typography>
    </ParameterTooltip>

  )
}

export default ParameterNode
