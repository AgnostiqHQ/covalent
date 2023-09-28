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
