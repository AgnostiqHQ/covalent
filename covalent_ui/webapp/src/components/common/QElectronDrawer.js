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
import QElectronList from '../qelectron/QElectronList'

const nodeDrawerWidth = 1110

const QElectronDrawer = ({ toggleQelectron, openQelectronDrawer }) => {
  const [expanded, setExpanded] = React.useState(true)
  const handleDrawerClose = () => {
    toggleQelectron()
  }

  const details = {
    title: 'Quantum Qaoa',
    status: 'RUNNING',
  }

  // useEffect(() => {
  //   const handleOutsideClick = (event) => {
  //     if (
  //       openQelectronDrawer &&
  //       !event.target.closest('.q-electron-card') &&
  //       !event.target.closest('#nodeDrawer')
  //     ) {
  //       handleDrawerClose()
  //     }
  //   }

  //   document.addEventListener('mousedown', handleOutsideClick)

  //   return () => {
  //     document.removeEventListener('mousedown', handleOutsideClick)
  //   }
  // }, [openQelectronDrawer])

  return (
    <Drawer
      transitionDuration={600}
      id="nodeDrawer"
      sx={(theme) => ({
        position: 'relative',
        width: nodeDrawerWidth,
        '& .MuiDrawer-paper': {
          width: nodeDrawerWidth,
          boxSizing: 'border-box',
          border: 'none',
          p: 3,
          marginRight: '10px',
          marginTop: '22px',
          maxHeight: '95vh',
          bgcolor: (theme) => theme.palette.background.qelectronDrawerbg,
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
      <Grid
        container
        sx={{ position: 'relative', maxHeight: '100%', overflow: 'auto' }}
      >
        <Grid item xs={7.9}>
          <QElectronTopBar
            details={details}
            toggleQelectron={toggleQelectron}
          />
          <QElelctronAccordion expanded={expanded} setExpanded={setExpanded} />
          <QElectronList expanded={expanded} />
        </Grid>
      </Grid>
    </Drawer>
  )
}

export default QElectronDrawer
