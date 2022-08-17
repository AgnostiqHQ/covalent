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
