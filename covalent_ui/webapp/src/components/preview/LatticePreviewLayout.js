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
import { Box, Typography } from '@mui/material'
import { useSelector } from 'react-redux'
import { useStoreActions, useStoreState } from 'react-flow-renderer'
import LatticeMain from '../graph/LatticeGraph'
import NotFound from '../NotFound'
import NodeDrawer, { nodeDrawerWidth } from './NodePreviewDrawer'
import { useEffect } from 'react'
import { graphBgColor } from '../../utils/theme'
import LatticeDrawer, { latticeDrawerWidth } from '../common/LatticeDrawer'
import NavDrawer, { navDrawerWidth } from '../common/NavDrawer'

import PreviewDrawerContents from './PreviewDrawerContents'

const LatticePreviewLayout = () => {
  const lattice = useSelector((state) => state.latticePreview.lattice)
  const selectedElectron = useStoreState((state) => {
    const nodeId = _.get(
      _.find(state.selectedElements, { type: 'electron' }),
      'id'
    )
    return _.find(
      _.get(lattice, 'graph.nodes'),
      (node) => nodeId === String(_.get(node, 'id'))
    )
  })

  const setSelectedElements = useStoreActions(
    (actions) => actions.setSelectedElements
  )

  // unselect on change of lattice
  useEffect(() => {
    setSelectedElements([])
  }, [lattice, setSelectedElements])

  if (!lattice) {
    return (
      <NotFound>
        <Typography variant="h6" sx={{ mb: 1 }}>
          Lattice preview not found.
        </Typography>
        <Typography color="text.secondary">
          Try running <code>[lattice].draw_ui()</code> again.
        </Typography>
      </NotFound>
    )
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
        <LatticeMain
          preview
          graph={lattice.graph}
          hasSelectedNode={!!selectedElectron}
          marginLeft={latticeDrawerWidth + navDrawerWidth}
          marginRight={!!selectedElectron ? nodeDrawerWidth : 0}
        />
      </Box>

      {/* <MobileAppBar /> */}
      <NavDrawer />
      <LatticeDrawer>
        <PreviewDrawerContents />
      </LatticeDrawer>

      <NodeDrawer node={selectedElectron} />
    </>
  )
}

export default LatticePreviewLayout
