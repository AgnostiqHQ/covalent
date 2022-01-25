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
import { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useParams } from 'react-router-dom'
import ReactFlow, { Controls, MiniMap } from 'react-flow-renderer'
import { Helmet } from 'react-helmet-async'
import {
  Box,
  Divider,
  ToggleButton,
  ToggleButtonGroup,
  Toolbar,
  Paper,
  Breadcrumbs,
  Link,
  Typography,
  IconButton,
} from '@mui/material'
import {
  ArrowBack,
  ArrowDownward,
  ArrowForward,
  ArrowUpward,
  Map as MapIcon,
  Refresh,
} from '@mui/icons-material'

import NodeInfo from './NodeInfo'
import ElectronNode from './graph/ElectronNode'
import ParameterNode from './graph/ParameterNode'
import layout from './graph/Layout'
import CopyButton from './CopyButton'
import { fetchResult } from '../redux/resultsSlice'

const Result = () => {
  const { dispatchId } = useParams()
  const result = useSelector((state) => state.results.cache[dispatchId])

  const [elements, setElements] = useState()
  const [direction, setDirection] = useState('TB')
  const [showMinimap, setShowMinimap] = useState(false)
  const [showParams, setShowParams] = useState(true)
  const [selectedNodeId, setSelectedNodeId] = useState(null)
  const [flowInstance, setFlowInstance] = useState()

  const dispatch = useDispatch()
  const handleRefresh = () => {
    dispatch(
      fetchResult({
        dispatchId: result.dispatch_id,
        resultsDir: result.results_dir,
      })
    )
  }

  useEffect(() => {
    setElements(layout(result.graph, direction, showParams))
  }, [result, direction, showParams])

  useEffect(() => {
    setTimeout(() => {
      if (flowInstance) {
        flowInstance.fitView()
      }
    })
  }, [elements, flowInstance])

  // handle resizing
  useEffect(() => {
    const resizeHandler = _.debounce(() => {
      flowInstance && flowInstance.fitView()
    }, 150)

    window.addEventListener('resize', resizeHandler)
    return () => {
      window.removeEventListener('resize', resizeHandler)
    }
  })

  if (!result) {
    return <div>Not found</div>
  }

  return (
    <>
      <Helmet title={dispatchId} />

      <Breadcrumbs sx={{ mb: 1 }}>
        <Link underline="hover" color="inherit" href="/">
          Results
        </Link>
        <Typography color="text.primary" fontWeight="500">
          {dispatchId}
        </Typography>
      </Breadcrumbs>

      <Box
        sx={{
          color: 'text.secondary',
          fontSize: 'body2.fontSize',
          fontFamily: 'monospace',
        }}
      >
        {result.results_dir}
        <CopyButton
          content={result.results_dir}
          size="small"
          title="Copy results directory"
        />
      </Box>

      <Toolbar>
        <ToggleButtonGroup
          value={direction}
          onChange={(event, newDirection) => {
            if (newDirection) {
              setDirection(newDirection)
            }
          }}
          exclusive
          size="small"
          sx={{ marginLeft: 'auto' }}
        >
          <ToggleButton value="TB">
            <ArrowDownward />
          </ToggleButton>
          <ToggleButton value="BT">
            <ArrowUpward />
          </ToggleButton>
          <ToggleButton value="LR">
            <ArrowForward />
          </ToggleButton>
          <ToggleButton value="RL">
            <ArrowBack />
          </ToggleButton>
        </ToggleButtonGroup>

        <Divider orientation="vertical" sx={{ m: 2 }} flexItem />

        <ToggleButton
          value="checked"
          selected={showMinimap}
          onChange={() => setShowMinimap(!showMinimap)}
          size="small"
        >
          <MapIcon />
        </ToggleButton>

        <Divider orientation="vertical" sx={{ m: 2 }} flexItem />

        <ToggleButton
          value="checked"
          selected={showParams}
          onChange={() => setShowParams(!showParams)}
          size="small"
        >
          Parameters
        </ToggleButton>

        <Divider orientation="vertical" sx={{ m: 2 }} flexItem />

        <IconButton onClick={handleRefresh}>
          <Refresh />
        </IconButton>
      </Toolbar>

      <Paper sx={{ p: 2, height: '500px' }}>
        <ReactFlow
          nodeTypes={{ electron: ElectronNode, parameter: ParameterNode }}
          nodesDraggable={false}
          nodesConnectable={false}
          onLoad={(instance) => {
            setFlowInstance(instance)
          }}
          elements={elements}
          onSelectionChange={(elements) => {
            // assume no multi-selection for now
            setSelectedNodeId(_.get(elements, ['0', 'id'], null))
          }}
        >
          <Controls />
          {showMinimap && <MiniMap />}
        </ReactFlow>
      </Paper>

      <NodeInfo dispatchId={dispatchId} nodeId={selectedNodeId} />
    </>
  )
}

export default Result
