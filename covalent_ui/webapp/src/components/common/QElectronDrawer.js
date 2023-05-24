import React, { useEffect } from 'react'
import {
  Grid,
  Divider,
  Drawer,
  IconButton,
  Paper,
  Typography,
  Skeleton,
} from '@mui/material'
import { alpha } from '@mui/material/styles'
import QElectronTopBar from './QElectronTopBar'
import QElelctronAccordion from './QElelctronAccordion'

const nodeDrawerWidth = 1110

const QElectronDrawer = ({ toggleQelectron, openQelectronDrawer }) => {
  const handleDrawerClose = () => {
    toggleQelectron()
  }

  const details = {
    title: 'Quantum Qaoa',
    status: 'RUNNING',
  }

  //   useEffect(() => {
  //     const handleOutsideClick = (event) => {
  //       if (
  //         openQelectronDrawer &&
  //         !event.target.closest('.q-electron-card') &&
  //         !event.target.closest('#nodeDrawer')
  //       ) {
  //         handleDrawerClose()
  //       }
  //     }

  //     document.addEventListener('mousedown', handleOutsideClick)

  //     return () => {
  //       document.removeEventListener('mousedown', handleOutsideClick)
  //     }
  //   }, [openQelectronDrawer])

  return (
    <Drawer
      id="nodeDrawer"
      sx={(theme) => ({
        width: nodeDrawerWidth,
        '& .MuiDrawer-paper': {
          width: nodeDrawerWidth,
          boxSizing: 'border-box',
          border: 'none',
          p: 3,
          marginRight: '10px',
          marginTop: '22px',
          height: '95vh',
          bgcolor: alpha(theme.palette.background.default),
          boxShadow: '0px 16px 50px rgba(0, 0, 0, 0.9)',
          backdropFilter: 'blur(8px)',
          borderRadius: '16px',
          '@media (max-width: 1290px)': {
            height: '92vh',
            marginTop: '70px',
          },
        },
      })}
      anchor="right"
      variant="persistent"
      open={openQelectronDrawer}
      onClose={handleDrawerClose}
      data-testid="nodeDrawer"
    >
      <Grid container>
        <Grid item xs={7.9}>
          <QElectronTopBar details={details} />
          <QElelctronAccordion />
        </Grid>
      </Grid>
    </Drawer>
  )
}

export default QElectronDrawer
