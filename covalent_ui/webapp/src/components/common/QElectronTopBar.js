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

import { Grid, IconButton, Typography, Box, Tooltip, Skeleton } from '@mui/material'
import React from 'react'
import { ChevronRight, } from '@mui/icons-material'
import { statusIcon, statusColor, statusLabel } from '../../utils/misc'
import CopyButton from './CopyButton'
import { useSelector } from 'react-redux';

const QElectronTopBar = (props) => {
  const { details, toggleQelectron } = props
  const qelectronJobOverviewIsFetching = useSelector(
    (state) => state.electronResults.qelectronJobOverviewList.isFetching
  )
  return (
    <Grid
      container
      id="qelectronTopbar"
      flexDirection="row"
      alignItems="center"
      justifyContent="space-between"
      p={1.5}
      sx={{
        background: 'transparent',
        borderRadius: '8px',
        border: '1px solid',
        borderColor: (theme) => theme.palette.background.coveBlack02,
      }}
      data-testid="QelectronTopBar-grid"
    >
      <Grid item xs={6} container flexDirection="row" alignItems="center">
        <IconButton
          onClick={() => toggleQelectron()}
          data-testid="backbtn"
          sx={{
            color: 'text.disabled',
            cursor: 'pointer',
            mr: 1,
            backgroundColor: (theme) => theme.palette.background.buttonBg,
            borderRadius: '10px',
            width: '32px',
            height: '32px',
          }}
        >
          <ChevronRight />
        </IconButton>
        {qelectronJobOverviewIsFetching && !details ?
          <Skeleton data-testid="qelectron_top__bar_skl" width={100} sx={{ mr: '5px' }} /> : <>
            <Typography fontSize="sidebarh2" mr={2}>
              {details?.title}
            </Typography>
          </>}
        <Grid
          sx={{
            width: '70px',
            height: '32px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            border: '1px solid',
            pl: '3px',
            borderColor: (theme) => theme.palette.background.coveBlack02,
            borderRadius: '8px 0px 0px 8px',
            backgroundColor: (theme) => theme.palette.background.buttonBg,
          }}
        >
          {qelectronJobOverviewIsFetching && !details ?
            <Skeleton data-testid="qelectron_top__bar_skl" width={100} sx={{ mr: '5px' }} /> : <>
              <Tooltip
                data-testid="toolTip"
                title={details?.id}
                style={{ fontSize: '2em' }}
              >
                <div
                  style={{
                    whiteSpace: 'nowrap',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    fontSize: '0.75rem'
                  }}
                >
                  {details?.id}
                </div>
              </Tooltip>
            </>}
        </Grid>
        <Grid
          sx={{
            width: '32px',
            height: '32px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            border: '1px solid',
            borderColor: (theme) => theme.palette.background.coveBlack02,
            borderRadius: '0px 8px 8px 0px',
            backgroundColor: (theme) => theme.palette.background.buttonBg,
          }}
        >
          <CopyButton content={details?.id} />
        </Grid>
      </Grid>
      <Grid id="status Container">
        {qelectronJobOverviewIsFetching && !details ?
          <Skeleton data-testid="qelectron_top__bar_skl" width={100} sx={{ mr: '5px' }} /> : <>
            <Box
              sx={{
                color: statusColor(details?.status),
                display: 'flex',
                fontSize: '1.125rem',
                alignItems: 'center',
                justifySelf: 'center',
              }}
            >
              {statusIcon(details?.status)}
              &nbsp;
              {statusLabel(details?.status)}
            </Box>
          </>}
      </Grid>
    </Grid>
  )
}

export default QElectronTopBar
