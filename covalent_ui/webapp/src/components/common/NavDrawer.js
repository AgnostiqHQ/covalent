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
import {
  Drawer,
  Link,
  List,
  ListItemButton,
  Tooltip,
  SvgIcon,
} from '@mui/material'

import { ReactComponent as Logo } from '../../assets/covalent-logo.svg'
import { ReactComponent as DispatchList } from '../../assets/dashboard.svg'
import { ReactComponent as DispatchPreview } from '../../assets/license.svg'
import { useMatch } from 'react-router-dom'

export const navDrawerWidth = 60

const NavDrawer = () => {
  return (
    <Drawer
      data-testid="navDrawer"
      variant="permanent"
      anchor="left"
      className="side-drawernav"
      sx={{
        width: navDrawerWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: navDrawerWidth,
          boxSizing: 'border-box',
          border: 'none',
          backgroundColor: 'background.default',
        },
      }}
    >
      <List>
        <ListItemButton sx={{ my: 2.5, mb: 6 }} component={Link} to="/">
          <Logo data-testid="covalentLogo" style={{ margin: 'auto' }} />
        </ListItemButton>

        <LinkButton
          title="Dispatch list"
          path="/"
          icon={DispatchList}
          margintop={8}
        />

        <LinkButton
          title="Lattice draw preview"
          path="/preview"
          icon={DispatchPreview}
        />
      </List>
    </Drawer>
  )
}

const LinkButton = ({ title, icon, path, margintop }) => {
  const selected = useMatch(path)

  return (
    <Tooltip
      title={title}
      placement="right"
      arrow
      enterDelay={500}
      enterNextDelay={750}
    >
      <ListItemButton
        sx={{ mt: margintop }}
        component={Link}
        to={path}
        selected={!!selected}
      >
        {!!selected ? (
          <SvgIcon
            sx={{
              mx: 'auto',
              border: '1px solid #998AFF',
              width: '30px',
              height: '30px',
              padding: '5px 0px 0px 3px',
              borderRadius: '6px',
              my: 2,
            }}
            component={icon}
          />
        ) : (
          <SvgIcon
            sx={{ mx: 'auto', my: 2, marginLeft: '4px' }}
            component={icon}
          />
        )}
      </ListItemButton>
    </Tooltip>
  )
}
export default NavDrawer
