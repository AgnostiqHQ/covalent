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
import React, { useEffect } from 'react'
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
import { graphResults } from '../../redux/graphSlice'
import DispatchTopBar from './DispatchTopBar'
import DispatchDrawerContents from './DispatchDrawerContents'

export function DispatchLayout() {
  const { dispatchId } = useParams()
  const dispatch = useDispatch()
  const graph_result = useSelector((state) => state.graphResults.graphList)
  const fetch = useSelector(
    (state) => state.graphResults.graphResultsList.isFetching
  )
  // check if socket message is received and call API
  const callSocketApi = useSelector((state) => state.common.callSocketApi)
  useEffect(() => {
    dispatch(graphResults({ dispatchId }))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [callSocketApi])

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
  }, [dispatchId, setSelectedElements])

  if (Object.keys(graph_result).length !== 0) {
    if(graph_result.links.length === 0){
    return <NotFound text="Lattice dispatch not found." />
  }
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
          paddingTop:'20px'
        }}
      >
        {Object.keys(graph_result).length !== 0 && !fetch ?
          (
          <LatticeGraph
            graph={graph_result}
            hasSelectedNode={!!selectedElectron}
            marginLeft={latticeDrawerWidth + navDrawerWidth}
          />
        ) : (
          <PageLoading />
        )}
      </Box>
      <NavDrawer />
      <LatticeDrawer>
        <DispatchDrawerContents />
      </LatticeDrawer>
      {Object.keys(graph_result).length !== 0 ? (
        <NodeDrawer
          node={selectedElectron}
          graph={graph_result}
          dispatchId={dispatchId}
        />
      ) : (
        <PageLoading />
      )}
    </>
  )
}

const UUID_PATTERN =
  /^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$/

 const DispatchLayoutValidate = () => {
   let { dispatchId } = useParams()
   if (!UUID_PATTERN.test(dispatchId)) {
     return <NotFound text="Lattice dispatch not found." />
   }
   return <DispatchLayout />
 }

export default DispatchLayoutValidate
