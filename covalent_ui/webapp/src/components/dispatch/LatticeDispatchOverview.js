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
import {
  Divider,
  Paper,
  Tooltip,
  Typography,
  Skeleton,
  Grid,
} from '@mui/material'
import { useSelector, useDispatch } from 'react-redux'
import React, { useEffect } from 'react'
import { formatDate, truncateMiddle, getLocalStartTime } from '../../utils/misc'
import CopyButton from '../common/CopyButton'
import SyntaxHighlighter from '../common/SyntaxHighlighter'
import Heading from '../common/Heading'
import InputSection from '../common/InputSection'
import ResultSection from '../common/ResultSection'
import ExecutorSection from '../common/ExecutorSection'
import {
  latticeResults,
  latticeFunctionString,
  latticeInput,
  latticeExecutorDetail,
} from '../../redux/latticeSlice'
import Runtime from '../dispatches/Runtime'

const LatticeDispatchOverview = ({ dispatchId, latDetails, isFetching }) => {
  const result = latDetails
  const dispatch = useDispatch()
  const drawerInput = useSelector((state) => state.latticeResults.latticeInput)
  const drawerInputListFetching = useSelector(
    (state) => state.latticeResults.latticeInputList.isFetching
  )
  const drawerResult = useSelector(
    (state) => state.latticeResults.latticeResult
  )
  const drawerResultListFetching = useSelector(
    (state) => state.latticeResults.latticeResultsList.isFetching
  )
  const drawerFunctionString = useSelector(
    (state) => state.latticeResults.latticeFunctionString
  )
  const drawerFunctionStringListFetching = useSelector(
    (state) => state.latticeResults.latticeFunctionStringList.isFetching
  )
  const drawerExecutorDetail = useSelector(
    (state) => state.latticeResults.latticeExecutorDetail
  )
  const drawerExecutorDetailListFetching = useSelector(
    (state) => state.latticeResults.latticeExecutorDetailList.isFetching
  )
  const callSocketApi = useSelector((state) => state.common.callSocketApi)

  useEffect(() => {
    dispatch(latticeResults({ dispatchId, params: 'result' }))
    dispatch(latticeFunctionString({ dispatchId, params: 'function_string' }))
    dispatch(latticeInput({ dispatchId, params: 'inputs' }))
    dispatch(latticeExecutorDetail({ dispatchId, params: 'executor' }))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [callSocketApi])
  const hasStarted = !!result?.started_at
  const hasEnded = !!result?.ended_at

  return (
    <div data-testid="dispatchoverview">
      {/* Description */}
      {result?.description &&
        (isFetching ? (
          <Skeleton />
        ) : (
          <>
            <Heading>Description</Heading>
            <Typography fontSize="body2.fontSize">
              {result?.description}
            </Typography>
          </>
        ))}
      {/* Start/end times */}
      {hasStarted && (
        <>
          <Heading>Started{hasEnded ? ' - Ended' : ''}</Heading>
          {!result && isFetching ? (
            <Skeleton />
          ) : (
            <Typography fontSize="body2.fontSize">
              {formatDate(getLocalStartTime(result?.started_at))}
              {hasEnded &&
                ` - ${formatDate(getLocalStartTime(result?.ended_at))}`}
            </Typography>
          )}
        </>
      )}

      {/* Runtime */}
      {result?.started_at ? (
        <>
          <Heading>Runtime</Heading>
          {!result && isFetching ? (
            <Skeleton />
          ) : (
            <Runtime
              startTime={result?.started_at}
              endTime={result?.ended_at}
            />
          )}
        </>
      ) : (
        <></>
      )}

      {/* Directory */}
      <Heading>Directory</Heading>
      {!result && isFetching ? (
        <Skeleton />
      ) : (
        <Typography
          sx={{
            overflowWrap: 'anywhere',
            fontSize: 'body2.fontSize',
            display: 'flex',
            alignItems: 'center',
          }}
        >
          <Tooltip title={result?.directory} enterDelay={500}>
            <span>{truncateMiddle(result?.directory, 15, 18)}</span>
          </Tooltip>
          <Grid sx={{ ml: '8px' }}>
            <CopyButton
              isBorderPresent
              content={result?.directory}
              size="small"
              title="Copy results directory"
            />
          </Grid>
        </Typography>
      )}

      {/* Input */}
      {Object.keys(drawerInput).length !== 0 && (
        <InputSection
          sx={(theme) => ({
            bgcolor: theme.palette.background.outRunBg,
            cursor: 'pointer',
          })}
          isFetching={
            drawerInputListFetching && Object.keys(drawerInput).length === 0
          }
          inputs={drawerInput}
        />
      )}

      {/* Result */}
      {Object.keys(drawerResult).length !== 0 &&
        result.status === 'COMPLETED' && (
          <>
            <ResultSection
              isFetching={
                drawerResultListFetching &&
                Object.keys(drawerResult).length === 0
              }
              sx={(theme) => ({
                bgcolor: theme.palette.background.outRunBg,
                cursor: 'pointer',
              })}
              results={drawerResult}
            />
          </>
        )}

      {/* Executor */}
      {Object.keys(drawerExecutorDetail).length !== 0 && (
        <ExecutorSection
          sx={(theme) => ({ bgcolor: theme.palette.background.outRunBg })}
          isFetching={
            Object.keys(drawerExecutorDetail).length === 0 &&
            drawerExecutorDetailListFetching
          }
          metadata={drawerExecutorDetail}
        />
      )}

      <Divider sx={{ my: 3 }} />

      {/* Source */}

      <Heading />

      {Object.keys(drawerFunctionString).length === 0 &&
      drawerFunctionStringListFetching ? (
        <Skeleton height={100} />
      ) : (
        <Paper
          elevation={0}
          sx={(theme) => ({ bgcolor: theme.palette.background.outRunBg })}
        >
          <SyntaxHighlighter src={drawerFunctionString.data} />
        </Paper>
      )}
    </div>
  )
}

export default LatticeDispatchOverview
