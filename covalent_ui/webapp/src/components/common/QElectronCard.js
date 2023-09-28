/* eslint-disable react/jsx-no-comment-textnodes */
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

import { Button, Grid, Typography, SvgIcon, Chip } from '@mui/material'
import React from 'react'
import { ReactComponent as ViewSvg } from '../../assets/qelectron/view.svg'
import { ReactComponent as QelectronSvg } from '../../assets/qelectron/qelectron.svg'
import { formatQElectronTime } from '../../utils/misc'

const QElectronCard = (props) => {
  const { qElectronDetails, toggleQelectron, openQelectronDrawer } = props

  const handleButtonClick = (e) => {
    e.stopPropagation()
    toggleQelectron()
  }

  return (
    //main container
    <Grid
      onClick={handleButtonClick}
      conatiner
      mt={5}
      p={2}
      sx={{
        backgroundColor: (theme) => theme.palette.background.default,
        border: '1px solid',
        borderRadius: '8px',
        cursor: 'pointer',
        borderColor: (theme) => theme.palette.primary.grey,
        '&:hover': {
          backgroundColor: (theme) => theme.palette.background.coveBlack02,
        },
      }}
      data-testid="QelectronCard-grid"
    >
      <Grid
        item
        xs={12}
        container
        direction="row"
        alignItems="center"
        justifyContent="space-between"
      >
        <Grid item container xs={8} direction="row" alignItems="center">
          <Typography sx={{ fontSize: '16px', mr: 1 }}>
            qelectrons
          </Typography>
          <span style={{ flex: 'none' }}>
            <SvgIcon
              aria-label="view"
              sx={{
                display: 'flex',
                justifyContent: 'flex-end',
                mr: 0,
                mt: 0.8,
                pr: 0,
              }}
            >
              <QelectronSvg />
            </SvgIcon>
          </span>
          <Chip
            sx={{
              height: '22px',
              ml: 0.1,
              mb: 0.2,
              fontSize: '0.75rem',
              color: '#FFFFFF',
            }}
            label="BETA"
            variant="outlined"
          />
        </Grid>
        <Button
          sx={{
            textTransform: 'capitalize',
            height: '2rem',
            width: '4.5rem',
            backgroundColor: (theme) => theme.palette.primary.blue02,
            color: (theme) => theme.palette.text.primary,
            '&:hover': {
              backgroundColor: (theme) => theme.palette.primary.blue02,
            },
          }}
        >
          <span style={{ flex: 'none' }}>
            <SvgIcon
              aria-label="view"
              sx={{
                display: 'flex',
                justifyContent: 'flex-end',
                mr: 0,
                mt: 1.5,
                pr: 0,
              }}
            >
              <ViewSvg />
            </SvgIcon>
          </span>
          <span style={{ flex: 'none', pl: 0, ml: 0, fontSize: '12px' }}>
            {!openQelectronDrawer ? 'Open' : 'Close'}
          </span>
        </Button>
      </Grid>
      <Grid
        item
        xs={12}
        mt={3}
        container
        direction="row"
        alignItems="center"
        justifyContent="space-between"
      >
        <Grid item sx={{ display: 'flex', flexDirection: 'column' }}>
          <Typography sx={{ fontSize: '12px' }}>Quantum Calls</Typography>
          <Typography sx={{ fontSize: '14px' }}>
            {qElectronDetails.total_quantum_calls}
          </Typography>
        </Grid>
        <Grid item sx={{ display: 'flex', flexDirection: 'column' }}>
          <Typography sx={{ fontSize: '12px' }}>Avg Time Of Call</Typography>
          <Typography sx={{ fontSize: '14px' }}>
            {formatQElectronTime(qElectronDetails.avg_quantum_calls)}
          </Typography>
        </Grid>
      </Grid>
    </Grid>
  )
}

export default QElectronCard
