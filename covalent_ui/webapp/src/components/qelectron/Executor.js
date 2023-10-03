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

import { Grid, Paper } from '@mui/material'
import React from 'react'
import SyntaxHighlighter from '../common/SyntaxHighlighter'
import { useSelector } from 'react-redux';

const Executor = (props) => {
  const { code } = props
  const qelectronJobOverviewIsFetching = useSelector(
    (state) => state.electronResults.qelectronJobOverviewList.isFetching
  )
  return (
    <Grid px={2} data-testid="Executor-grid">
      <Paper
        elevation={0}
        sx={(theme) => ({
          bgcolor: theme.palette.background.outRunBg,
        })}
      >
        {' '}
        <SyntaxHighlighter src={code} preview fullwidth isFetching={qelectronJobOverviewIsFetching} />
      </Paper>
    </Grid>
  )
}

export default Executor
