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

import { useState } from 'react'
import { useSelector } from 'react-redux'
import { useParams } from 'react-router-dom'
import {
  Box,
  CircularProgress,
  IconButton,
  Paper,
  styled,
  SvgIcon,
  Tab,
  Tooltip,
  Typography,
} from '@mui/material'
import { AccountTreeOutlined, ChevronLeft } from '@mui/icons-material'
import { TabContext, TabList, TabPanel } from '@mui/lab'
import { alpha } from '@mui/material/styles'

import CopyButton from '../common/CopyButton'
import { ReactComponent as AtomSvg } from '../../assets/atom.svg'
import { selectResultProgress } from '../dispatches/ResultProgress'
import LatticeDispatchOverview from './LatticeDispatchOverview'
import { statusIcon, truncateMiddle } from '../../utils/misc'
import { LatticeOutput } from '../common/LogOutput'
import ErrorCard from '../common/ErrorCard'

const DispatchDrawerContents = () => {
  const { dispatchId } = useParams()
  const [tab, setTab] = useState('overview')

  return (
    <Box sx={{ p: 3 }}>
      {/* dispatch id */}
      <IconButton href="/" sx={{ color: 'text.disabled', mr: 1 }}>
        <ChevronLeft />
      </IconButton>

      <AccountTreeOutlined fontSize="inherit" />
      <Tooltip title={dispatchId} placement="top">
        <Typography component="span" sx={{ mx: 1 }}>
          {truncateMiddle(dispatchId, 14, 13)}
        </Typography>
      </Tooltip>

      <CopyButton content={dispatchId} size="small" title="Copy dispatch Id" />

      {/* status */}
      <LatticeStatusCard dispatchId={dispatchId} />

      {/* tabs */}
      <TabContext value={tab}>
        <CustomTabList
          variant="fullWidth"
          onChange={(e, newTab) => setTab(newTab)}
        >
          <Tab label="Overview" value="overview" />
          <Tab label="Output" value="output" />
        </CustomTabList>

        <TabPanel value="overview" sx={{ px: 0, py: 1 }}>
          <LatticeDispatchOverview dispatchId={dispatchId} />
        </TabPanel>

        <TabPanel value="output" sx={{ px: 0, py: 1 }}>
          <LatticeOutput dispatchId={dispatchId} />
          {/* <LogOutput dispatchId={dispatchId} /> */}
        </TabPanel>
      </TabContext>
    </Box>
  )
}

const CustomTabList = styled(TabList)(({ theme }) => ({
  '& .MuiTab-root': {
    textTransform: 'none',
    '&.Mui-selected': {
      color: theme.palette.text.primary,
    },
  },
  '& .MuiTabs-indicator': {
    height: 1,
    backgroundColor: theme.palette.text.primary,
  },
}))

const LatticeStatusCard = ({ dispatchId }) => {
  const { completed, total, status, label, color, error } = useSelector(
    (state) => selectResultProgress(state, dispatchId)
  )

  return (
    <Box sx={{ my: 2 }}>
      <Paper sx={{ px: 3, py: 2 }} elevation={0}>
        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: 'repeat(2, 1fr)',
          }}
        >
          {/* left column */}
          <Box sx={{ borderRight: '1px solid #29425B' }}>
            <Typography color="text.secondary" fontSize="body2.fontSize">
              Status
            </Typography>

            <Box
              sx={{
                color: `${color}.main`,
                display: 'flex',
                fontSize: '1.125rem',
                alignItems: 'center',
                py: 1,
              }}
            >
              {statusIcon(status)}
              &nbsp;
              {label}
            </Box>
          </Box>

          {/* right column */}
          <Box sx={{ justifySelf: 'end' }}>
            <Typography color="text.secondary" fontSize="body2.fontSize">
              Progress
            </Typography>

            {/* electron progress */}
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                py: 1,
              }}
            >
              <SvgIcon fontSize="inherit" sx={{ mr: 1.5 }}>
                <AtomSvg />
              </SvgIcon>

              <Typography fontSize="body2.fontSize">
                <Box
                  component="span"
                  sx={{
                    color: status === 'COMPLETED' ? 'inherit' : `${color}.main`,
                  }}
                >
                  {completed}
                </Box>
                &nbsp;/ {total}
              </Typography>

              <Box sx={{ ml: 2, position: 'relative' }}>
                <CircularProgress
                  variant="determinate"
                  sx={(theme) => ({
                    color: alpha(theme.palette[color].main, 0.2),
                  })}
                  size="2rem"
                  value={100}
                />
                <CircularProgress
                  sx={{ position: 'absolute', left: 0 }}
                  variant="determinate"
                  color={color}
                  size="2rem"
                  value={(completed * 100) / total}
                />
              </Box>
            </Box>
          </Box>
        </Box>
      </Paper>

      <ErrorCard showElectron error={error} />
    </Box>
  )
}

export default DispatchDrawerContents
