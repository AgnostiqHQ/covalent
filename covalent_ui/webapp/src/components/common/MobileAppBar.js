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

import { alpha, AppBar, IconButton, Toolbar } from '@mui/material'
import { Menu as MenuIcon } from '@mui/icons-material'

import { toggleLatticeDrawer } from '../../redux/commonSlice'
import { useDispatch } from 'react-redux'

const MobileAppBar = () => {
  const dispatch = useDispatch()

  return (
    <AppBar
      data-testid="mobile appbar"
      position="fixed"
      sx={(theme) => ({
        display: {
          xs: 'block',
          md: 'none',
        },
        bgcolor: alpha(theme.palette.background.paper, 0.3),
        backdropFilter: 'blur(16px)',
      })}
    >
      <Toolbar>
        <IconButton
          sx={{ mr: 2 }}
          color="inherit"
          edge="start"
          onClick={() => dispatch(toggleLatticeDrawer())}
        >
          <MenuIcon />
        </IconButton>
      </Toolbar>
    </AppBar>
  )
}

export default MobileAppBar
