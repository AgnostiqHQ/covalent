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
import * as React from 'react'
import Box from '@mui/material/Box'
import Modal from '@mui/material/Modal'
import Skeleton from '@mui/material/Skeleton'
import _ from 'lodash'
import { Light } from 'react-syntax-highlighter'
import python from 'react-syntax-highlighter/dist/cjs/languages/hljs/python'
import yaml from 'react-syntax-highlighter/dist/cjs/languages/hljs/yaml'
import json from 'react-syntax-highlighter/dist/cjs/languages/hljs/json'
import style from 'react-syntax-highlighter/dist/cjs/styles/hljs/androidstudio'
import { Grid, SvgIcon, Tooltip } from '@mui/material'
import { ReactComponent as ViewSvg } from '../../assets/codeview.svg'
import { ReactComponent as CloseSvg } from '../../assets/close.svg'

import { useState } from 'react'

Light.registerLanguage('python', python)
Light.registerLanguage('yaml', yaml)
Light.registerLanguage('json', json)

const SyntaxHighlighter = ({ src, preview, fullwidth, ...props }) => {
  const { isFetching } = props;
  const [open, setOpen] = useState(false)
  const handleOpen = () => setOpen(true)
  const handleClose = () => setOpen(false)

  const styles = {
    outline: 'none',
    position: 'absolute',
    top: '50%',
    left: '49%',
    transform: 'translate(-50%, -50%)',
    p: 4,
    width: ' 95%',
    height: '95%',
    bgcolor: '#0B0B11E5',
    border: '2px solid transparent',
    boxShadow: 24,
  }

  return (
    <>
      <Grid
        container
        sx={{
          width: preview ? (preview && fullwidth ? '100%' : '20.7rem') : null,
          height: preview ? (preview && fullwidth ? '100%' : '10rem') : null,
        }}
      >
        <Grid item xs={11}>
          {isFetching && !src ?
            <Box sx={{ height: '5rem' }}>
              <Skeleton data-testid="syntax__box_skl" width={150} sx={{ ml: "5px", mt: '7px' }} /></Box> : <>
              <Light
                data-testid="syntax"
                language="python"
                style={style}
                customStyle={{
                  margin: 0,
                  padding: 10,
                  maxHeight: 240,
                  fontSize: 12,
                  backgroundColor: 'transparent',
                }}
                {...props}
              >
                {_.trim(_.truncate(src, { length: 200 }), '"" \n')}
              </Light></>}
        </Grid>
        <Grid
          item
          pr={1}
          pt={0.5}
          xs={1}
          sx={{
            display: 'flex',
            justifyContent: 'flex-end',
          }}
        >
          {preview && (!isFetching || src) && (
            <Tooltip
              title="Expand view"
              placement="bottom"
              data-testid="expandbutton"
            >
              <SvgIcon
                aria-label="view"
                sx={{
                  display: 'flex',
                  justifyContent: 'flex-end',
                  mr: 0,
                  mt: 1,
                  pr: 0,
                  cursor: 'pointer',
                }}
                onClick={handleOpen}
              >
                <ViewSvg />
              </SvgIcon>
            </Tooltip>
          )}
        </Grid>
      </Grid>
      <Modal
        open={open}
        onClose={handleClose}
        aria-labelledby="modal-modal-title"
        aria-describedby="modal-modal-description"
      >
        <Box sx={styles}>
          <Grid container sx={{ height: '100%' }}>
            <Grid item xs={11} sx={{ height: '100%' }}>
              <Light
                data-testid="syntax"
                language="python"
                style={style}
                customStyle={{
                  margin: 0,
                  padding: 10,
                  maxHeight: ' 100%',
                  fontSize: 12,
                  backgroundColor: 'transparent',
                }}
                {...props}
              >
                {_.trim(src, '"" \n')}
              </Light>
            </Grid>
            <Grid
              item
              pr={1}
              pt={0.5}
              xs={1}
              sx={{
                display: 'flex',
                justifyContent: 'flex-end',
                cursor: 'default',
              }}
            >
              <SvgIcon
                aria-label="view"
                sx={{
                  display: 'flex',
                  justifyContent: 'flex-end',
                  mr: 0,
                  mt: 1,
                  pr: 0,
                  cursor: 'pointer',
                }}
                onClick={handleClose}
              >
                <CloseSvg />
              </SvgIcon>
            </Grid>
          </Grid>
        </Box>
      </Modal>
    </>
  )
}

export default SyntaxHighlighter
