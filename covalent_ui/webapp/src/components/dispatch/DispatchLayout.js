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
 import { Box } from '@mui/material'
 import { useDispatch, useSelector } from 'react-redux'
 import { useStoreActions, useStoreState } from 'react-flow-renderer'
 import { useParams } from 'react-router-dom'
 import { useEffect } from 'react'

 import LatticeGraph from '../graph/LatticeGraph'
 import NotFound from '../NotFound'
 import NodeDrawer, { nodeDrawerWidth } from '../common/NodeDrawer'
 import PageLoading from '../common/PageLoading'
 import LatticeDrawer, { latticeDrawerWidth } from '../common/LatticeDrawer'
 import NavDrawer, { navDrawerWidth } from '../common/NavDrawer'
 import { fetchResult } from '../../redux/resultsSlice'
 import DispatchDrawerContents from './DispatchDrawerContents'

 const DispatchLayout = () => {
   const { dispatchId } = useParams()
   const result = useSelector((state) => state.results.cache[dispatchId])
   const isFetching = useSelector(
     (state) => state.results.fetchResult.isFetching
   )

   const selectedElectron = useStoreState((state) => {
     const nodeId = _.get(
       _.find(state.selectedElements, { type: 'electron' }),
       'id'
     )
     return _.find(
       _.get(result, 'graph.nodes'),
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

   const dispatch = useDispatch()
   useEffect(() => {
     if (!result || _.get(result, 'status') === 'RUNNING') {
       dispatch(fetchResult({ dispatchId }))
     }
     // eslint-disable-next-line react-hooks/exhaustive-deps
   }, [dispatchId])

   if (!result) {
     if (isFetching) {
       return <PageLoading />
     }
     return <NotFound text="Lattice dispatch not found." />
   }

   return (
     <>
       <Box
         sx={{
           display: 'flex',
           width: '100vw',
           height: '100vh',
           bgcolor: '#08081A',
         }}
       >
         <LatticeGraph
           graph={result.graph}
           hasSelectedNode={!!selectedElectron}
           marginLeft={latticeDrawerWidth + navDrawerWidth}
           marginRight={!!selectedElectron ? nodeDrawerWidth : 0}
         />
       </Box>

       <NavDrawer />
       <LatticeDrawer>
         <DispatchDrawerContents />
       </LatticeDrawer>
       <NodeDrawer node={selectedElectron} graph={result.graph} />
     </>
   )
 }

 const UUID_PATTERN =
   /^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$/

 const DispatchLayoutValidate = () => {
   let { dispatchId } = useParams()
   if (!UUID_PATTERN.test(dispatchId)) {
     return <NotFound />
   }
   return <DispatchLayout />
 }

 export default DispatchLayoutValidate
