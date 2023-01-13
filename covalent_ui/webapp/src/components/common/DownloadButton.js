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

import { IconButton, Tooltip, Grid } from '@mui/material'
import { ReactComponent as DownloadIcon } from '../../assets/download.svg'

const DownloadButton = ({
  content,
  isBorderPresent,
  onClick,
  disabled,
  ...props
}) => {
  return (
    <Tooltip title={props.title} placement="right">
      <IconButton
        onClick={onClick}
        disabled={disabled}
        disableRipple
        sx={{ color: 'text.tertiary' }}
        {...props}
      >
        <Grid
          sx={{
            border: isBorderPresent ? '1px solid #303067' : null,
            borderRadius: '8px',
            width: '32px',
            height: '32px',
          }}
          container
          direction="row"
          justifyContent="center"
          alignItems="center"
        >
          <DownloadIcon
            style={{ margin: 'auto', width: '16px', height: '16px' }}
            data-testid="downloadButton"
          />
        </Grid>
      </IconButton>
    </Tooltip>
  )
}

export default DownloadButton
