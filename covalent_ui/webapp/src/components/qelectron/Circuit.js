/*
 * Copyright 2022 Agnostiq Inc.
 * Note: This file is subject to a proprietary license agreement entered into between
 * you (or the person or organization that you represent) and Agnostiq Inc. Your rights to
 * access and use this file is subject to the terms and conditions of such agreement.
 * Please ensure you carefully review such agreements and, if you have any questions
 * please reach out to Agnostiq at: [support@agnostiq.com].
 */

import { Grid, Typography, SvgIcon, Box, Modal, Paper } from '@mui/material'
import React, { useState } from 'react'
import theme from '../../utils/theme'
import { ReactComponent as QelectronSvg } from '../../assets/qelectron/circuit.svg'
import { ReactComponent as CircuitLarge } from '../../assets/qelectron/circuit-large.svg'
import { ReactComponent as CloseSvg } from '../../assets/close.svg'
import SyntaxHighlighter from '../common/SyntaxHighlighter'

const styles = {
  outline: 'none',
  position: 'absolute',
  top: '50%',
  left: '50%',
  transform: 'translate(-50%, -50%)',
  p: 4,
  width: ' 95%',
  height: '95%',
  bgcolor: '#0B0B11E5',
  border: '2px solid transparent',
  boxShadow: 24,
}

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
        {value ? value : '-'}
      </Typography>
    </Grid>
  )
}

const Circuit = ({ circuitDetails }) => {
  const [openModal, setOpenModal] = useState(false)

  const handleClose = () => {
    setOpenModal(false)
  }

  return (
    <Grid
      px={4}
      pt={2}
      container
      flexDirection="column
    "
    >
      <Grid
        id="topGrid"
        item
        container
        xs={11.85}
        justifyContent="space-between"
      >
        <SingleGrid title="No. of Qbits" value={circuitDetails?.total_qbits} />
        <SingleGrid title="No.1 Qbit Gates" value={circuitDetails?.qbit1_gates} />
        <SingleGrid title="No.2 Qbit Gates" value={circuitDetails?.qbit2_gates} />
        <SingleGrid title="Depth" value={circuitDetails?.depth} />
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

        <Grid sx={{ width: '80%', height: '100%' }}>
          <Paper
            elevation={0}
            sx={(theme) => ({
              bgcolor: theme.palette.background.outRunBg,
            })}
          >
            {' '}
            <SyntaxHighlighter src={circuitDetails?.circuit_diagram} preview fullwidth />
          </Paper>
        </Grid>
      </Grid>
      <Modal
        open={openModal}
        onClose={handleClose}
        aria-labelledby="modal-modal-title"
        aria-describedby="modal-modal-description"
      >
        <Box sx={styles}>
          <Grid container sx={{ height: '100%' }}>
            <Grid item xs={11} sx={{ height: '100%' }}>
              <Grid
                mt={2}
                container
                justifyContent="center"
                sx={{ width: '900px', height: '320px' }}
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
                    component={CircuitLarge}
                    viewBox="0 0 900 320" // Specify the viewBox to match the desired container size
                  />
                </span>
              </Grid>
            </Grid>
            <Grid
              item
              pr={1}
              pt={0.5}
              xs={1}
              sx={{
                display: 'flex',
                justifyContent: 'flex-end',
                cursor: 'pointer',
              }}
            >
              <span style={{ flex: 'none' }} onClick={handleClose}>
                <SvgIcon
                  aria-label="view"
                  sx={{
                    display: 'flex',
                    justifyContent: 'flex-end',
                    mr: 0,
                    mt: 1,
                    pr: 0,
                  }}
                >
                  <CloseSvg />
                </SvgIcon>
              </span>
            </Grid>
          </Grid>
        </Box>
      </Modal>
    </Grid>
  )
}

export default Circuit
