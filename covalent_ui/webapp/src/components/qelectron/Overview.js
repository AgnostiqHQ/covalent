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
import { Grid, Typography, Paper, Skeleton } from '@mui/material'
import theme from '../../utils/theme'
import SyntaxHighlighter from '../common/SyntaxHighlighter'
import { formatQElectronTime, getLocalStartTime, formatDate } from '../../utils/misc'
import { useSelector } from 'react-redux';

const Overview = (props) => {
  const { details } = props
  const code = details?.result;

  const qelectronJobOverviewIsFetching = useSelector(
    (state) => state.electronResults.qelectronJobOverviewList.isFetching
  )

  return (
    <>
      {' '}
      <Typography
        px={2}
        sx={{
          color: (theme) => theme.palette.text.primary,
          fontSize: theme.typography.sidebarh2,
          fontWeight: 'bold',
        }}
      >
        Execution Details
      </Typography>
      <Grid container px={2} py={1} direcction="row" data-testid="Overview-grid">
        <Grid id="leftGrid" item xs={6}>
          <Typography
            sx={{
              fontSize: theme.typography.sidebarh3,
              mt: 2,
              color: (theme) => theme.palette.text.tertiary,
            }}
          >
            Backend
          </Typography>
          <Typography
            sx={{
              fontSize: theme.typography.sidebarh2,
              mt: 1,
              color: (theme) => theme.palette.text.primary,
            }}
          >
            {qelectronJobOverviewIsFetching && !details ?
              <Skeleton data-testid="node__box_skl" width={150} />
              : <>{(details?.backend) ? (details?.backend) : '-'}</>}
          </Typography>
          <Typography
            sx={{
              fontSize: theme.typography.sidebarh3,
              mt: 2,
              color: (theme) => theme.palette.text.tertiary,
            }}
          >
            Time Elapsed
          </Typography>
          <Typography
            sx={{
              fontSize: theme.typography.sidebarh2,
              mt: 1,
              color: (theme) => theme.palette.text.primary,
            }}
          >
            {qelectronJobOverviewIsFetching && !details ?
              <Skeleton data-testid="node__box_skl" width={150} /> : <>
                {(details?.time_elapsed) ? (formatQElectronTime(details?.time_elapsed)) : '-'}
              </>}
          </Typography>
          <Typography
            sx={{
              fontSize: theme.typography.sidebarh3,
              mt: 2,
              color: (theme) => theme.palette.text.tertiary,
            }}
          >
            Start time - End time
          </Typography>
          {details?.start_time && details?.end_time &&
            <Typography
              sx={{
                fontSize: theme.typography.sidebarh2,
                mt: 1,
                color: (theme) => theme.palette.text.primary,
              }}
            >
              {qelectronJobOverviewIsFetching && !details ?
                <Skeleton data-testid="node__box_skl" width={150} /> : <>
                  {formatDate(getLocalStartTime(details?.start_time))}
                  {` - ${formatDate(getLocalStartTime(details?.end_time))}`}
                </>}
            </Typography>}
        </Grid>
        <Grid
          id="rightGrid"
          item
          xs={6}
          sx={{ display: 'flex', alignItems: 'center' }}
          pt={1}
        >
          <Paper
            elevation={0}
            sx={(theme) => ({
              bgcolor: theme.palette.background.outRunBg,
            })}
          >
            <SyntaxHighlighter src={code} preview isFetching={qelectronJobOverviewIsFetching} />
          </Paper>
        </Grid>
      </Grid>
    </>
  )
}

export default Overview
