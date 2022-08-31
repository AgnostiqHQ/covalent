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

import * as React from 'react'
import Menu from '@mui/material/Menu'
import MenuItem from '@mui/material/MenuItem'

export function LayoutOptions(props) {
  const { algorithm, handleChangeAlgorithm, open, anchorEl, handleClose } =
    props
  const options = [
    {
      optionName: 'Layered',
      optionValue: 'layered',
    },
    {
      optionName: 'Tree',
      optionValue: 'mrtree',
    },
    {
      optionName: 'Force',
      optionValue: 'force',
    },
    {
      optionName: 'Rectangular',
      optionValue: 'rectpacking',
    },
    {
      optionName: 'Box',
      optionValue: 'box',
    },
    {
      optionName: 'Old Layout',
      optionValue: 'oldLayout',
    },
  ]
  return (

    <div data-testid="layoutoption" title="lay__out_menu">
      <Menu
        data-testid='lay__tit'
        variant="menu"
        anchorEl={anchorEl}
        open={open}
        onClose={handleClose}
        keepMounted={false}
        getContentAnchorEl={null}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
        transformOrigin={{ vertical: 'top', horizontal: 'left' }}
        PaperProps={{
          style: {
            transform: 'translateX(-5px) translateY(5px)',
          },
        }}
      >

        {options.map((option) => (
          <MenuItem
            data-testid='layout__opt_menu'
            sx={{
              fontSize: '0.875rem',
              '&.Mui-selected': {
                backgroundColor: '#1C1C46',
              },
            }}
            selected={algorithm === option.optionValue}
            key={option.optionName}
            onClick={() => handleChangeAlgorithm(option.optionValue)}
          >
            {option.optionName}
          </MenuItem>
        ))}

      </Menu>
    </div>
  )
}
