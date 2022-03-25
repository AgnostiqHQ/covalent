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

import _ from 'lodash'
import {
  Container,
  Paper,
  Typography,
  Divider,
  CircularProgress,
} from '@mui/material'
import { useSelector } from 'react-redux'
import { createSelector } from '@reduxjs/toolkit'
import { differenceInSeconds, isValid, parseISO } from 'date-fns'

import ResultListing from './dispatches/ResultListing'
import { Box } from '@mui/system'
import CopyButton from './common/CopyButton'
import { humanize } from './dispatches/Runtime'
import { displayStatus } from '../utils/misc'
import NavDrawer from './common/NavDrawer'

const selectResultsCache = (state) => state.results.cache

const selectLatestResult = createSelector(selectResultsCache, (cache) => {
  return _.chain(cache).values().maxBy('start_time').value()
})

export const selectDispatcherAddress = createSelector(
  selectLatestResult,
  (latestResult) => {
    let address = _.get(latestResult, 'lattice.metadata.dispatcher', null)
    if (address) {
      const protocol = _.includes(address, '//') ? '' : 'https://'
      address = protocol + address
    }
    return address
  }
)

export const parseDurationInSecs = (start, end) => {
  start = parseISO(start)
  end = parseISO(end)
  if (!isValid(start) || !isValid(end)) {
    return 0
  }
  return differenceInSeconds(end, start)
}

export const selectJobStats = createSelector(selectResultsCache, (cache) => {
  const isRunning = (result) => result.status === 'RUNNING'
  const isCompleted = (result) => result.status === 'COMPLETED'

  const stats = _.reduce(
    cache,
    (stats, result) => {
      if (!result) {
        return stats
      }
      stats.running += isRunning(result) ? 1 : 0
      stats.done += isCompleted(result) ? 1 : 0
      stats.duration += parseDurationInSecs(result.start_time, result.end_time)
      if (
        !stats.latest ||
        // prefer running to not running
        (isRunning(result) && !isRunning(stats.latest)) ||
        // prefer last started among running
        (isRunning(result) &&
          isRunning(stats.latest) &&
          result.start_time > stats.latest.start_time) ||
        // prefer last ended among not running
        (!isRunning(result) &&
          !isRunning(stats.latest) &&
          result.end_time > stats.latest.end_time)
      ) {
        stats.latest = result
      }
      return stats
    },
    {
      running: 0,
      done: 0,
      duration: 0,
      latest: null,
    }
  )

  return stats
})

const Dashboard = () => {
  const dispatcherAddress = useSelector(selectDispatcherAddress)
  const stats = useSelector(selectJobStats)
  const isFetching = useSelector(
    (state) => state.results.fetchResults.isFetching
  )

  return (
    <Box sx={{ display: 'flex' }}>
      <NavDrawer />

      <Container maxWidth="xl" sx={{ mb: 4, mt: 7 }}>
        <Paper elevation={0} sx={{ p: 3, mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Typography fontSize="h5.fontSize">Dispatch list</Typography>
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
                />
              </>
            )}
          </Box>

          <Box sx={{ mt: 3, display: 'flex', justifyContent: 'space-around' }}>
            <DashboardCard content={stats.running} desc="Total jobs running" />
            <DashboardDivider />

            <DashboardCard content={stats.done} desc="Total jobs done" />
            <DashboardDivider />

            <DashboardCard
              content={displayStatus(_.get(stats, 'latest.status')) || 'N/A'}
              desc="Latest running task status"
            />
            <DashboardDivider />

            <DashboardCard
              content={humanize(stats.duration * 1000)}
              desc="Total dispatcher duration"
            />
          </Box>
        </Paper>

        <ResultListing />
      </Container>
    </Box>
  )
}

const DashboardCard = ({ desc, content }) => (
  <Box sx={{ textAlign: 'right' }}>
    <Typography fontSize="h5.fontSize">{content}</Typography>
    <Typography color="text.secondary">{desc}</Typography>
  </Box>
)

const DashboardDivider = () => (
  <Divider flexItem orientation="vertical" sx={{ borderColor: '#29425B' }} />
)

export default Dashboard
