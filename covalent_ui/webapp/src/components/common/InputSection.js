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
import { Paper, Skeleton } from '@mui/material'

import Heading from './Heading'
import SyntaxHighlighter from './SyntaxHighlighter'

const InputSection = ({ isFetching, inputs, preview, ...props }) => {
  const inputSrc = preview
    ? _.join(
      _.map(inputs, (value, key) => `${key}: ${value}`),
      '\n'
    )
    : inputs
  return (
    <>
      {isFetching ? (
        <Skeleton sx={{ height: '80px' }} />
      ) : (
        inputSrc && (
          <>
            <Heading>Input</Heading>
            <Paper elevation={0} {...props}>
              <SyntaxHighlighter language="json" src={inputSrc} />
            </Paper>
          </>)
      )}
    </>
  )
}

export default InputSection
