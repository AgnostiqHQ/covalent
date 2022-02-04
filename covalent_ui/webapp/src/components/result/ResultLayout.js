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
import { useParams } from 'react-router-dom'
import { useDispatch, useSelector } from 'react-redux'
import { AppBar, Box, Drawer, IconButton, Link, Toolbar } from '@mui/material'
import { Menu as MenuIcon } from '@mui/icons-material'
import { useStoreActions, useStoreState } from 'react-flow-renderer'
import { alpha } from '@mui/material/styles'

import LatticeMain from './LatticeMain'
import LatticeDrawer from './LatticeDrawer'
import NodeDrawer, { nodeDrawerWidth } from './NodeDrawer'
import { ReactComponent as Logo } from '../../assets/covalent-full-logo.svg'
import { fetchResult } from '../../redux/resultsSlice'
import { graphBgColor } from '../../utils/theme'

const drawerWidth = 400

const ResultLayout = () => {
  const { dispatchId } = useParams()
  const result = useSelector((state) => state.results.cache[dispatchId])

  const selectedElectron = useStoreState((state) =>
    _.find(state.selectedElements, { type: 'electron' })
  )
  const setSelectedElements = useStoreActions(
    (actions) => actions.setSelectedElements
  )

  const [latticeDrawerOpen, setLatticeDrawerOpen] = useState(false)

  const handleLatticeDrawerToggle = () => {
    setLatticeDrawerOpen(!latticeDrawerOpen)
  }

  // unselect on change of dispatch
  useEffect(() => {
    setSelectedElements([])
  }, [dispatchId, setSelectedElements])

  const dispatch = useDispatch()
  useEffect(() => {
    if (_.get(result, 'status') === 'RUNNING') {
      dispatch(
        fetchResult({
          dispatchId: result.dispatch_id,
          resultsDir: result.results_dir,
        })
      )
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [dispatchId])

  // TODO handle not found

  return (
    <>
      <Box sx={{ display: 'flex' }}>
        <Box
          sx={{
            width: { md: drawerWidth },
            flexShrink: { md: 0 },
          }}
        >
          {/* Mobile drawer */}
          <Drawer
            variant="temporary"
            open={latticeDrawerOpen}
            onClose={handleLatticeDrawerToggle}
            ModalProps={{
              // better performance on mobile toggle
              keepMounted: true,
            }}
            sx={{
              display: { xs: 'block', md: 'none' },
              '& .MuiDrawer-paper': {
                boxSizing: 'border-box',
                width: drawerWidth,
              },
            }}
          >
            <LatticeDrawer />
          </Drawer>

          {/* Desktop drawer */}
          <Drawer
            variant="permanent"
            sx={(theme) => ({
              display: { xs: 'none', md: 'block' },
              '& .MuiDrawer-paper': {
                boxSizing: 'border-box',
                width: drawerWidth,
                border: 'none',
                bgcolor: alpha(theme.palette.background.default, 0.3),
                '&:not(:hover)::-webkit-scrollbar-thumb': {
                  backgroundColor: 'inherit',
                },
                '&:not(:hover)::-webkit-scrollbar': {
                  backgroundColor: 'inherit',
                },
                transition: 'background-color 1s',
              },
            })}
            open
          >
            <AppBar
              position="static"
              elevation={0}
              sx={(theme) => ({
                bgcolor: alpha(theme.palette.background.default, 0.3),
              })}
            >
              <Toolbar sx={{ my: 3, mb: 2 }}>
                <Link href="/">
                  <Logo />
                </Link>
              </Toolbar>
            </AppBar>

            <LatticeDrawer />
          </Drawer>
        </Box>

        <Box
          component="main"
          sx={(theme) => ({
            flexGrow: 1,
            // width: { md: `calc(100% - ${drawerWidth}px)` },
            height: '100vh',
            marginRight: `-${nodeDrawerWidth}px`,
            ...(!!selectedElectron && {
              marginRight: 0,
            }),
            bgcolor: graphBgColor,
          })}
        >
          <AppBar
            position="static"
            sx={{ display: { xs: 'block', md: 'none' } }}
          >
            <Toolbar>
              <IconButton
                color="inherit"
                edge="start"
                onClick={handleLatticeDrawerToggle}
                sx={{ mr: 2 }}
              >
                <MenuIcon />
              </IconButton>
              <Logo />
            </Toolbar>
          </AppBar>

          <LatticeMain hasSelectedNode={!!selectedElectron} />
        </Box>

        <NodeDrawer
          dispatchId={dispatchId}
          nodeId={_.get(selectedElectron, 'id')}
        />
      </Box>
    </>
  )
}

export default ResultLayout
