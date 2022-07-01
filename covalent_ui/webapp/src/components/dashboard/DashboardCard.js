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

import React, { useEffect } from 'react'
import { Paper, Typography, Divider, CircularProgress } from '@mui/material'
import { Box } from '@mui/system'
import CopyButton from '../common/CopyButton'
import { displayStatus, secondsToHms } from '../../utils/misc'
import { useDispatch, useSelector } from 'react-redux'
import { fetchDashboardOverview } from '../../redux/dashboardSlice'

const DashboardCard = (props) => {
  const { dispatcherAddress } = props
  const dispatch = useDispatch()

  // selecting the dashboardOverview from redux state
  const dashboardStats = useSelector(
    (state) => state.dashboard.dashboardOverview
  )
  const isDeleted = useSelector((state) => (state.dashboard.deleteResults.isDeleted))

  const isFetching = useSelector(
    (state) => state.dashboard.fetchDashboardOverview.isFetching
  )

  const fetchDashboardOverviewResult =()=>{
    dispatch(fetchDashboardOverview())
  }

  useEffect(() => {
    fetchDashboardOverviewResult()
  },[isDeleted])

  return (
    <Paper elevation={0} sx={{ p: 3, mb: 2, borderRadius: '8px' }}>
      <Box sx={{ display: 'flex', alignItems: 'center' }}>
        <Typography fontSize="h5.fontSize" sx={{ color: '#F1F1F6' }}>
          Dispatch list
        </Typography>
        {isFetching && <CircularProgress size="1rem" sx={{ mx: 2 }} />}
        {dispatcherAddress && (
          <>
            <Typography sx={{ ml: 'auto' }} color="text.secondary">
              {dispatcherAddress}
            </Typography>
            <CopyButton
              sx={{ ml: 1 }}
              size="small"
              content={dispatcherAddress}
              title="Copy dispatcher address"
              isBorderPresent={true}
            />
          </>
        )}
      </Box>
      <Box sx={{ mt: 3, display: 'flex', justifyContent: 'space-around' }}>
        <DashBoardCardItems
          content={dashboardStats.total_jobs_running}
          desc="Total jobs running"
          align="center"
        />
        <DashboardDivider />
        <DashBoardCardItems
          content={dashboardStats.total_jobs_done}
          desc="Total jobs done"
          align="center"
        />
        <DashboardDivider />
        <DashBoardCardItems
          content={
            displayStatus(dashboardStats.latest_running_task_status) || 'N/A'
          }
          desc="Latest running task status"
          align="center"
        />
        <DashboardDivider />
        <DashBoardCardItems
          content={secondsToHms(dashboardStats.total_dispatcher_duration)}
          desc="Total dispatcher duration"
          align="flex-end"
        />
      </Box>
    </Paper>
  )
}

const DashBoardCardItems = ({ desc, content, align }) => (
  <Box
    sx={{
      display: 'flex',
      mr: 1,
      flexDirection: 'column',
      alignItems: align,
      width: '100%',
    }}
  >
    <Typography fontSize="h5.fontSize">
      {content || content === 0 ? content : 'N/A'}
    </Typography>
    <Typography color="text.secondary">{desc}</Typography>
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
