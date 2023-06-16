/*
 * Copyright 2022 Agnostiq Inc.
 * Note: This file is subject to a proprietary license agreement entered into between
 * you (or the person or organization that you represent) and Agnostiq Inc. Your rights to
 * access and use this file is subject to the terms and conditions of such agreement.
 * Please ensure you carefully review such agreements and, if you have any questions
 * please reach out to Agnostiq at: [support@agnostiq.com].
 */
import { Grid, Paper } from '@mui/material'
import React from 'react'
import SyntaxHighlighter from '../common/SyntaxHighlighter'
import { useSelector } from 'react-redux';

const Executor = (props) => {
  const { code } = props
  const qelectronJobOverviewIsFetching = useSelector(
    (state) => state.electronResults.qelectronJobOverviewList.isFetching
  )
  return (
    <Grid px={2}>
      <Paper
        elevation={0}
        sx={(theme) => ({
          bgcolor: theme.palette.background.outRunBg,
        })}
      >
        {' '}
        <SyntaxHighlighter src={code} preview fullwidth isFetching={qelectronJobOverviewIsFetching} />
      </Paper>
    </Grid>
  )
}

export default Executor
