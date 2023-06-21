/**
 * Copyright 2023 Agnostiq Inc.
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
import Box from '@mui/material/Box'
import Tab from '@mui/material/Tab'
import TabContext from '@mui/lab/TabContext'
import TabList from '@mui/lab/TabList'
import Divider from '@mui/material/Divider'

const QElectronTab = (props) => {
  const { handleChange, value } = props
  return (
    <Box sx={{ width: '100%', typography: 'body1' }}>
      <TabContext value={value}>
        <TabList
          onChange={handleChange}
          aria-label="lab API tabs example"
          sx={{
            '& .MuiTabs-indicator': {
              backgroundColor: 'transparent',
            },
            '& .MuiTab-root': {
              textTransform: 'capitalize',
              color: (theme) => theme.palette.text.tertiary,
              '&.Mui-selected': {
                color: (theme) => theme.palette.text.secondary,
              },
            },
          }}
        >
          <Tab
            label="Overview"
            value="1"
            sx={{
              '&.Mui-selected': {
                color: 'white',
              },
            }}
          />
          <Divider
            orientation="vertical"
            flexItem
            sx={{
              height: '24px',
              my: '10px',
            }}
          />
          <Tab
            label="Circuit"
            value="2"
            sx={{
              '&.Mui-selected': {
                color: 'white',
              },
            }}
          />
          <Divider
            orientation="vertical"
            flexItem
            sx={{
              height: '24px',
              my: '10px',
            }}
          />
          <Tab
            label="Executor"
            value="3"
            sx={{
              '&.Mui-selected': {
                color: 'white',
              },
            }}
          />
        </TabList>
      </TabContext>
    </Box>
  )
}

export default QElectronTab
