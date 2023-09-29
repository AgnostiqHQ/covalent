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
