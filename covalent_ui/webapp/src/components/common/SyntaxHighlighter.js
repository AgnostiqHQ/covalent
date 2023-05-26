/**
 * Copyright 2021 Agnostiq Inc.
 *
 * This file is part of Covalent.
 *
 * Licensed under the GNU Affero General Public License 3.0 (the "License").
 * A copy of the License may be obtained with this software package or at
 *
 *      https://www.gnu.org/licenses/agpl-3.0.en.html
 *
 * Use of this file is prohibited except in compliance with the License. Any
 * modifications or derivative works of this file must retain this copyright
 * notice, and modified files must contain a notice indicating that they have
 * been altered from the originals.
 *
 * Covalent is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE. See the License for more details.
 *
 * Relief from the License may be granted by purchasing a commercial license.
 */
import * as React from 'react'
import Box from '@mui/material/Box'
import Slide from '@mui/material/Slide'
import Typography from '@mui/material/Typography'
import Modal from '@mui/material/Modal'
import _ from 'lodash'
import { Light } from 'react-syntax-highlighter'
import python from 'react-syntax-highlighter/dist/cjs/languages/hljs/python'
import yaml from 'react-syntax-highlighter/dist/cjs/languages/hljs/yaml'
import json from 'react-syntax-highlighter/dist/cjs/languages/hljs/json'
import style from 'react-syntax-highlighter/dist/cjs/styles/hljs/androidstudio'
import { Grid, SvgIcon } from '@mui/material'
import { ReactComponent as ViewSvg } from '../../assets/codeview.svg'
import { ReactComponent as CloseSvg } from '../../assets/close.svg'

import { useState } from 'react'

Light.registerLanguage('python', python)
Light.registerLanguage('yaml', yaml)
Light.registerLanguage('json', json)

const SyntaxHighlighter = ({ src, preview, fullwidth, ...props }) => {
  const [open, setOpen] = useState(false)
  const handleOpen = () => setOpen(true)
  const handleClose = () => setOpen(false)

  const styles = {
    position: 'absolute',
    top: '2%',
    left: '2%',
    transform: 'translate(-2%, -2%)',
    width: ' 95%',
    height: '95%',
    bgcolor: '#0B0B11E5',
    border: '2px solid transparent',
    boxShadow: 24,
    p: 4,
  }

  return (
    <>
      <Grid
        container
        sx={{
          width: preview ? (preview && fullwidth ? '100%' : '20rem') : null,
          height: preview ? (preview && fullwidth ? '100%' : '10rem') : null,
        }}
      >
        <Grid item xs={11}>
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
            cursor: 'pointer',
          }}
        >
          {preview && (
            <span style={{ flex: 'none' }} onClick={handleOpen}>
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
                <ViewSvg />
              </SvgIcon>
            </span>
          )}
        </Grid>
      </Grid>
      <Modal
        open={open}
        onClose={handleClose}
        aria-labelledby="modal-modal-title"
        aria-describedby="modal-modal-description"
      >
        <Slide direction="down" in={open}>
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
        </Slide>
      </Modal>
    </>
  )
}

export default SyntaxHighlighter
