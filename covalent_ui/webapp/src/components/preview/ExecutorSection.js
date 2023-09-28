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

import _ from 'lodash'
import { Paper } from '@mui/material'
import React from 'react'
import Heading from '../common/Heading'
import SyntaxHighlighter from '../common/SyntaxHighlighter'

const ExecutorSection = ({ isFetching, metadata, ...props }) => {
  const executorType = _.get(metadata, 'executor_name')
  const executorParams = _.omitBy(_.get(metadata, 'executor'), (v) => v === '')
  const src = _.join(
    _.map(executorParams, (value, key) => `${key}: ${value}`),
    '\n'
  )
  return (
    <>
      <Heading data-testid="executorSection">
        Executor: <strong>{executorType}</strong>
      </Heading>
      {src && (
        <Paper elevation={0} {...props}>
          <SyntaxHighlighter language="json" src={src} />
        </Paper>
      )}
    </>
  )
}

export default ExecutorSection
