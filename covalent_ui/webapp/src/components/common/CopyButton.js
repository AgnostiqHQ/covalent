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
import copy from 'copy-to-clipboard'
import { IconButton, Tooltip } from '@mui/material'
import { ContentCopyRounded, CheckRounded } from '@mui/icons-material'

const CopyButton = ({ content, title = 'Copy', ...props }) => {
  const [copied, setCopied] = useState(false)

  return (
    <Tooltip title={copied ? 'Copied!' : title} placement="right">
      <IconButton
        onClick={(e) => {
          copy(content)
          setCopied(true)
          setTimeout(() => setCopied(false), 1200)
          e.stopPropagation()
        }}
        sx={{ color: 'text.secondary' }}
        {...props}
      >
        {copied ? (
          <CheckRounded fontSize="inherit" />
        ) : (
          <ContentCopyRounded fontSize="inherit" />
        )}
      </IconButton>
    </Tooltip>
  )
}

export default CopyButton
