/*
 * Copyright 2022 Agnostiq Inc.
 * Note: This file is subject to a proprietary license agreement entered into between
 * you (or the person or organization that you represent) and Agnostiq Inc. Your rights to
 * access and use this file is subject to the terms and conditions of such agreement.
 * Please ensure you carefully review such agreements and, if you have any questions
 * please reach out to Agnostiq at: [support@agnostiq.com].
 */

import { Grid, Typography, SvgIcon } from '@mui/material'
import React from 'react'
import theme from '../../utils/theme'
import { ReactComponent as QelectronSvg } from '../../assets/qelectron/circuit.svg'

const SingleGrid = ({ title, value }) => {
  return (
    <Grid>
      <Typography
        sx={{
          fontSize: theme.typography.sidebarh3,
          color: (theme) => theme.palette.text.tertiary,
        }}
      >
        {title}
      </Typography>
      <Typography
        sx={{
          fontSize: theme.typography.sidebarh2,
          color: (theme) => theme.palette.text.primary,
        }}
      >
        {value}
      </Typography>
    </Grid>
  )
}

const Circuit = ({ circuitDetails }) => {
  return (
    <Grid
      px={4}
      pt={2}
      container
      flexDirection="column
    "
    >
      <Grid id="topGrid" item container xs={10} justifyContent="space-between">
        <SingleGrid title="No. of Qbits" value={circuitDetails.no_of_qbits} />
        <SingleGrid title="No.1 Qbit Gates" value={circuitDetails.no1_gates} />
        <SingleGrid title="No.2 Qbit Gates" value={circuitDetails.no2_gates} />
        <SingleGrid title="Depth" value={circuitDetails.depth} />
      </Grid>
      <Grid id="bottomGrid" mt={3}>
        <Typography
          sx={{
            fontSize: theme.typography.sidebarh3,
            color: (theme) => theme.palette.text.tertiary,
          }}
        >
          Circuit
        </Typography>
        <Grid
          mt={2}
          container
          justifyContent="center"
          sx={{ width: '700px', height: '100px' }}
        >
          <span
            style={{
              width: '100%',
              height: '100%',
              display: 'flex',
              justifyContent: 'flex-end',
            }}
          >
            <SvgIcon
              aria-label="view"
              sx={{
                width: '100%',
                height: '100%',
                color: (theme) => theme.palette.text.primary,
              }}
              component={QelectronSvg}
              viewBox="0 0 700 100" // Specify the viewBox to match the desired container size
            />
          </span>
        </Grid>
      </Grid>
    </Grid>
  )
}

export default Circuit
