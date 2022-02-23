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
import { Divider, Paper, Tooltip, Typography } from '@mui/material'
import { useSelector } from 'react-redux'

import { formatDate, truncateMiddle } from '../../utils/misc'
import CopyButton from '../common/CopyButton'
import Runtime from '../dispatches/Runtime'
import SyntaxHighlighter from '../common/SyntaxHighlighter'
import Heading from '../common/Heading'
import InputSection from '../common/InputSection'
import ExecutorSection from '../common/ExecutorSection'

const LatticeDispatchOverview = ({ dispatchId }) => {
  const result = useSelector((state) => state.results.cache[dispatchId])

  const src = _.get(result, 'lattice.function_string', '# source unavailable')
  const showResult = result.status === 'COMPLETED'

  const hasStarted = !!result.start_time
  const hasEnded = !!result.end_time

  return (
    <>
      {/* Description */}
      {result.lattice.doc && (
        <>
          <Heading>Description</Heading>
          <Typography fontSize="body2.fontSize">
            {result.lattice.doc}
          </Typography>
        </>
      )}

      {/* Start/end times */}
      {hasStarted && (
        <>
          <Heading>Started{hasEnded ? ' - Ended' : ''}</Heading>
          <Typography fontSize="body2.fontSize">
            {formatDate(result.start_time)}
            {hasEnded && ` - ${formatDate(result.end_time)}`}
          </Typography>
        </>
      )}

      {/* Runtime */}
      <Heading>Runtime</Heading>
      <Runtime
        sx={{ fontSize: 'body2.fontSize' }}
        startTime={result.start_time}
        endTime={result.end_time}
      />

      {/* Directory */}
      <Heading>Directory</Heading>
      <Typography sx={{ overflowWrap: 'anywhere', fontSize: 'body2.fontSize' }}>
        <Tooltip title={result.results_dir} enterDelay={500}>
          <span>{truncateMiddle(result.results_dir, 15, 25)}</span>
        </Tooltip>
        <CopyButton
          content={result.results_dir}
          size="small"
          title="Copy results directory"
        />
      </Typography>

      {/* Input */}
      <InputSection inputs={_.get(result, 'lattice.kwargs')} />

      {/* Result */}
      {showResult && (
        <>
          <Heading>Result</Heading>
          <Paper elevation={0}>
            <SyntaxHighlighter language="python" src={result.result} />
          </Paper>
        </>
      )}

      {/* Executor */}
      <ExecutorSection metadata={_.get(result, 'lattice.metadata')} />

      <Divider sx={{ my: 3 }} />

      {/* Source */}
      <Heading />
      <Paper elevation={0}>
        <SyntaxHighlighter src={src} />
      </Paper>
    </>
  )
}

export default LatticeDispatchOverview
