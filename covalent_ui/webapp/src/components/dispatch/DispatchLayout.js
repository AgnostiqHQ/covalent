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

import _ from 'lodash'
import React, { useEffect, useState } from 'react'
import { Box } from '@mui/material'
import { useDispatch, useSelector } from 'react-redux'
import { useParams } from 'react-router-dom'
import LatticeGraph from '../graph/LatticeGraph'
import NotFound from '../NotFound'
import NodeDrawer from '../common/NodeDrawer'
import PageLoading from '../common/PageLoading'
import { graphBgColor } from '../../utils/theme'
import LatticeDrawer, { latticeDrawerWidth } from '../common/LatticeDrawer'
import NavDrawer, { navDrawerWidth } from '../common/NavDrawer'
import { graphResults, resetGraphState } from '../../redux/graphSlice'
import { resetLatticeState } from '../../redux/latticeSlice'
import { resetElectronState } from '../../redux/electronSlice'
import DispatchTopBar from './DispatchTopBar'
import DispatchDrawerContents from './DispatchDrawerContents'
import '@xyflow/react/dist/style.css'

const initialSelectedNodes = [];

export function DispatchLayout() {
  const { dispatchId } = useParams()
  const dispatch = useDispatch()
  const graph_result = useSelector((state) => state.graphResults.graphList)
  const [prettify, setPrettify] = useState(true)
  const latDetailError = useSelector(
    (state) => state.latticeResults.latticeDetailsResults.error
  )
  const sublatticesDispatchId = useSelector(
    (state) => state.latticeResults.sublatticesId
  )
  // check if socket message is received and call API
  const callSocketApi = useSelector((state) => state.common.callSocketApi)
  useEffect(() => {
    if (sublatticesDispatchId?.dispatchId)
      dispatch(graphResults({ dispatchId: sublatticesDispatchId?.dispatchId }))
    else dispatch(graphResults({ dispatchId }))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [callSocketApi, sublatticesDispatchId])

  // reset store values to initial state when moved to another page
  useEffect(() => {
    return () => {
      dispatch(resetGraphState())
      dispatch(resetLatticeState())
      dispatch(resetElectronState())
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // TODO: replace
  console.log("DEBUG: rendering DispatchLayout")
  // Track selected flow node to control the NodeDrawer
  const [selectedNodes, setSelectedNodes] = useState(initialSelectedNodes);
  const handleNodeSelectionChange = (selected) => {
    console.log("DEBUG: In handleNodeSelectionChange")
    setSelectedNodes(selected)
  }

  const nodeId = selectedNodes.length === 1 ? selectedNodes[0].id : ''
  const selectedElectron = _.find(
      _.get(graph_result, 'nodes'),
      (node) => nodeId === String(_.get(node, 'id')) && _.get(node, 'type') !== 'parameter'
  )
  const handleNodeDrawerClose = () => {
    // MIGRATION: update selected attributes of nodes and edges
    setSelectedNodes(initialSelectedNodes)
  }

  // unselect on change of dispatch
  useEffect(() => {
    setSelectedNodes(initialSelectedNodes)
  }, [dispatchId, setSelectedNodes, sublatticesDispatchId])

  // dispatch id not found
  if (latDetailError !== null && latDetailError.status === 400) {
    return <NotFound text="Lattice dispatch not found." />
  }

  return (
    <>
    <Box
      sx={{
        display: 'flex',
        width: '100vw',
        height: '100vh',
        bgcolor: graphBgColor,
      }}
    >
      <DispatchTopBar />
      <NavDrawer />
      <LatticeDrawer>
        <DispatchDrawerContents />
      </LatticeDrawer>
      <Box
        sx={{
          flex: 1,
          height: '100%',
          marginLeft: `${latticeDrawerWidth + navDrawerWidth}px`,
          paddingTop: '35px',
        }}
      >
        {Object.keys(graph_result).length !== 0 && (
          <LatticeGraph
            graph={graph_result}
            hasSelectedNode={!!selectedElectron}
            marginLeft={latticeDrawerWidth + navDrawerWidth}
            dispatchId={dispatchId}
            togglePrettify={() => {
              setPrettify(!prettify)
            }}
            prettify={prettify}
            handleNodeSelectionChange={handleNodeSelectionChange}
          />
        )}
      </Box>

      {Object.keys(graph_result).length !== 0 ? (
        <NodeDrawer
          prettify={prettify}
          node={selectedElectron}
          dispatchId={
            sublatticesDispatchId
              ? sublatticesDispatchId?.dispatchId
              : dispatchId
          }
          handleClose={handleNodeDrawerClose}
        />
      ) : (
        <PageLoading />
      )}

    </Box>

    </>
  )
}

const UUID_PATTERN =
  /^[0-9a-fA-F]{8}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{12}$/;

export function DispatchLayoutValidate() {
  let { dispatchId } = useParams()
  if (!UUID_PATTERN.test(dispatchId)) {
    return <NotFound text="Lattice dispatch not found." />
  }
  return <DispatchLayout />
}
