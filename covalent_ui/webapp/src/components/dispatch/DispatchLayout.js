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
import DispatchDrawerContents from './DispatchDrawerContents'

export function DispatchLayout() {
  const { dispatchId } = useParams()
  const dispatch = useDispatch()
  const graph_result = useSelector((state) => state.graphResults.graphList)
  const fetch = useSelector((state) => state.graphResults.graphResultsList.isFetching)
  useEffect(() => {
    dispatch(graphResults({ dispatchId }))
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
  }, [dispatchId, setSelectedElements])


  if (fetch) {
    return <PageLoading />
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
        {Object.keys(graph_result).length !== 0 ?
          <LatticeGraph
            graph={graph_result}
            hasSelectedNode={!!selectedElectron}
            marginLeft={latticeDrawerWidth + navDrawerWidth}
          />
          :
          <PageLoading />
        }
      </Box>
      <NavDrawer />
      <LatticeDrawer>
        <DispatchDrawerContents />
      </LatticeDrawer>
      {selectedElectron &&
        <NodeDrawer node={selectedElectron} dispatchId={dispatchId} />
      }
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

export default DispatchLayoutValidate;
