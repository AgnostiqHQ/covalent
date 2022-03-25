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
import { useEffect, useRef, useState } from 'react'
import ReactFlow, { Background, MiniMap } from 'react-flow-renderer'
import { lighten } from '@mui/material'

import ElectronNode from './ElectronNode'
import ParameterNode from './ParameterNode'
import DirectedEdge from './DirectedEdge'
import layout from './Layout'
import LatticeControls from './LatticeControls'
import theme from '../../utils/theme'
import { statusColor } from '../../utils/misc'
import useFitViewHelper from './ReactFlowHooks'

// https://reactjs.org/docs/hooks-faq.html#how-to-get-the-previous-props-or-state
function usePrevious(value) {
  const ref = useRef()
  useEffect(() => {
    ref.current = value
  })
  return ref.current
}

const LatticeGraph = ({
  graph,
  hasSelectedNode,
  marginLeft = 0,
  marginRight = 0,
}) => {
  const { fitView } = useFitViewHelper()

  const [elements, setElements] = useState()
  const [direction, setDirection] = useState('TB')
  const [showMinimap, setShowMinimap] = useState(false)
  const [showParams, setShowParams] = useState(false)
  const [nodesDraggable, setNodesDraggable] = useState(false)

  useEffect(() => {
    setElements(layout(graph, direction, showParams))
  }, [graph, direction, showParams])

  const prevMarginRight = usePrevious(marginRight)
  useEffect(() => {
    setTimeout(() => {
      const animate =
        prevMarginRight !== undefined && prevMarginRight !== marginRight
      fitView({
        marginLeft,
        marginRight,
        ...(animate ? { duration: 300 } : null),
      })
    })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [fitView, marginLeft, marginRight, graph, direction, showParams])

  // handle resizing
  useEffect(() => {
    const resizeHandler = _.debounce(
      () => fitView({ duration: 250, marginLeft, marginRight }),
      50
    )
    window.addEventListener('resize', resizeHandler)
    return () => {
      window.removeEventListener('resize', resizeHandler)
    }
  }, [marginRight, marginLeft, fitView])

  return (
    <>
      <ReactFlow
        nodeTypes={{ electron: ElectronNode, parameter: ParameterNode }}
        edgeTypes={{ directed: DirectedEdge }}
        nodesDraggable={nodesDraggable}
        nodesConnectable={false}
        elements={elements}
        // prevent selection when nothing is selected to prevent fitView
        selectNodesOnDrag={hasSelectedNode}
      >
        <Background
          variant="dots"
          color={lighten(theme.palette.background.paper, 0.05)}
          gap={12}
          size={1}
        />

        <LatticeControls
          marginLeft={marginLeft}
          marginRight={marginRight}
          showParams={showParams}
          toggleParams={() => {
            setShowParams(!showParams)
          }}
          showMinimap={showMinimap}
          toggleMinimap={() => {
            setShowMinimap(!showMinimap)
          }}
          direction={direction}
          setDirection={setDirection}
          nodesDraggable={nodesDraggable}
          toggleNodesDraggable={() => setNodesDraggable(!nodesDraggable)}
        />
        {showMinimap && (
          <MiniMap
            style={{ backgroundColor: theme.palette.background.default }}
            maskColor={theme.palette.background.paper}
            nodeColor={(node) => statusColor(node.data.status)}
          />
        )}
      </ReactFlow>
    </>
  )
}

export default LatticeGraph
