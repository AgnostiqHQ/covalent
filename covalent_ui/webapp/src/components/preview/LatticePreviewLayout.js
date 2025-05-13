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
import { useState } from 'react'
import { useSelector } from 'react-redux'
import LatticeMain from '../graph/LatticeGraph'
import NotFound from '../NotFound'
import NodeDrawer, { nodeDrawerWidth } from './NodePreviewDrawer'
import { useEffect } from 'react'
import { graphBgColor } from '../../utils/theme'
import LatticeDrawer, { latticeDrawerWidth } from '../common/LatticeDrawer'
import NavDrawer, { navDrawerWidth } from '../common/NavDrawer'

import PreviewDrawerContents from './PreviewDrawerContents'

const initialSelectedNodes = [];

const LatticePreviewLayout = () => {
  const lattice = useSelector((state) => state.latticePreview.lattice)

  // Track selected flow node to control the NodeDrawer
  const [selectedNodes, setSelectedNodes] = useState(initialSelectedNodes);
  const handleNodeSelectionChange = (selected) => {
    setSelectedNodes(selected)
  }

  const nodeId = selectedNodes.length === 1 ? selectedNodes[0].id : ''
  const selectedElectron = _.find(
      _.get(lattice, 'graph.nodes'),
      (node) => nodeId === String(_.get(node, 'id')) && _.get(node, 'type') !== 'parameter'
  )
  const handleNodeDrawerClose = () => {
    setSelectedNodes(initialSelectedNodes)
  }

  // unselect on change of lattice
  useEffect(() => {
    setSelectedNodes(initialSelectedNodes)
  }, [lattice, setSelectedNodes])

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
        <NavDrawer />
        <LatticeDrawer>
          <PreviewDrawerContents />
        </LatticeDrawer>

        <Box
          sx={{
            flex: 1,
            height: '100%',
            marginLeft: `${latticeDrawerWidth + navDrawerWidth}px`,
            paddingTop: '35px',
          }}
        >
          <LatticeMain
            preview
            graph={lattice.graph}
            hasSelectedNode={!!selectedElectron}
            marginLeft={latticeDrawerWidth + navDrawerWidth}
            marginRight={!!selectedElectron ? nodeDrawerWidth : 0}
            handleNodeSelectionChange={handleNodeSelectionChange}
          />
        </Box>

        <NodeDrawer node={selectedElectron} handleClose={handleNodeDrawerClose} />

      </Box>
    </>
  )
}

export default LatticePreviewLayout
