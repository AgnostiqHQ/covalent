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
import { useStoreActions, useStoreState } from 'react-flow-renderer'
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
import QElectronDrawer from '../common/QElectronDrawer'

export function DispatchLayout() {
  const { dispatchId } = useParams()
  const dispatch = useDispatch()
  const [openQelectronDrawer, setOpenQelectronDrawer] = useState(false)
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

  const selectedElectron = useStoreState((state) => {
    const nodeId = _.get(
      _.find(state.selectedElements, { type: 'electron' }),
      'id'
    )
    return _.find(
      _.get(graph_result, 'nodes'),
      (node) => nodeId === String(_.get(node, 'id'))
    )
  })
  const setSelectedElements = useStoreActions(
    (actions) => actions.setSelectedElements
  )

  // unselect on change of dispatch
  useEffect(() => {
    setSelectedElements([])
  }, [dispatchId, setSelectedElements, sublatticesDispatchId])

  // dispatch id not found
  if (latDetailError !== null && latDetailError.status === 400) {
    return <NotFound text="Lattice dispatch not found." />
  }

  return (
    <>
      <DispatchTopBar />
      <Box
        sx={{
          display: 'flex',
          width: '100vw',
          height: '100vh',
          bgcolor: graphBgColor,
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
          />
        )}
      </Box>
      <NavDrawer />
      <LatticeDrawer>
        <DispatchDrawerContents />
      </LatticeDrawer>

      {
        <QElectronDrawer
          toggleQelectron={() => setOpenQelectronDrawer((prev) => !prev)}
          openQelectronDrawer={openQelectronDrawer}
          dispatchId={
            sublatticesDispatchId
              ? sublatticesDispatchId?.dispatchId
              : dispatchId
          }
          electronId={selectedElectron?.node_id}
        />
      }
      {Object.keys(graph_result).length !== 0 ? (
        <NodeDrawer
          setOpenQelectronDrawer={setOpenQelectronDrawer}
          toggleQelectron={() => setOpenQelectronDrawer((prev) => !prev)}
          openQelectronDrawer={openQelectronDrawer}
          prettify={prettify}
          node={selectedElectron}
          graph={graph_result}
          dispatchId={
            sublatticesDispatchId
              ? sublatticesDispatchId?.dispatchId
              : dispatchId
          }
        />
      ) : (
        <PageLoading />
      )}
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
