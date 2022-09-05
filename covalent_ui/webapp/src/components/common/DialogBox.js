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

import * as React from 'react'
import Box from '@mui/material/Box'
import Typography from '@mui/material/Typography'
import Modal from '@mui/material/Modal'
import { Grid, SvgIcon } from '@mui/material'
import { ReactComponent as CloseIcon } from '../../assets/close.svg'
import PrimaryButton from './PrimaryButton'

export default function DialogBox({
  totalItems,
  openDialogBox,
  setOpenDialogBox,
  icon,
  title,
  handler,
  message,
}) {
  const handleClose = () => setOpenDialogBox(false)
  
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
              style={{ fontSize: '25px' }}
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
              {title} {totalItems} {totalItems === 1 ? 'item ?' : 'items ?'}
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
            {message} {totalItems} {totalItems === 1 ? 'item' : totalItems === 0 || totalItems===undefined ? '' : 'items'} ?
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
              handler={handleClose}
              title="Cancel"
              hoverColor={(theme) => theme.palette.primary.dark}
            />
          </Grid>
          <Grid item>
            <PrimaryButton
              bgColor={(theme) => theme.palette.primary.dark}
              hoverColor="#403cff"
              title={title}
              handler={handler}
            />
          </Grid>
        </Grid>
      </Box>
    </Modal>
  )
}
