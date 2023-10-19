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

import * as React from 'react'
import Box from '@mui/material/Box'
import Typography from '@mui/material/Typography'
import Modal from '@mui/material/Modal'
import { Grid, SvgIcon } from '@mui/material'
import { ReactComponent as CloseIcon } from '../../assets/close.svg'
import PrimaryButton from '../common/PrimaryButton'

export default function DialogBox({
  totalItems,
  openDialogBox,
  setOpenDialogBox,
  icon,
  title,
  handler,
  message,
  handleClose,
  handlePopClose
}) {

  return (
    <Modal
      open={openDialogBox}
      onClose={handleClose}
      aria-labelledby="modal-modal-title"
      aria-describedby="modal-modal-description"
      data-testid="dialogBox"
    >
      <Box
        data-testid="dialogbox"
        sx={{
          position: 'absolute',
          top: '40%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          minWidth: 500,
          bgcolor: 'background.paper',
          border: '1px solid',
          borderColor: (theme) => theme.palette.primary.blue04,
          borderRadius: '24px',
          boxShadow: 24,
          p: 2,
          '&:focus': {
            outline: 'none',
          },
        }}
      >
        <Grid
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
          }}
        >
          <Grid
            sx={{ display: 'flex', flexDirection: 'row', alignItems: 'center' }}
          >
            <SvgIcon
              data-testid="dialogIcon"
              component={icon}
              style={{ fontSize: '30px' }}
            />
            <Typography
              sx={{
                paddingBottom: '5px',
                paddingLeft: '3px',
                fontWeight: 'bold',
              }}
              color="textPrimary"
              variant="subtitle2"
              data-testid="messageTitle"
            >
              {title}
            </Typography>
          </Grid>

          <CloseIcon
            data-testid="closeIcon"
            style={{
              marginTop: '3px',
              width: '10px',
              height: '10px',
              cursor: 'pointer',
            }}
            onClick={handleClose}
          />
        </Grid>
        <Grid sx={{ display: 'flex' }} mt={2}>
          <Typography
            sx={{ paddingBottom: '5px', paddingLeft: '4px' }}
            color="textPrimary"
            variant="subtitle2"
            data-testid="message"
          >
            {message}
          </Typography>
        </Grid>
        <Grid
          container
          display="flex"
          justifyContent="flex-end"
          spacing={1}
          mt={2}
          sx={{ maxWidth: '100%' }}
        >
          <Grid item>
            <PrimaryButton
              handler={handlePopClose}
              title="Exit without saving"
              hoverColor={(theme) => theme.palette.primary.dark}
            />
          </Grid>
          <Grid item>
            <PrimaryButton
              bgColor={(theme) => theme.palette.primary.dark}
              hoverColor="#403cff"
              // title={title}
              title="Save & exit"
              handler={handler}
            />
          </Grid>
        </Grid>
      </Box>
    </Modal>
  )
}
