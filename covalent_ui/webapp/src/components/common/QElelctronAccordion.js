/**
 * This file is part of Covalent.
 *
 * Licensed under the Apache License 2.0 (the "License"). A copy of the
 * License may be obtained with this software package or at
 *
 *     https://www.apache.org/licenses/LICENSE-2.0
 *
 * Use of this file is prohibited except in compliance with the License.
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import React from 'react'
import Accordion from '@mui/material/Accordion'
import AccordionSummary from '@mui/material/AccordionSummary'
import AccordionDetails from '@mui/material/AccordionDetails'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import { Grid, IconButton } from '@mui/material'
import QElectronTab from './QElectronTab'
import Overview from '../qelectron/Overview'
import Circuit from '../qelectron/Circuit'
import Executor from '../qelectron/Executor'

const QElelctronAccordion = (props) => {
  const { expanded, setExpanded, overviewData, openQelectronDrawer } = props
  const [value, setValue] = React.useState('1')

  React.useEffect(() => {
    if (openQelectronDrawer) setValue('1')
  }, [openQelectronDrawer]);

  const handleAccordChange = () => {
    setExpanded(!expanded)
  }

  const handleChange = (event, newValue) => {
    setValue(newValue)
    setExpanded(true)
  }
  return (
    <Grid mt={2} data-testid="Accordion-grid">
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
          {value === '3' && <Executor code={JSON.stringify(overviewData?.executor?.executor, null, 4)} />}
        </AccordionDetails>
      </Accordion>
    </Grid>
  )
}

export default QElelctronAccordion
