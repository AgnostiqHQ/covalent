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

import { useState, useEffect } from 'react'
import { useSelector, useDispatch } from 'react-redux'
import { useParams } from 'react-router-dom'
import { Box, styled, Tab, Skeleton } from '@mui/material'
import { TabContext, TabList, TabPanel } from '@mui/lab'
import LatticeDispatchOverview from './LatticeDispatchOverview'
import ErrorCard from '../common/ErrorCard'
import { latticeDetails, latticeError } from '../../redux/latticeSlice'

const DispatchDrawerContents = (props) => {
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
  const callSocketApi = useSelector(
    (state) => state.common.callSocketApi
  )

  useEffect(() => {
    dispatch(latticeDetails({ dispatchId }))
    dispatch(latticeError({ dispatchId, params: 'error' }))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [callSocketApi])

  return (
    <Box sx={{ px: 3, my: 0 }}>
      {Object.keys(drawerLatticeError).length !== 0 &&
        (drawerLatticeErrorFetching &&
        drawerLatticeError.status === 'FAILED' ? (
          <Skeleton height={300} />
        ) : (
          <ErrorCard showElectron error={drawerLatticeError.data} />
        ))}

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
          <LatticeDispatchOverview
            dispatchId={dispatchId}
            latDetails={drawerLatticeDetails}
            isFetching={drawerLatticeDetailsFetching}
          />
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

export default DispatchDrawerContents
