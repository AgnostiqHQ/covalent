/*
 * Copyright 2022 Agnostiq Inc.
 * Note: This file is subject to a proprietary license agreement entered into between
 * you (or the person or organization that you represent) and Agnostiq Inc. Your rights to
 * access and use this file is subject to the terms and conditions of such agreement.
 * Please ensure you carefully review such agreements and, if you have any questions
 * please reach out to Agnostiq at: [support@agnostiq.com].
 */
import React from 'react'
import { Grid, Typography, Paper } from '@mui/material'
import theme from '../../utils/theme'
import SyntaxHighlighter from '../common/SyntaxHighlighter'

const Overview = (props) => {
  const code = `tensor([0.224,0.2213,.1214])`
  const { details } = props
  return (
    <>
      {' '}
      <Typography
        px={2}
        sx={{
          color: (theme) => theme.palette.text.primary,
          fontSize: theme.typography.sidebarh2,
          fontWeight: 'bold',
        }}
      >
        Execution Details
      </Typography>
      <Grid container px={2} py={1} direcction="row">
        <Grid id="leftGrid" item xs={6}>
          <Typography
            sx={{
              fontSize: theme.typography.sidebarh3,
              mt: 2,
              color: (theme) => theme.palette.text.tertiary,
            }}
          >
            Backend
          </Typography>
          <Typography
            sx={{
              fontSize: theme.typography.sidebarh2,
              mt: 1,
              color: (theme) => theme.palette.text.primary,
            }}
          >
            {details.backend}
          </Typography>
          <Typography
            sx={{
              fontSize: theme.typography.sidebarh3,
              mt: 2,
              color: (theme) => theme.palette.text.tertiary,
            }}
          >
            Time Elapsed
          </Typography>
          <Typography
            sx={{
              fontSize: theme.typography.sidebarh2,
              mt: 1,
              color: (theme) => theme.palette.text.primary,
            }}
          >
            {details.time}
          </Typography>
          <Typography
            sx={{
              fontSize: theme.typography.sidebarh3,
              mt: 2,
              color: (theme) => theme.palette.text.tertiary,
            }}
          >
            Start time - End time
          </Typography>
          <Typography
            sx={{
              fontSize: theme.typography.sidebarh2,
              mt: 1,
              color: (theme) => theme.palette.text.primary,
            }}
          >
            {details.start_time} -{details.end_time}
          </Typography>
        </Grid>
        <Grid
          id="rightGrid"
          item
          xs={6}
          sx={{ display: 'flex', alignItems: 'center' }}
          pt={1}
        >
          <Paper
            elevation={0}
            sx={(theme) => ({
              bgcolor: theme.palette.background.outRunBg,
            })}
          >
            <SyntaxHighlighter src={code} preview />
          </Paper>
        </Grid>
      </Grid>
    </>
  )
}

export default Overview
