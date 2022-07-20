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
import { useEffect, useRef, useState } from 'react'
import ReactFlow, { MiniMap } from 'react-flow-renderer'
import ElectronNode from './ElectronNode'
import ParameterNode from './ParameterNode'
import DirectedEdge from './DirectedEdge'
import layout from './Layout'
import assignNodePositions from './LayoutElk'
import LatticeControls from './LatticeControlsElk'
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
  marginRight = 0
}) => {
  const { fitView } = useFitViewHelper()

  const [elements, setElements] = useState([])
  const [direction, setDirection] = useState('DOWN')
  const [showMinimap, setShowMinimap] = useState(false)
  const [showParams, setShowParams] = useState(false)
  const [nodesDraggable, setNodesDraggable] = useState(false)
  const [algorithm, setAlgorithm] = useState('layered')
  const [hideLabels, setHideLabels] = useState(false)

  // set Margin
  const prevMarginRight = usePrevious(marginRight)

  const marginSet = () => {
    setTimeout(() => {
      const animate =
        prevMarginRight !== undefined && prevMarginRight !== marginRight
      fitView({
        marginLeft,
        marginRight,
        ...(animate ? { duration: 250 } : null),
      })
    })
  }

  useEffect(() => {
    marginSet()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [fitView, marginLeft, marginRight, graph, direction, elements, showParams])

  // handle resizing
  const resizing = () => {
    const resizeHandler = () =>
      fitView({ duration: 250, marginLeft, marginRight })
    window.addEventListener('resize', resizeHandler)
    return () => {
      window.removeEventListener('resize', resizeHandler)
    }
  }
  useEffect(() => {
    resizing()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [marginRight, marginLeft, fitView, elements])

  // layouting
  useEffect(() => {
    if (algorithm === 'oldLayout') {
      setElements(layout(graph, direction, showParams,hideLabels))
    } else {
      assignNodePositions(graph, direction, showParams, algorithm,hideLabels)
        .then((els) => {
          setElements(els)
        })
        .catch((error) => console.log(error))
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [graph, direction, showParams, algorithm,hideLabels])

  // menu for layout
  const [anchorEl, setAnchorEl] = useState(null)
  const open = Boolean(anchorEl)
  const handleClick = (event) => {
    setAnchorEl(event.currentTarget)
  }
  const handleClose = () => {
    setAnchorEl(null)
  }

  const handleChangeAlgorithm = (event) => {
    setAnchorEl(null);
    setAlgorithm(event);
  };

  const handleHideLabels = () => {
    const value= !hideLabels
    setHideLabels(value);
  };


  return (
    <>
      {elements?.length > 0 && (
        <ReactFlow
          nodeTypes={{ electron: ElectronNode, parameter: ParameterNode }}
          edgeTypes={{ directed: DirectedEdge }}
          nodesDraggable={nodesDraggable}
          nodesConnectable={false}
          elements={elements}
          defaultZoom={1}
          minZoom={0}
          maxZoom={3}
          // prevent selection when nothing is selected to prevent fitView
          selectNodesOnDrag={hasSelectedNode}
        >
          {/* <Background
         variant="dots"
         color={lighten(theme.palette.background.paper, 0.05)}
         gap={12}
         size={1}
       /> */}

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
            open={open}
            anchorEl={anchorEl}
            handleClick={handleClick}
            handleClose={handleClose}
            direction={direction}
            setDirection={setDirection}
            algorithm={algorithm}
            handleHideLabels={handleHideLabels}
            hideLabels={hideLabels}
            handleChangeAlgorithm={handleChangeAlgorithm}
            nodesDraggable={nodesDraggable}
            toggleNodesDraggable={() => setNodesDraggable(!nodesDraggable)}
          />
          {showMinimap && (
            <MiniMap
              style={{
                backgroundColor: theme.palette.background.default,
                position: 'absolute',
                bottom: 12,
                left: 513,
                zIndex: 5,
                height: 150,
                width: 300,
              }}
              maskColor={theme.palette.background.paper}
              nodeColor={(node) => statusColor(node.data.status)}
            />
          )}
        </ReactFlow>
      )}
    </>
  )
}

export default LatticeGraph
