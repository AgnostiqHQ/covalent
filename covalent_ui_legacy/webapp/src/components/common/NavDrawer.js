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

import React from 'react'
import { Drawer, Link, List, ListItemButton, Tooltip } from '@mui/material'

import ViewListIcon from '@mui/icons-material/ViewList'
import DriveFileRenameOutlineIcon from '@mui/icons-material/DriveFileRenameOutline'
import { ReactComponent as Logo } from '../../assets/covalent-logo.svg'
import { useMatch } from 'react-router-dom'

export const navDrawerWidth = 60

const NavDrawer = () => {
  return (
    <Drawer
      variant="permanent"
      anchor="left"
      sx={{
        width: navDrawerWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: navDrawerWidth,
          boxSizing: 'border-box',
          border: 'none',
        },
      }}
    >
      <List>
        <ListItemButton sx={{ my: 6 }} component={Link} to="/">
          <Logo style={{ margin: 'auto' }} />
        </ListItemButton>

        <LinkButton title="Dispatch list" path="/" icon={ViewListIcon} />

        <LinkButton
          title="Lattice draw preview"
          path="/preview"
          icon={DriveFileRenameOutlineIcon}
        />
      </List>
    </Drawer>
  )
}

const LinkButton = ({ title, icon, path }) => {
  const selected = useMatch(path)

  return (
    <Tooltip
      title={title}
      placement="right"
      arrow
      enterDelay={500}
      enterNextDelay={750}
    >
      <ListItemButton component={Link} to={path} selected={!!selected}>
        {React.createElement(icon, { sx: { mx: 'auto' } })}
      </ListItemButton>
    </Tooltip>
  )
}

export default NavDrawer
