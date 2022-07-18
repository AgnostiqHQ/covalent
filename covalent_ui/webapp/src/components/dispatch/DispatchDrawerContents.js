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

import { useState,useEffect } from 'react'
import { useSelector,useDispatch } from 'react-redux'
import { useParams } from 'react-router-dom'
import {
  Box,
  CircularProgress,
  IconButton,
  styled,
  Tab,
  Tooltip,
  Typography,
  SvgIcon
} from '@mui/material'
import { ChevronLeft } from '@mui/icons-material'
import { TabContext, TabList, TabPanel } from '@mui/lab'
import CopyButton from '../common/CopyButton'
import LatticeDispatchOverview from './LatticeDispatchOverview'
import { statusIcon, truncateMiddle ,  statusColor,statusLabel
} from '../../utils/misc'
import ErrorCard from '../common/ErrorCard'
import { ReactComponent as TreeSvg } from '../../assets/tree.svg'
import { latticeDetails,latticeError} from '../../redux/latticeSlice'

const DispatchDrawerContents = () => {
  const { dispatchId } = useParams()
  const dispatch = useDispatch()
  const [tab, setTab] = useState('overview')

  const drawerLatticeDetails = useSelector((state) => state.latticeResults.latticeDetails)
  const drawerLatticeError = useSelector((state) => state.latticeResults.latticeError)

  useEffect(() => {
    dispatch(latticeDetails({ dispatchId}))
    dispatch(latticeError({dispatchId,params:'error'}))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return (
    <Box sx={{ p: 3 }}>
      {/* dispatch id */}
      <IconButton href="/" sx={{ color: 'text.disabled', mr: 1 }}>
        <ChevronLeft />
      </IconButton>

      <SvgIcon component={TreeSvg} sx={{verticalAlign:"middle",marginTop:1}}/>

      <Tooltip title={dispatchId} placement="top">
        <Typography component="span" sx={{ mx: 1 ,verticalAlign:"middle"}}>
          {truncateMiddle(dispatchId, 8, 13)}
        </Typography>
      </Tooltip>

      <CopyButton content={dispatchId} size="small" title="Copy dispatch Id" />

      {/* status */}
      <LatticeStatusCard dispatchId={dispatchId} latDetails={drawerLatticeDetails}
      latError={drawerLatticeError}/>

      {/* tabs */}
      {/* {latOutput !== null && */}
      <TabContext value={tab}>
        <CustomTabList
          variant="fullWidth"
          onChange={(e, newTab) => setTab(newTab)}
        >
          <Tab label="Overview" value="overview" />
        </CustomTabList>

        <TabPanel value="overview" sx={{ px: 0, py: 1 }}>
          <LatticeDispatchOverview dispatchId={dispatchId} latDetails={drawerLatticeDetails} />
        </TabPanel>
      </TabContext>
{/* } */}
    </Box>
  )
}

const CustomTabList = styled(TabList)(({ theme }) => ({
  '& .MuiTab-root': {
    textTransform: 'none',
    '&.Mui-selected': {
      color: theme.palette.primary.white,
    },
  },
  '& .MuiTabs-indicator': {
    height: 1,
    backgroundColor: theme.palette.text.primary,
  },
}))

const LatticeStatusCard = ({ dispatchId ,latDetails,latError }) => {
  return (
    <Box sx={{ my: 2 }}>
        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: 'repeat(2, 1fr)',
          }}
        >
          <Box sx={{ borderRight: '1px solid #303067' }}>
            <Typography color="text.secondary" fontSize="body2.fontSize">
              Status
            </Typography>

            <Box
              sx={{
                color: statusColor(latDetails.status),
                display: 'flex',
                fontSize: '1.125rem',
                alignItems: 'center',
                py: 1,
              }}
            >
              {statusIcon(latDetails.status)}
              &nbsp;
              {statusLabel(latDetails.status)}
            </Box>
          </Box>

          <Box sx={{ justifySelf: 'end' }}>
            <Typography color="text.secondary" fontSize="body2.fontSize">
              Progress
            </Typography>

            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                py: 1,
              }}
            >
              <Typography fontSize="body2.fontSize">
                <Box
                  component="span"
                  sx={{
                    color: latDetails.status!=='COMPLETED'?statusColor(latDetails.status):'',
                  }}
                >
                  {latDetails.total_electrons_completed}
                </Box>
                &nbsp;/ {latDetails.total_electrons}
              </Typography>

              <Box sx={{ ml: 2, position: 'relative' }}>
                <CircularProgress
                  variant="determinate"
                  sx={(theme) => ({
                    color: theme.palette.secondary.main,
                  })}
                  size="2rem"
                  value={100}
                />
                <CircularProgress
                  style={{ color: statusColor(latDetails.status)}}
                  sx={{ position: 'absolute', left: 0 }}
                  variant="determinate"
                  size="2rem"
                  value={(latDetails.total_electrons_completed * 100) / latDetails.total_electrons}
                />
              </Box>
            </Box>
          </Box>
        </Box>
        {Object.keys(latError).length !==0 &&
      <ErrorCard showElectron error={latError.data} />
    }
    </Box>
  )
}

export default DispatchDrawerContents
