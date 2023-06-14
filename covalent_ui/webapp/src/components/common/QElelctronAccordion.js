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
import { Grid, IconButton } from '@mui/material'
import QElectronTab from './QElectronTab'
import Overview from '../qelectron/Overview'
import Circuit from '../qelectron/Circuit'
import Executor from '../qelectron/Executor'

const QElelctronAccordion = (props) => {
  const { expanded, setExpanded, overviewData } = props
  const [value, setValue] = React.useState('1')

  const handleAccordChange = () => {
    setExpanded(!expanded)
  }

  const details = {
    backend: 'IBM Quantum',
    time: '1h 22m',
    start_time: 'Dec 12, 14:44:32',
    end_time: 'Dec 13, 16:00:22',
  }

  const circuitDetails = {
    no_of_qbits: 20,
    no1_gates: 1001,
    no2_gates: 2234,
    depth: 543,
  }

  const code = `// Imports
  import mongoose, { Schema } from 'mongoose'
  
  // Collection name
  export const collection = 'Product'|
  
  // Schema
  const schema = new Schema({
    name: {
      type: String,
      required: true
    },
  
    description: {
      type: String
    }
  }, {timestamps: true})
  
  // Model
  export default mongoose.model(collection, schema, collection)
  `

  const handleChange = (event, newValue) => {
    setValue(newValue)
    setExpanded(true)
  }
  return (
    <Grid mt={2}>
      <Accordion
        TransitionProps={{ timeout: 400 }}
        expanded={expanded}
        // onChange={handleAccordChange}
        sx={{
          background: (theme) => theme.palette.background.qelectronDrawerbg,
          border: '2px solid',
          borderRadius: '8px',
          minHeight: expanded ? '19rem' : '2rem',
          borderColor: (theme) => theme.palette.background.qelectronbg,
        }}
      >
        <AccordionSummary
          sx={{
            height: '2rem',
            padding: 0, // Remove the default padding
            '& .MuiAccordionSummary-content': {
              margin: 0, // Remove the default margin
            },
          }}
          p={0}
          expandIcon={
            <IconButton
              onClick={handleAccordChange}
              aria-expanded={expanded}
              aria-label="Toggle accordion"
            >
              <ExpandMoreIcon />
            </IconButton>
          }
          aria-controls="panel1a-content"
          id="panel1a-header"
        >
          <QElectronTab value={value} handleChange={handleChange} />
        </AccordionSummary>
        <AccordionDetails sx={{ p: 0, margin: 'auto' }}>
          {value === '1' && <Overview details={overviewData?.overview} />}
          {value === '2' && <Circuit circuitDetails={overviewData?.circuit} />}
          {value === '3' && <Executor code={code} />}
        </AccordionDetails>
      </Accordion>
    </Grid>
  )
}

export default QElelctronAccordion
