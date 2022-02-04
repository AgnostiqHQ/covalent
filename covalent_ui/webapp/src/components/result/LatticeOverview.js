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
import CopyButton from '../CopyButton'
import Runtime from '../results/Runtime'
import SyntaxHighlighter from '../SyntaxHighlighter'
import Heading from './Heading'

const LatticeOverview = ({ dispatchId }) => {
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
          <Typography>{result.lattice.doc}</Typography>
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
          <span>{truncateMiddle(result.results_dir, 15, 28)}</span>
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

export const ExecutorSection = ({ metadata }) => {
  const executorType = _.get(metadata, 'backend')
  const executorParams = _.omitBy(_.get(metadata, 'executor'), (v) => v === '')

  return (
    <>
      {!_.isEmpty(executorType)}
      <Heading>Executor: {executorType}</Heading>

      {!_.isEmpty(executorParams) && (
        <Typography
          sx={{
            fontSize: 'body2.fontSize',
            overflowX: 'auto',
            whiteSpace: 'nowrap',
            pb: 1,
          }}
        >
          {_.map(executorParams, (value, key) => (
            <span key={key}>
              {key} = {value}
              <br />
            </span>
          ))}
        </Typography>
      )}
    </>
  )
}

export const InputSection = ({ inputs }) => {
  if (_.isEmpty(inputs)) {
    return null
  }

  const inputSrc = _.join(
    _.map(inputs, (value, key) => `${key}=${value}`),
    ', '
  )

  return (
    <>
      <Heading>Input</Heading>
      <Paper elevation={0}>
        <SyntaxHighlighter language="python" src={inputSrc} />
      </Paper>
    </>
  )
}
export default LatticeOverview
