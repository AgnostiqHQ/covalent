import React, { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
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
import {
  qelectronJobs,
  qelectronJobOverview
} from '../../redux/electronSlice'

const nodeDrawerWidth = 1110

const QElectronDrawer = ({ toggleQelectron, openQelectronDrawer, dispatchId, electronId }) => {
  const dispatch = useDispatch()
  const [expanded, setExpanded] = React.useState(true)
  const handleDrawerClose = () => {
    toggleQelectron()
  }

  const rowClickHandler = (job_id) => {
    dispatch(qelectronJobOverview({ dispatchId, electronId, jobId: job_id }))
  }

  const details = {
    title: 'Quantum Qaoa',
    status: 'RUNNING',
  }

  const listData = useSelector(
    (state) => state.electronResults.qelectronJobs
  );

  const overviewData = useSelector(
    (state) => state.electronResults.qelectronJobOverview
  );

  useEffect(() => {
    if (electronId && openQelectronDrawer) {
      const bodyParams = {
        sort_by: 'start_time',
        direction: 'DESC',
        offset: 0
      }
      dispatch(
        qelectronJobs({
          dispatchId,
          electronId,
          bodyParams
        })
      ).then((res) => {
        const job_id = res.payload[0].job_id
        dispatch(qelectronJobOverview({ dispatchId, electronId, jobId: job_id }))
      })
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [openQelectronDrawer])

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
          <QElelctronAccordion expanded={expanded} setExpanded={setExpanded} overviewData={overviewData} />
          <QElectronList expanded={expanded} data={listData} rowClick={rowClickHandler} dispatchId={dispatchId} electronId={electronId} />
        </Grid>
      </Grid>
    </Drawer>
  )
}

export default QElectronDrawer
