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

import { Grid, Typography, SvgIcon, Box, Modal, Paper, Skeleton } from '@mui/material'
import React, { useState } from 'react'
import theme from '../../utils/theme'
import { ReactComponent as CircuitLarge } from '../../assets/qelectron/circuit-large.svg'
import { ReactComponent as CloseSvg } from '../../assets/close.svg'
import SyntaxHighlighter from '../common/SyntaxHighlighter'
import { useSelector } from 'react-redux';

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

const SingleGrid = ({ title, value, id }) => {

  const qelectronJobOverviewIsFetching = useSelector(
    (state) => state.electronResults.qelectronJobOverviewList.isFetching
  );

  return (
    <Grid item sx={{ width: '10.4rem' }} data-testid={id}>
      <Typography
        sx={{
          fontSize: theme.typography.sidebarh3,
          color: (theme) => theme.palette.text.tertiary,
        }}
      >
        {title}
      </Typography>
      {qelectronJobOverviewIsFetching && !value ?
        <Skeleton data-testid="node__box_skl" width={30} /> : <>
          <Typography
            sx={{
              fontSize: theme.typography.sidebarh2,
              color: (theme) => theme.palette.text.primary,
            }}
          >
            {value || value === 0 ? value : '-'}
          </Typography>
        </>}
    </Grid>
  )
}

const Circuit = ({ circuitDetails }) => {
  const [openModal, setOpenModal] = useState(false)
  const [circuitData, setCircuitData] = useState(circuitDetails);

  const handleClose = () => {
    setOpenModal(false)
  }
  const qelectronJobOverviewIsFetching = useSelector(
    (state) => state.electronResults.qelectronJobOverviewList.isFetching
  );

  React.useEffect(() => {
    const details = { ...circuitData };
    const gatesArray = [];
    Object?.keys(details)?.forEach((item, index) => {
      const obj = {};
      if (/qbit[0-9]+_gates/.test(item)) {
        obj['value'] = details[item];
        const i = item?.substring(4, item?.indexOf('_'));
        obj['title'] = `No. ${i}-Qubit Gates`;
        obj['id'] = item;
        gatesArray?.push(obj);
      }
    })
    details['gates'] = [...gatesArray];
    setCircuitData({ ...details });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [circuitDetails])

  const renderQubitgates = () => {
    return circuitData?.gates?.map((detail, index) => (
      <SingleGrid title={detail?.title} value={detail?.value} id={detail?.id} />
    ));
  }

  return (
    <Grid
      px={4}
      pt={2}
      container
      height="14rem"
      sx={{ overflow: 'auto' }}
      data-testid="Circuit-grid"
    >
      <Grid
        id="topGrid"
        item
        container
        xs={11.85}
        columnSpacing={7.4}
        rowSpacing={4}
      >
        <SingleGrid title="No. of Qubits" value={circuitData?.total_qbits} id='total_qbits' />
        {renderQubitgates()}
        <SingleGrid title="Depth" value={circuitData?.depth} id='depth' />
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

        <Grid sx={{ width: '17rem', height: '5rem' }} data-testid="circuit">
          <Paper
            elevation={0}
            sx={(theme) => ({
              bgcolor: theme.palette.background.outRunBg,
            })}
          >
            {' '}
            <SyntaxHighlighter src={circuitDetails?.circuit_diagram} preview fullwidth isFetching={qelectronJobOverviewIsFetching} />
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
