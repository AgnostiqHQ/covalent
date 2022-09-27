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
import { Divider, Paper, Tooltip, Typography, Skeleton } from '@mui/material'
import { useSelector, useDispatch } from 'react-redux'
import React, { useEffect } from 'react'
import { formatDate, truncateMiddle } from '../../utils/misc'
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
import { isDemo } from '../../utils/demo/setup'

const LatticeDispatchOverview = ({ dispatchId, latDetails, isFetching }) => {
  const result = latDetails
  const dispatch = useDispatch()
  const drawerInput = useSelector((state) => state.latticeResults.latticeResultsData[dispatchId].latticeInput)
  const drawerInputListFetching = useSelector(
    (state) => state.latticeResults.latticeInputList.isFetching
  )
  const drawerResult = useSelector(
    (state) => state.latticeResults.latticeResultsData[dispatchId].latticeResult
  )
  const drawerResultListFetching = useSelector(
    (state) => state.latticeResults.latticeResultsList.isFetching
  )
  const drawerFunctionString = useSelector(
    (state) => state.latticeResults.latticeResultsData[dispatchId].latticeFunctionString
  )
  const drawerFunctionStringListFetching = useSelector(
    (state) => state.latticeResults.latticeFunctionStringList.isFetching
  )
  const drawerExecutorDetail = useSelector(
    (state) => state.latticeResults.latticeResultsData[dispatchId].latticeExecutor
  )
  const callSocketApi = useSelector((state) => state.common.callSocketApi)

  useEffect(() => {
    if (!isDemo) {
      dispatch(latticeResults({ dispatchId, params: 'result' }))
      dispatch(latticeFunctionString({ dispatchId, params: 'function_string' }))
      dispatch(latticeInput({ dispatchId, params: 'inputs' }))
      dispatch(latticeExecutorDetail({ dispatchId, params: 'executor' }))
    }
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
          {isFetching ? (
            <Skeleton />
          ) : (
            <Typography fontSize="body2.fontSize">
              {formatDate(result?.started_at)}
              {hasEnded && ` - ${formatDate(result?.ended_at)}`}
            </Typography>
          )}
        </>
      )}

      {/* Runtime */}
      <Heading>Runtime</Heading>
      {isFetching ? (
        <Skeleton />
      ) :
        (
          <Runtime startTime={result?.started_at} endTime={result?.ended_at} />
        )}

      {/* Directory */}
      <Heading>Directory</Heading>
      {isFetching ? (
        <Skeleton />
      ) : (
        <Typography
          sx={{ overflowWrap: 'anywhere', fontSize: 'body2.fontSize' }}
        >
          <Tooltip title={result?.directory} enterDelay={500}>
            <span>{truncateMiddle(result?.directory, 15, 20)}</span>
          </Tooltip>
          <CopyButton
            isBorderPresent
            content={result?.directory}
            size="small"
            title="Copy results directory"
          />
        </Typography>
      )}

      {/* Input */}
      {drawerInput && (
        <InputSection
          isFetching={
            drawerInputListFetching && Object.keys(drawerInput).length === 0
          }
          sx={() => ({ cursor: 'pointer' })}
          inputs={drawerInput}
        />
      )}


      {/* Result */}
      {drawerResult && result.status === 'COMPLETED' && (
        <>
          <ResultSection
            isFetching={
              drawerResultListFetching && Object.keys(drawerResult).length === 0
            }
            sx={() => ({ cursor: 'pointer' })}
            results={drawerResult}
          />
        </>
      )}

      {/* Executor */}
      {drawerExecutorDetail && (
        <ExecutorSection
          isFetching={
            Object.keys(drawerExecutorDetail).length === 0
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
        <Paper elevation={0}>
          <SyntaxHighlighter src={drawerFunctionString.data} />
        </Paper>
      )}
    </div>
  )
}

export default LatticeDispatchOverview
