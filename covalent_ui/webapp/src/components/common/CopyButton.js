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
import { IconButton, Tooltip, Grid } from '@mui/material'
import { CheckRounded } from '@mui/icons-material'
import { ReactComponent as CopyIcon } from '../../assets/copy.svg'

const CopyButton = ({
  content,
  isBorderPresent,
  title = 'Copy',
  width,
  height,
  borderRadius,
  ...props
}) => {
  const [copied, setCopied] = useState(false)

  return (
    <Tooltip
      title={copied ? 'Copied!' : title}
      placement="right"
      data-testid="copyButton"
    >
      <IconButton
        onClick={() => {
          copy(content)
          setCopied(true)
          setTimeout(() => setCopied(false), 1200)
        }}
        disableRipple
        sx={{ color: 'text.tertiary' }}
        {...props}
      >
        <Grid
          sx={{
            border: isBorderPresent ? '1px solid #303067' : null,
            borderRadius: borderRadius ? borderRadius : '8px',
            width: width ? width : '32px',
            height: height ? height : '32px',
          }}
          container
          direction="row"
          justifyContent="center"
          alignItems="center"
        >
          {copied ? (
            <CheckRounded
              fontSize="inherit"
              data-testid="copiedIcon"
              style={{
                margin: 'auto',
                width: width ? width / 2 : null,
                height: height ? height / 2 : null,
              }}
            />
          ) : (
            <CopyIcon
              style={{
                margin: 'auto',
                width: width ? width / 2 : '16px',
                height: height ? height / 2 : '16px',
              }}
              data-testid="copyIcon"
            />
          )}
        </Grid>
      </IconButton>
    </Tooltip>
  )
}

export default CopyButton
