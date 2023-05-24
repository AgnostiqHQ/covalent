import React from 'react'
import Box from '@mui/material/Box'
import Tab from '@mui/material/Tab'
import TabContext from '@mui/lab/TabContext'
import TabList from '@mui/lab/TabList'
import TabPanel from '@mui/lab/TabPanel'
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
              color: 'gray',
              '&.Mui-selected': {
                color: 'white',
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
