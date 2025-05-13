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
import { useEffect, useState, createRef, memo, useMemo, useCallback } from 'react'
import { useScreenshot, createFileName } from 'use-react-screenshot'
import {
  ReactFlow,
  MiniMap,
  useReactFlow,
  applyEdgeChanges,
  applyNodeChanges,
} from '@xyflow/react'
import { NODE_TEXT_COLOR, ElectronNode } from './ElectronNode'
import ParameterNode from './ParameterNode'
import DirectedEdge from './DirectedEdge'
import assignNodePositions from './LayoutElk'
import LatticeControls from './LatticeControlsElk'
import theme from '../../utils/theme'
import { statusColor } from '../../utils/misc'
import covalentLogo from '../../assets/frame.png'

function shouldUnselectNodes(hasSelectedNode, flowNodes) {
  if (hasSelectedNode) {
    return false;
  }
  const selected = flowNodes.filter((n) => n.selected === true)
  return selected.length > 0;
}

function onInit(reactFlowInstance) {
  reactFlowInstance.fitView();
}

const LatticeGraph = ({
  togglePrettify,
  prettify,
  graph,
  preview,
  hasSelectedNode,
  marginLeft = 0,
  marginRight = 0,
  dispatchId,
  handleNodeSelectionChange,
}) => {
  const { fitView } = useReactFlow()
  const [nodes, setNodes] = useState([])
  const [edges, setEdges] = useState([])
  const [direction, setDirection] = useState('DOWN')
  const [showMinimap, setShowMinimap] = useState(false)
  const [showParams, setShowParams] = useState(false)
  const [showPostProcess, setPostProcess] = useState(false)
  const [nodesDraggable, setNodesDraggable] = useState(false)
  const [algorithm, setAlgorithm] = useState('layered')
  const [hideLabels, setHideLabels] = useState(false)
  const [screen, setScreen] = useState(false)

  const nodeMap = new Map((graph?.nodes ?? []).map((node) => [node.name, node]))

  const searchName = ':postprocess:'
  const searchStatus = 'FAILED'
  const desiredNode = nodeMap.get(searchName)

  const handleNodesChange = useCallback(
    (changes) => {
      setNodes((nds) => applyNodeChanges(changes, nds));
      const selectedNodes = changes.filter((c) => c.type === 'select').filter((c) => c.selected === true);
      handleNodeSelectionChange(selectedNodes);
    },
    [setNodes, handleNodeSelectionChange],
  )
  const handleEdgesChange = useCallback(
    (changes) => setEdges((eds) => applyEdgeChanges(changes, eds)),
    [setEdges],
  )

  // Unselect all nodes when NodeDrawer is closed
  if (shouldUnselectNodes(hasSelectedNode, nodes)) {
    setNodes(
      (nds) => nds.map(
        (elem) => ({...elem, selected: false})
      )
    );
  }

  useEffect(() => {
    if (desiredNode && desiredNode.status === searchStatus) {
      setPostProcess(true)
    }

    // setPostProcess(
    // 	!!graph?.nodes?.find(
    // 		obj => obj.name.startsWith(':postprocess:') && obj.status === 'NEW_OBJECT'
    // 	)
    // );
  }, [graph, desiredNode])


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
  }, [marginRight, marginLeft, fitView, nodes, edges, graph])

  // layouting
  useEffect(() => {
    assignNodePositions(
      graph,
      direction,
      showParams,
      algorithm,
      hideLabels,
      preview,
      showPostProcess,
      prettify
    )
      .then((els) => {
        setNodes(els.nodes);
        setEdges(els.edges);
      })
      .catch((error) => console.log(error))
      // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [
    graph,
    direction,
    showParams,
    algorithm,
    hideLabels,
    showPostProcess,
    prettify,
  ])

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
    setAnchorEl(null)
    setAlgorithm(event)
  }

  const handleHideLabels = () => {
    const value = !hideLabels
    setHideLabels(value)
  }

  /*<--------ScreenShot-------->*/

  useEffect(() => {
    if (screen) {
      var svgElements = ref_chart.current.querySelectorAll('svg')
      svgElements.forEach(function (item) {
        item.style.marginBottom = '14px'
      })
      takeScreenShot(ref_chart.current).then(download)
      svgElements.forEach(function (item) {
        item.style.marginBottom = '0px'
      })
      setScreen(false)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [screen])

  const ref_chart = createRef(null)

  // eslint-disable-next-line no-unused-vars
  const [image, takeScreenShot] = useScreenshot({
    type: 'image/jpeg',
    quality: 1.0,
  })

  const download = (image, { name = dispatchId, extension = 'jpg' } = {}) => {
    const a = document.createElement('a')
    a.href = image
    a.download = createFileName(extension, name)
    a.click()
  }

  useEffect(() => {
    if (!hasSelectedNode) resetNodeStyles()
  }, [hasSelectedNode])

  const resetNodeStyles = () => {
    setEdges((eds) => eds.map(
      (elem) => ({
        ...elem,
        animated: false,
        labelsStyle: { fill: NODE_TEXT_COLOR },
        style: {
          ...elem.style,
          stroke: '#303067',
        },
      })
    ))
  }

  const nodeTypes = useMemo(
    () => ({ electron: ElectronNode, parameter: ParameterNode }),
    []
  )
  const edgeTypes = useMemo(() => ({ directed: DirectedEdge }), [])


  const defaultViewport = { zoom: 0.5 }

  return (
    <>
      {nodes?.length > 0 && (
        <>
          <ReactFlow
            ref={ref_chart}
            data-testid="lattice__graph"
            nodeTypes={nodeTypes}
            edgeTypes={edgeTypes}
            nodesDraggable={nodesDraggable}
            nodesConnectable={false}
            nodes={nodes}
            edges={edges}
            onNodesChange={handleNodesChange}
            onEdgesChange={handleEdgesChange}
            onInit={onInit}
            defaultViewport={defaultViewport}
            minZoom={0}
            maxZoom={1.5}
            selectNodesOnDrag={hasSelectedNode}
            onPaneClick={() => {
              resetNodeStyles()
            }}
          >
            {screen && (
              <div>
                <img
                  style={{
                    position: 'absolute',
                    zIndex: '2',
                    paddingLeft: '25px',
                    bottom: '25px',
                  }}
                  src={covalentLogo}
                  alt="covalentLogo"
                />
              </div>
            )}
          </ReactFlow>
          <LatticeControls
            marginLeft={marginLeft}
            marginRight={marginRight}
            showPostProcess={showPostProcess}
            togglePostProcess={() => {
              setPostProcess(!showPostProcess)
            }}
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
            togglePrettify={togglePrettify}
            prettify={prettify}
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
                left: 522,
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

export default memo(LatticeGraph)
