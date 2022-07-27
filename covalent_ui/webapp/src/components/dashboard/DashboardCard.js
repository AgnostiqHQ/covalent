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

import React, { useEffect, useState } from 'react'
import {
  Paper,
  Typography,
  Divider,
  Skeleton,
  Snackbar,
  SvgIcon,
} from '@mui/material'
import { Box } from '@mui/system'
import { displayStatus, secondsToHms } from '../../utils/misc'
import { useDispatch, useSelector } from 'react-redux'
import { fetchDashboardOverview } from '../../redux/dashboardSlice'
import { ReactComponent as closeIcon } from '../../assets/close.svg'

const DashboardCard = () => {
  const dispatch = useDispatch()
  // check if socket message is received and call API
  const callSocketApi = useSelector((state) => state.common.callSocketApi)
  // selecting the dashboardOverview from redux state
  const dashboardStats = useSelector(
    (state) => state.dashboard.dashboardOverview
  )
  const isFetching = useSelector(
    (state) => state.dashboard.fetchDashboardOverview.isFetching
  )

  const isError = useSelector(
    (state) => state.dashboard.fetchDashboardOverview.error
  )
  //check if any dispatches are deleted and call the API
  const isDeleted = useSelector((state) => state.dashboard.dispatchesDeleted)

  const [openSnackbar, setOpenSnackbar] = useState(Boolean(isError))

  const fetchDashboardOverviewResult = () => {
    dispatch(fetchDashboardOverview())
  }

  useEffect(() => {
    fetchDashboardOverviewResult()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isDeleted, callSocketApi])

  useEffect(() => {
    if (isError) setOpenSnackbar(true)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isError])

  return (
    <Paper elevation={0} sx={{ p: 3, mb: 2, borderRadius: '8px' }}>
      <Box sx={{ display: 'flex', alignItems: 'center' }}>
        <Typography fontSize="h5.fontSize" sx={{ color: '#FFFFFF' }}>
          Dispatch list
        </Typography>
        <Snackbar
          open={openSnackbar}
          autoHideDuration={3000}
          message="Something went wrong,please contact the administrator!"
          onClose={() => setOpenSnackbar(false)}
          action={
            <SvgIcon
              sx={{
                mt: 2,
                zIndex: 2,
                cursor: 'pointer',
              }}
              component={closeIcon}
              onClick={() => setOpenSnackbar(false)}
            />
          }
        />
      </Box>
      <Box sx={{ mt: 3, display: 'flex', justifyContent: 'space-around' }}>
        <DashBoardCardItems
          content={dashboardStats.total_jobs_running}
          desc="Total jobs running"
          align="center"
          isSkeletonPresent={isFetching}
        />
        <DashboardDivider />
        <DashBoardCardItems
          content={dashboardStats.total_jobs_completed}
          desc="Total jobs done"
          align="center"
          isSkeletonPresent={isFetching}
        />
        <DashboardDivider />
        <DashBoardCardItems
          content={
            displayStatus(dashboardStats.latest_running_task_status) || 'N/A'
          }
          desc="Latest running task status"
          align="center"
          isSkeletonPresent={isFetching}
        />
        <DashboardDivider />
        <DashBoardCardItems
          content={secondsToHms(dashboardStats.total_dispatcher_duration)}
          desc="Total dispatcher duration"
          align="flex-end"
          isSkeletonPresent={isFetching}
        />
      </Box>
    </Paper>
  )
}

const DashBoardCardItems = ({ desc, content, align, isSkeletonPresent }) => (
  <Box
    sx={{
      display: 'flex',
      mr: 1,
      flexDirection: 'column',
      alignItems: align,
      width: '100%',
    }}
  >
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'flex-end',
      }}
    >
      <Typography fontSize="h5.fontSize" color="text.secondary">
        {isSkeletonPresent ? (
          <Skeleton width={25} />
        ) : content || content === 0 ? (
          content
        ) : (
          'N/A'
        )}
      </Typography>
      <Typography sx={{ marginTop: '16px' }} color="text.primary">
        {' '}
        {desc}
      </Typography>
    </Box>
  </Box>
)

const DashboardDivider = () => (
  <Divider
    flexItem
    orientation="vertical"
    sx={(theme) => ({
      borderColor: theme.palette.background.coveBlack02,
      ml: 1,
    })}
  />
)

export default DashboardCard
