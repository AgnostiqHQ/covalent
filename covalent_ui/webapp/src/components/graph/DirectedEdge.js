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

import { BezierEdge } from 'react-flow-renderer'

import theme from '../../utils/theme'
import { NODE_TEXT_COLOR } from './ElectronNode'

const DirectedEdge = (props) => {
  return (
    <BezierEdge
      {...props}
      style={props?.style ? props?.style : {
        stroke: theme.palette.background.coveBlack02,
      }}
      labelBgPadding={[8, 4]}
      labelBgBorderRadius={0}
      labelBgStyle={props?.labelBgStyle ? props?.labelBgStyle : { fill: theme.palette.background.default, color: '#fff', fillOpacity: 1 }}
      labelStyle={{ fill: NODE_TEXT_COLOR }}
    />
  )
}

export default DirectedEdge
