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

 import { useMemo } from 'react'
 import { zoomIdentity } from 'd3-zoom'
 import { getRectOfNodes, useStoreState, useStore } from 'react-flow-renderer'

 const DEFAULT_PADDING = 0.1

 const initialFitViewHelper = {
   fitView: ({ padding = DEFAULT_PADDING, includeHiddenNodes = false }) => {},
 }

 const getTransition = (selection, duration = 0) => {
   return selection.transition().duration(duration)
 }

 const clamp = (val, min = 0, max = 1) => Math.min(Math.max(val, min), max)

 const getTransformForBounds = (
   bounds,
   width,
   height,
   minZoom,
   maxZoom,
   padding = 0.1,
   marginLeft = 0,
   marginRight = 0
 ) => {
   width -= marginLeft + marginRight
   const xZoom = width / (bounds.width * (1 + padding))
   const yZoom = height / (bounds.height * (1 + padding))
   const zoom = Math.min(xZoom, yZoom)
   const clampedZoom = clamp(zoom, minZoom, maxZoom)
   const boundsCenterX = bounds.x + bounds.width / 2
   const boundsCenterY = bounds.y + bounds.height / 2
   const x = width / 2 - boundsCenterX * clampedZoom + marginLeft
   const y = height / 2 - boundsCenterY * clampedZoom

   return [x, y, clampedZoom]
 }

 /**
  * Customized fitView helper that supports margins.
  */
 const useFitViewHelper = () => {
   const store = useStore()
   const d3Zoom = useStoreState((s) => s.d3Zoom)
   const d3Selection = useStoreState((s) => s.d3Selection)

   const fitViewHelperFunctions = useMemo(() => {
     if (d3Selection && d3Zoom) {
       return {
         fitView: (
           options = {
             padding: DEFAULT_PADDING,
             includeHiddenNodes: false,
             duration: 0,
             marginLeft: 0,
             marginRight: 0,
           }
         ) => {
           const { nodes, width, height, minZoom, maxZoom } = store.getState()

           if (!nodes.length) {
             return
           }

           const bounds = getRectOfNodes(
             options.includeHiddenNodes
               ? nodes
               : nodes.filter((node) => !node.isHidden)
           )
           const [x, y, zoom] = getTransformForBounds(
             bounds,
             width,
             height,
             options.minZoom || minZoom,
             options.maxZoom || maxZoom,
             options.padding || DEFAULT_PADDING,
             options.marginLeft || 0,
             options.marginRight || 0
           )
           const transform = zoomIdentity.translate(x, y).scale(zoom)

           d3Zoom.transform(
             getTransition(d3Selection, options.duration),
             transform
           )
         },
         initialized: true,
       }
     }

     return initialFitViewHelper
   }, [store, d3Zoom, d3Selection])

   return fitViewHelperFunctions
 }

 export default useFitViewHelper
