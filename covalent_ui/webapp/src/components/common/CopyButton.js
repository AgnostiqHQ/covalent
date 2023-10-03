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
  backgroundColor,
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
        onClick={(e) => {
          e.stopPropagation()
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
            padding: 0,
            '&:hover': {
              backgroundColor: backgroundColor || ''
            }
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
