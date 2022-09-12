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
import { useEffect, useRef, useState, useMemo, useCallback, createRef } from 'react'
import ReactFlow, { MiniMap, applyEdgeChanges, applyNodeChanges } from 'react-flow-renderer'
import ElectronNode from './ElectronNode'
import ParameterNode from './ParameterNode'
import DirectedEdge from './DirectedEdge'
import layout from './Layout'
import assignNodePositions from './LayoutElk'
import LatticeControls from './LatticeControlsElk'
import theme from '../../utils/theme'
import { statusColor } from '../../utils/misc'
import useFitViewHelper from './ReactFlowHooks'
import { useScreenshot, createFileName } from "use-react-screenshot"
import covalentLogo from '../../assets/frame.png'

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
  preview,
  hasSelectedNode,
  onClickNode,
  marginLeft = 0,
  marginRight = 0,
  setSelectedElectron,
  dispatchId
}) => {
  const { fitView } = useFitViewHelper()
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [direction, setDirection] = useState('DOWN')
  const [showMinimap, setShowMinimap] = useState(false)
  const [showParams, setShowParams] = useState(false)
  const [nodesDraggable, setNodesDraggable] = useState(false)
  const [algorithm, setAlgorithm] = useState('layered')
  const [hideLabels, setHideLabels] = useState(false)
  const [fitMarginLeft, setFitMarginLeft] = useState()
  const [fitMarginRight, setFitMarginRight] = useState()
  const [screen, setScreen] = useState(false);

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
  }, [fitView, marginLeft, marginRight, graph, direction, showParams])


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
  }, [marginRight, marginLeft,fitView])

  // layouting
  useEffect(() => {
    if (algorithm === 'oldLayout') {
      const els = layout(graph, direction, showParams, hideLabels)
      const initialNodes = els && els.filter((e) => e.type !== 'directed')
      const initialEdges = els && els.filter((e) => e.type === 'directed')
      setNodes(initialNodes)
      setEdges(initialEdges)
      setTimeout(() => fitView({ marginLeft: fitMarginLeft, marginRight: fitMarginRight, duration: 300 }), 300)
    } else {
      assignNodePositions(graph, direction, showParams, algorithm, hideLabels)
        .then((els) => {
          const initialNodes = els && els.filter((e) => e.type !== 'directed')
          const initialEdges = els && els.filter((e) => e.type === 'directed')
          setNodes(initialNodes)
          setEdges(initialEdges)
        }).then(() => fitView({ marginLeft: fitMarginLeft, marginRight: fitMarginRight, duration: 300 }))
        .catch((error) => console.log(error))
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [graph, direction, showParams, algorithm, hideLabels])

  // menu for layout
  const [anchorEl, setAnchorEl] = useState(null)
  const open = Boolean(anchorEl)
  const handleClick = (event, marginLeft, marginRight) => {
    setAnchorEl(event.currentTarget)
    setFitMarginLeft(marginLeft)
    setFitMarginRight(marginRight)
  }
  const handleOrientationChange = (direction, marginLeft, marginRight) => {
    setDirection(direction)
    setFitMarginLeft(marginLeft)
    setFitMarginRight(marginRight)
  }
  const handleClose = () => {
    setAnchorEl(null)
  }

  const handleChangeAlgorithm = (event) => {
    setAnchorEl(null);
    setAlgorithm(event);
  };

  const handleHideLabels = (marginLeft, marginRight) => {
    const value = !hideLabels
    setHideLabels(value);
    setFitMarginLeft(marginLeft)
    setFitMarginRight(marginRight)
  };

  const onNodesChange = useCallback(
    (changes) => setNodes((nds) => applyNodeChanges(changes, nds)),
    [setNodes]
  );
  const onEdgesChange = useCallback(
    (changes) => setEdges((eds) => applyEdgeChanges(changes, eds)),
    [setEdges]
  );

  /*<--------ScreenShot-------->*/

  useEffect(() => {
    if (screen) {
      takeScreenShot(ref_chart.current).then(download);
      setScreen(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [screen]);


  const ref_chart = createRef(null);

  // eslint-disable-next-line no-unused-vars
  const [image, takeScreenShot] = useScreenshot({
    type: "image/jpeg",
    quality: 1.0,
  });

  const download = (image, { name = dispatchId, extension = "jpg" } = {}) => {
    const a = document.createElement("a");
    a.href = image;
    a.download = createFileName(extension, name);
    a.click();
  };

  const nodeTypes = useMemo(() => ({ electron: ElectronNode, parameter: ParameterNode }), []);
  const edgeTypes = useMemo(() => ({ directed: DirectedEdge }), []);
  return (
    <>
      {nodes?.length > 0 && (
        <>
          <ReactFlow
            ref={ref_chart}
            nodeTypes={nodeTypes}
            edgeTypes={edgeTypes}
            data-testid="lattice__graph"
            nodesDraggable={nodesDraggable}
            nodesConnectable={false}
            nodes={nodes}
            edges={edges}
            defaultZoom={0.5}
            minZoom={0}
            maxZoom={1.5}
            fitView
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            // prevent selection when nothing is selected to prevent fitView
            selectNodesOnDrag={hasSelectedNode}
            onNodeClick={(e) => onClickNode(e)}
            onPaneClick={e => setSelectedElectron(null)}
          >
            {screen &&
              <div>
                <img style={{ position: 'absolute', zIndex: '2', right: '20px', bottom: '25px' }}
                  src={covalentLogo} alt='covalentLogo' />
              </div>
            }
          </ReactFlow>
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
            toggleScreenShot={() => {
              setScreen(true)

            }}
            open={open}
            anchorEl={anchorEl}
            handleClick={handleClick}
            handleClose={handleClose}
            direction={direction}
            setDirection={handleOrientationChange}
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
        </>
      )}
    </>
  )
}

export default LatticeGraph
