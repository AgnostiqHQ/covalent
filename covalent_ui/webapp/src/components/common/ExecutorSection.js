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
import { Paper } from '@mui/material'
import React from 'react'
import Heading from './Heading'
import SyntaxHighlighter from './SyntaxHighlighter'

const ExecutorSection = ({ isFetching, metadata, ...props }) => {
  const executorType = _.get(metadata, 'executor_name')
  const executor_details = _.get(metadata, 'executor_details')
  const src = executor_details && _.join(
    _.map(executor_details?.attributes, (value, key) => `${key}: ${value}`),
    '\n'
  )
  return (
    <>
      {!isFetching && (
        <Heading data-testid="executorSection">
          Executor: <strong>{executorType}</strong>
        </Heading>
      )}
      {executor_details && !isFetching && (
        <Paper elevation={0} {...props}>
          <SyntaxHighlighter language="yaml" src={src} />
        </Paper>
      )}
    </>
  )
}

export default ExecutorSection
