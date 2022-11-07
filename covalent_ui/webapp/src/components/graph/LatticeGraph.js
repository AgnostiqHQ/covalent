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
import { useEffect, useRef, useState, createRef } from 'react'
import { useScreenshot, createFileName } from 'use-react-screenshot'
import ReactFlow, {
  MiniMap,
  getIncomers,
  getOutgoers,
  isEdge,
} from 'react-flow-renderer'
import { NODE_TEXT_COLOR, ElectronNode } from './ElectronNode'
import ParameterNode from './ParameterNode'
import DirectedEdge from './DirectedEdge'
import layout from './Layout'
import assignNodePositions from './LayoutElk'
import LatticeControls from './LatticeControlsElk'
import theme from '../../utils/theme'
import { statusColor } from '../../utils/misc'
import useFitViewHelper from './ReactFlowHooks'
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
  marginLeft = 0,
  marginRight = 0,
  dispatchId,
}) => {
  const { fitView } = useFitViewHelper()
  const [elements, setElements] = useState([])
  const [direction, setDirection] = useState('DOWN')
  const [showMinimap, setShowMinimap] = useState(false)
  const [showParams, setShowParams] = useState(false)
  const [nodesDraggable, setNodesDraggable] = useState(false)
  const [algorithm, setAlgorithm] = useState('layered')
  const [hideLabels, setHideLabels] = useState(false)
  const [screen, setScreen] = useState(false)
  const [highlighted, setHighlighted] = useState(false)

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
    if (!highlighted) marginSet()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [fitView, marginLeft, marginRight, graph, elements, highlighted])

  useEffect(() => {
    setHighlighted(false)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [direction, showParams, algorithm, hideLabels, graph])

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
  }, [marginRight, marginLeft, fitView, elements, graph])

  // layouting
  useEffect(() => {
    if (algorithm === 'oldLayout') {
      setElements(layout(graph, direction, showParams, hideLabels, preview))
    } else {
      assignNodePositions(
        graph,
        direction,
        showParams,
        algorithm,
        hideLabels,
        preview
      )
        .then((els) => {
          setElements(els)
        })
        .catch((error) => console.log(error))
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [graph, direction, showParams, algorithm, hideLabels])

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

  // highlight links of selected nodes
  const getAllIncomers = (node, elements) => {
    return getIncomers(node, elements).reduce(
      (memo, incomer) => [
        ...memo,
        incomer,
        ...getAllIncomers(incomer, elements),
      ],
      []
    )
  }

  const getAllOutgoers = (node, elements) => {
    return getOutgoers(node, elements).reduce(
      (memo, outgoer) => [
        ...memo,
        outgoer,
        ...getAllOutgoers(outgoer, elements),
      ],
      []
    )
  }

  const highlightPath = (node, elements, selection) => {
    if (node && elements) {
      const allIncomers = getAllIncomers(node, elements)
      const allOutgoers = getAllOutgoers(node, elements)
      setHighlighted(true)
      setElements((prevElements) => {
        return prevElements?.map((elem) => {
          const incomerIds = allIncomers.map((i) => i.id)
          const outgoerIds = allOutgoers.map((o) => o.id)
          if (isEdge(elem)) {
            if (selection) {
              const animated =
                (outgoerIds.includes(elem.target) &&
                  (outgoerIds.includes(elem.source) ||
                    node.id === elem.source)) ||
                (incomerIds.includes(elem.source) &&
                  (incomerIds.includes(elem.target) || node.id === elem.target))
              elem.style = {
                ...elem.style,
                stroke: animated ? '#6473FF' : '#303067',
              }
              elem.labelStyle = animated
                ? { fill: '#6473FF' }
                : { fill: NODE_TEXT_COLOR }
            } else {
              elem.animated = false
              elem.style = {
                ...elem.style,
                stroke: '#303067',
              }
            }
          }

          return elem
        })
      })
    }
  }

  useEffect(() => {
    if (!hasSelectedNode) resetNodeStyles()
  }, [hasSelectedNode])

  const resetNodeStyles = () => {
    setElements((prevElements) => {
      return prevElements?.map((elem) => {
        if (isEdge(elem)) {
          elem.animated = false
          elem.labelStyle = { fill: NODE_TEXT_COLOR }
          elem.style = {
            ...elem.style,
            stroke: '#303067',
          }
        }
        return elem
      })
    })
  }

  return (
    <>
      {elements?.length > 0 && (
        <>
          <ReactFlow
            ref={ref_chart}
            data-testid="lattice__graph"
            nodeTypes={{ electron: ElectronNode, parameter: ParameterNode }}
            edgeTypes={{ directed: DirectedEdge }}
            nodesDraggable={nodesDraggable}
            nodesConnectable={false}
            elements={elements}
            defaultZoom={0.5}
            minZoom={0}
            maxZoom={1.5}
            onSelectionChange={(selectedElements) => {
              const node = selectedElements?.[0]
              highlightPath(node, elements, true)
            }}
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

export default LatticeGraph
