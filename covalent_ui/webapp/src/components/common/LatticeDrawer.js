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
