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
