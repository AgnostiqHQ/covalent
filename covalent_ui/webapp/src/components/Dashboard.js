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
  AppBar,
  Container,
  Link,
  Paper,
  Typography,
  Toolbar,
} from '@mui/material'
import { useSelector } from 'react-redux'
import { createSelector } from '@reduxjs/toolkit'

import ResultListing from './results/ResultListing'
import { ReactComponent as Logo } from '../assets/covalent-full-logo.svg'
import { Box } from '@mui/system'
import CopyButton from './CopyButton'

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

const Dashboard = () => {
  const dispatcherAddress = useSelector(selectDispatcherAddress)

  return (
    <>
      <AppBar position="static" color="transparent" sx={{ my: 3 }}>
        <Toolbar>
          <Container>
            <Link href="/">
              <Logo />
            </Link>
          </Container>
        </Toolbar>
      </AppBar>

      <Container>
        <Paper sx={{ p: 2, mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Typography fontSize={20}>Dispatch list</Typography>

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
        </Paper>
      </Container>

      <Container>
        <ResultListing />
      </Container>
    </>
  )
}

export default Dashboard
