/*
 * Copyright 2022 Agnostiq Inc.
 * Note: This file is subject to a proprietary license agreement entered into between
 * you (or the person or organization that you represent) and Agnostiq Inc. Your rights to
 * access and use this file is subject to the terms and conditions of such agreement.
 * Please ensure you carefully review such agreements and, if you have any questions
 * please reach out to Agnostiq at: [support@agnostiq.com].
 */

import React from 'react'
import Accordion from '@mui/material/Accordion'
import AccordionSummary from '@mui/material/AccordionSummary'
import AccordionDetails from '@mui/material/AccordionDetails'
import Typography from '@mui/material/Typography'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import { Grid } from '@mui/material'
import QElectronTab from './QElectronTab'
import Overview from '../qelectron/Overview'

const QElelctronAccordion = () => {
  const [value, setValue] = React.useState('1')

  const details = {
    backend: 'IBM Quantum',
    time: '1h 22m',
    start_time: 'Dec 12, 14:44:32',
    end_time: 'Dec 13, 16:00:22',
  }

  const handleChange = (event, newValue) => {
    setValue(newValue)
  }
  return (
    <Grid mt={2}>
      <Accordion
        defaultExpanded
        sx={{
          background: (theme) => theme.palette.background.paper,
          border: '2px solid',
          borderRadius: '8px',
          borderColor: (theme) => theme.palette.background.qelectronbg,
        }}
      >
        <AccordionSummary
          expandIcon={<ExpandMoreIcon />}
          aria-controls="panel1a-content"
          id="panel1a-header"
        >
          <QElectronTab value={value} handleChange={handleChange} />
        </AccordionSummary>
        <AccordionDetails sx={{ p: 0 }}>
          {value === '1' && <Overview details={details} />}
          {value === '2' && <Grid p={2}>2</Grid>}
          {value === '3' && <Grid p={2}>3</Grid>}
        </AccordionDetails>
      </Accordion>
    </Grid>
  )
}

export default QElelctronAccordion
