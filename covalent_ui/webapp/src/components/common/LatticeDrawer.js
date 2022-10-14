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

import { Drawer } from '@mui/material'
import { navDrawerWidth } from './NavDrawer'

export const latticeDrawerWidth = 400

const drawerPaperStyles = (theme) => ({
  py: 2,
  width: latticeDrawerWidth,
  boxSizing: 'border-box',
  border: 'none',
  backgroundColor: theme.palette.background.default,
  '&:not(:hover)::-webkit-scrollbar-thumb': {
    backgroundColor: 'inherit',
  },
  '&:not(:hover)::-webkit-scrollbar': {
    backgroundColor: 'inherit',
  },
  ml: `${navDrawerWidth}px`,
})

const LatticeDrawer = ({ children }) => {
  return (
    <>
      {/* Desktop */}
      <Drawer
        data-testid="latticeDrawer"
        variant="permanent"
        sx={(theme) => ({
          // display: { xs: 'none', md: 'block' },
          '& .MuiDrawer-paper': drawerPaperStyles(theme),
        })}
      >
        {children}
      </Drawer>

      {/* Mobile */}
      {/* <Drawer
        variant="temporary"
        open={latticeDrawerOpen}
        onClose={() => dispatch(toggleLatticeDrawer())}
        sx={(theme) => ({
          display: { xs: 'block', md: 'none' },
          '& .MuiDrawer-paper': drawerPaperStyles(theme),
        })}
      >
        <LatticeDrawerContents />
      </Drawer> */}
    </>
  )
}

export default LatticeDrawer
