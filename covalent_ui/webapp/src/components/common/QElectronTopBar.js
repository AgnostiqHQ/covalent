/*
 * Copyright 2022 Agnostiq Inc.
 * Note: This file is subject to a proprietary license agreement entered into between
 * you (or the person or organization that you represent) and Agnostiq Inc. Your rights to
 * access and use this file is subject to the terms and conditions of such agreement.
 * Please ensure you carefully review such agreements and, if you have any questions
 * please reach out to Agnostiq at: [support@agnostiq.com].
 */

import { Grid, IconButton, Typography, Box } from '@mui/material'
import React from 'react'
import { ChevronRight } from '@mui/icons-material'
import { statusIcon, statusColor, statusLabel } from '../../utils/misc'
import CopyButton from './CopyButton'

const QElectronTopBar = (props) => {
  const { details, toggleQelectron } = props
  return (
    <Grid
      container
      id="qelectronTopbar"
      flexDirection="row"
      alignItems="center"
      justifyContent="space-between"
      p={1.5}
      sx={{
        background: (theme) => theme.palette.background.qelectronbg,
        borderRadius: '8px',
      }}
    >
      <Grid item xs={6} container flexDirection="row" alignItems="center">
        <IconButton
          onClick={() => toggleQelectron()}
          data-testid="backbtn"
          sx={{
            color: 'text.disabled',
            cursor: 'pointer',
            mr: 1,
            backgroundColor: (theme) => theme.palette.background.buttonBg,
            borderRadius: '10px',
            width: '32px',
            height: '32px',
          }}
        >
          <ChevronRight />
        </IconButton>
        <Typography fontSize='sidebarh2' mr={2}>{details.title}</Typography>
        <Grid
          sx={{
            width: '32px',
            height: '32px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            border: '1px solid',
            borderColor: (theme) => theme.palette.background.coveBlack02,
            borderRadius: '8px 0px 0px 8px',
            backgroundColor: (theme) => theme.palette.background.buttonBg,
          }}
        >
          id
        </Grid>
        <Grid
          sx={{
            width: '32px',
            height: '32px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            border: '1px solid',
            borderColor: (theme) => theme.palette.background.coveBlack02,
            borderRadius: '0px 8px 8px 0px',
            backgroundColor: (theme) => theme.palette.background.buttonBg,
          }}
        >
          <CopyButton content={details.title} />
        </Grid>
      </Grid>
      <Grid id="status Container">
        <Box
          sx={{
            color: statusColor(details.status),
            display: 'flex',
            fontSize: '1.125rem',
            alignItems: 'center',
            justifySelf: 'center',
          }}
        >
          {statusIcon(details.status)}
          &nbsp;
          {statusLabel(details.status)}
        </Box>
      </Grid>
    </Grid>
  )
}

export default QElectronTopBar
