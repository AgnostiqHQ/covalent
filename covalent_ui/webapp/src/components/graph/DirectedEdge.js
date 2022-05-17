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

import theme, { graphBgColor } from '../../utils/theme'

const DirectedEdge = (props) => {
  return (
    <BezierEdge
      {...props}
      style={{
        strokeWidth: 2,
        stroke: theme.palette.background.coveBlack02,
      }}
      labelBgStyle={{ fill: graphBgColor }}
      labelStyle={{
        fill: theme.palette.text.tertiary,
        fontSize: '10',
      }}
      arrowHeadType="arrow"
    />
  )
}

export default DirectedEdge
