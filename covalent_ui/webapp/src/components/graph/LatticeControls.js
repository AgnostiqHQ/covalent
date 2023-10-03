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

import { useZoomPanHelper } from 'react-flow-renderer'
import { ToggleButton, ToggleButtonGroup, Tooltip } from '@mui/material'
import {
  Add as PlusIcon,
  ArrowBack,
  ArrowDownward,
  ArrowForward,
  ArrowUpward,
  Fullscreen,
  LockOpenOutlined,
  LockOutlined,
  MapOutlined,
  Remove as MinusIcon,
} from '@mui/icons-material'
import useFitViewHelper from './ReactFlowHooks'


const LatticeControls = ({
   marginLeft = 0,
   marginRight = 0,
   showParams,
   toggleParams,
   showMinimap,
   toggleMinimap,
   direction,
   setDirection,
   nodesDraggable,
   toggleNodesDraggable,
 }) => {
   const { zoomIn, zoomOut } = useZoomPanHelper()
   const { fitView } = useFitViewHelper()

   return (
     <ToggleButtonGroup
       orientation="vertical"
       size="small"
       sx={{
         position: 'absolute',
         bottom: 12,
         left: 12 + marginLeft,
         zIndex: 5,
         bgcolor: 'background.paper',
         opacity: 0.7,
       }}
     >
       <Hint title="Zoom in">
         <ToggleButton value="" onClick={() => zoomIn(300)}>
           <PlusIcon />
         </ToggleButton>
       </Hint>

       <Hint title="Zoom out">
         <ToggleButton value="" onClick={() => zoomOut(300)}>
           <MinusIcon />
         </ToggleButton>
       </Hint>

       <Hint title="Fit to screen">
         <ToggleButton
           value=""
           onClick={() => {
             fitView({ duration: 300, marginLeft, marginRight })
           }}
         >
           <Fullscreen />
         </ToggleButton>
       </Hint>

       <Hint title="Toggle parameters">
         <ToggleButton onClick={toggleParams} value="" selected={showParams}>
         </ToggleButton>
       </Hint>

       <Hint title="Toggle minimap">
         <ToggleButton onClick={toggleMinimap} value="" selected={showMinimap}>
           <MapOutlined />
         </ToggleButton>
       </Hint>

       <Hint title="Change orientation">
         <ToggleButton
           onClick={() => {
             switch (direction) {
               case 'TB':
                 return setDirection('BT')
               case 'BT':
                 return setDirection('LR')
               case 'LR':
                 return setDirection('RL')
               case 'RL':
                 return setDirection('TB')
               default:
             }
           }}
           value=""
         >
           {
             {
               TB: <ArrowDownward />,
               BT: <ArrowUpward />,
               LR: <ArrowForward />,
               RL: <ArrowBack />,
             }[direction]
           }
         </ToggleButton>
       </Hint>

       <Hint title="Toggle draggable nodes">
         <ToggleButton onClick={toggleNodesDraggable} value="">
           {nodesDraggable ? <LockOpenOutlined /> : <LockOutlined />}
         </ToggleButton>
       </Hint>
     </ToggleButtonGroup>
   )
 }

 const Hint = (props) => <Tooltip arrow placement="right" {...props} />

 export default LatticeControls
