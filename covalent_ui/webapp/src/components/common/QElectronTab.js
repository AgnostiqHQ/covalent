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
import React from 'react'
import Box from '@mui/material/Box'
import Tab from '@mui/material/Tab'
import TabContext from '@mui/lab/TabContext'
import TabList from '@mui/lab/TabList'
import Divider from '@mui/material/Divider'

const QElectronTab = (props) => {
  const { handleChange, value } = props
  return (
    <Box sx={{ width: '100%', typography: 'body1' }} data-testid="QelectronTab-box">
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
