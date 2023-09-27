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
