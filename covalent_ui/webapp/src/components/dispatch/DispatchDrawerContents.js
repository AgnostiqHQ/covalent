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

import { useState, useEffect } from 'react'
import { useSelector, useDispatch } from 'react-redux'
import { useParams } from 'react-router-dom'
import {
  Box,
  styled,
  Tab,
  Skeleton,
  IconButton,
  Tooltip,
  Typography,
  SvgIcon,
} from '@mui/material'
import { TabContext, TabList, TabPanel } from '@mui/lab'
import LatticeDispatchOverview from './LatticeDispatchOverview'
import SublatticesListing from '../dispatches/SublatticesListing'
import ErrorCard from '../common/ErrorCard'
import {
  latticeDetails,
  latticeError,
  sublatticesListDetails,
  resetSublatticesId,
} from '../../redux/latticeSlice'
import { ChevronLeft } from '@mui/icons-material'
import CopyButton from '../common/CopyButton'
import { truncateMiddle } from '../../utils/misc'
import { ReactComponent as TreeSvg } from '../../assets/tree.svg'

const DispatchDrawerContents = () => {
  const { dispatchId } = useParams()
  const dispatch = useDispatch()
  const [tab, setTab] = useState('overview')

  const drawerLatticeDetails = useSelector(
    (state) => state.latticeResults.latticeDetails
  )
  const drawerLatticeError = useSelector(
    (state) => state.latticeResults.latticeError
  )
  const drawerLatticeDetailsFetching = useSelector(
    (state) => state.latticeResults.latticeDetailsResults.isFetching
  )
  const drawerLatticeErrorFetching = useSelector(
    (state) => state.latticeResults.latticeErrorList.isFetching
  )
  const callSocketApi = useSelector((state) => state.common.callSocketApi)

  const sublatticesListView = useSelector(
    (state) => state.latticeResults.sublatticesList
  )
  const sublatticesListApi = () => {
    const bodyParams = {
      sort_by: 'total_electrons',
      direction: 'desc',
      dispatchId,
    }
    dispatch(sublatticesListDetails(bodyParams))
  }

  useEffect(() => {
    dispatch(latticeError({ dispatchId, params: 'error' }))
    dispatch(latticeDetails({ dispatchId }))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [callSocketApi])

  useEffect(() => {
    sublatticesListApi()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [callSocketApi])

  const handleTabChange = (value) => {
    dispatch(resetSublatticesId())
    setTab(value)
  }

  return (
    <Box sx={{ px: 3 }} data-testid="latticedispatchoverview">
      <Box
        sx={{ mt: '16px', p: 0, display: 'flex', alignItems: 'center' }}
        data-testid="backbtn"
      >
        <IconButton
          data-testid="backbtn"
          href="/"
          sx={{
            color: 'text.disabled',
            mr: 1,
            backgroundColor: (theme) => theme.palette.background.buttonBg,
            borderRadius: '10px',
            width: '32px',
            height: '32px',
          }}
        >
          <ChevronLeft />
        </IconButton>

        <SvgIcon
          component={TreeSvg}
          sx={{ verticalAlign: 'middle', marginTop: 1 }}
        />
        {!dispatchId ? (
          <Skeleton width={200} />
        ) : (
          <Tooltip title={dispatchId} placement="top">
            <Typography
              component="span"
              sx={{
                mx: 1,
                verticalAlign: 'middle',
                fontSize: '1 rem',
                color: (theme) => theme.palette.text.secondary,
              }}
            >
              {truncateMiddle(dispatchId, 8, 13)}
            </Typography>
          </Tooltip>
        )}

        <CopyButton
          data-testid="copydispatchId"
          content={dispatchId}
          size="small"
          title="Copy dispatch Id"
          isBorderPresent
        />
      </Box>
      {drawerLatticeDetails.status === 'FAILED' &&
        (drawerLatticeErrorFetching ? (
          <Skeleton height={300} />
        ) : (
          <ErrorCard showElectron error={drawerLatticeError.data} />
        ))}

      {/* tabs */}
      {/* {latOutput !== null && */}
      <TabContext value={tab} sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <CustomTabList
          variant="fullWidth"
          onChange={(e, newTab) => handleTabChange(newTab)}
        >
          <Tab label="Overview" value="overview" />
          {sublatticesListView.length > 0 && (
            <Tab label="Sublattices" value="sublattices" />
          )}
        </CustomTabList>

        <TabPanel value="overview" sx={{ px: 0, py: 1 }}>
          <LatticeDispatchOverview
            dispatchId={dispatchId}
            latDetails={drawerLatticeDetails}
            isFetching={drawerLatticeDetailsFetching}
          />
        </TabPanel>
        {sublatticesListView.length > 0 && (
          <TabPanel value="sublattices" sx={{ px: 0, py: 1 }}>
            <SublatticesListing />
          </TabPanel>
        )}
      </TabContext>
      {/* } */}
    </Box>
  )
}

const CustomTabList = styled(TabList)(({ theme }) => ({
  '& .MuiTab-root': {
    textTransform: 'none',
    color: '#86869A',
    '&.Mui-selected': {
      color: theme.palette.primary.white,
    },
  },
  '& .MuiTabs-indicator': {
    height: 1,
    backgroundColor: theme.palette.text.primary,
  },
}))

export default DispatchDrawerContents
