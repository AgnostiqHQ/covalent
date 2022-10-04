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
import _ from 'lodash'
import {
  Paper,
  Skeleton,
  Tooltip,
  tooltipClasses
} from '@mui/material'
import copy from 'copy-to-clipboard'
import { styled } from '@mui/material/styles'
import Heading from './Heading'
import SyntaxHighlighter from './SyntaxHighlighter'

const ResultTooltip = styled(({ className, ...props }) => (
  <Tooltip {...props} classes={{ popper: className }} />
))(() => ({
  [`& .${tooltipClasses.tooltip}`]: {
    // customize tooltip
    maxWidth: 500,
  },
}))

const ResultSection = ({ isFetching, results, preview, ...props }) => {
  const [copied, setCopied] = useState(false)
  const resultSrc = preview
    ? _.join(
      _.map(results.data, (value, key) => `${key}: ${value}`),
      '\n'
    )
    : results.data
  return (
    <>
      {isFetching ? (
        <Skeleton sx={{ height: '80px' }} />
      ) : (
        resultSrc && (
          <ResultTooltip title={copied ? 'Python object copied' : 'Copy python object'} arrow>
            <div onClick={
              () => {
                copy(results?.python_object)
                setCopied(true)
                setTimeout(() => setCopied(false), 1200)
              }
            } >
              <Heading data-testid='resultSection'>Result</Heading>
              <Paper elevation={0} {...props} >
                <SyntaxHighlighter language="json" src={resultSrc} />
              </Paper>
            </div>
          </ResultTooltip>
        )
      )}
    </>
  )
}

export default ResultSection
