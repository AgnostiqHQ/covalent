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
        <Skeleton data-testid='skeleton' sx={{ height: '80px' }} />
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
