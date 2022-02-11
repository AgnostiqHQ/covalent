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
  AccountTreeOutlined,
  ChevronLeft,
  Edit as EditIcon,
} from '@mui/icons-material'
import {
  alpha,
  AppBar,
  Box,
  Divider,
  IconButton,
  Link,
  Paper,
  Toolbar,
  Typography,
} from '@mui/material'
import { useSelector } from 'react-redux'

import { ReactComponent as Logo } from '../../assets/covalent-full-logo.svg'
import Heading from '../result/Heading'
import { ExecutorSection, InputSection } from '../result/LatticeOverview'
import SyntaxHighlighter from '../SyntaxHighlighter'

const LatticeDrawerContents = () => {
  const preview = useSelector((state) => state.latticePreview.lattice)

  return (
    <>
      <AppBar
        position="static"
        elevation={0}
        sx={(theme) => ({
          bgcolor: alpha(theme.palette.background.default, 0.3),
        })}
      >
        <Toolbar sx={{ my: 3, mb: 2 }}>
          <Link href="/">
            <Logo />
          </Link>
        </Toolbar>
      </AppBar>

      <Box sx={{ px: 3 }}>
        {/* dispatch id */}
        <IconButton href="/" sx={{ color: 'text.disabled', mr: 1 }}>
          <ChevronLeft />
        </IconButton>

        <AccountTreeOutlined fontSize="inherit" />
        <Typography component="span" sx={{ mx: 1 }}>
          {_.get(preview, 'lattice.name')}
        </Typography>

        <PreviewStatusCard />

        <LatticePreviewOverview preview={preview} />
      </Box>
    </>
  )
}

const PreviewStatusCard = () => {
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
                display: 'flex',
                fontSize: '1.125rem',
                alignItems: 'center',
                py: 1,
              }}
            >
              <EditIcon fontSize="sm" sx={{ mr: 1 }} />
              Draft
            </Box>
          </Box>
        </Box>
      </Paper>
    </Box>
  )
}

const LatticePreviewOverview = ({ preview }) => {
  const src = _.get(preview, 'lattice.function_string', '# source unavailable')

  return (
    <>
      {/* Description */}
      {preview.lattice.doc && (
        <>
          <Heading>Description</Heading>
          <Typography fontSize="body2.fontSize">
            {preview.lattice.doc}
          </Typography>
        </>
      )}

      {/* Input */}
      <InputSection inputs={_.get(preview, 'lattice.kwargs')} />

      {/* Executor */}
      <ExecutorSection metadata={_.get(preview, 'lattice.metadata')} />

      <Divider sx={{ my: 3 }} />

      {/* Source */}
      <Heading />
      <Paper elevation={0}>
        <SyntaxHighlighter src={src} />
      </Paper>
    </>
  )
}

export default LatticeDrawerContents
