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

import { useReactFlow } from 'react-flow-renderer'
import { ToggleButton, ToggleButtonGroup, Tooltip,  SvgIcon,
} from '@mui/material'
import {
  Add as PlusIcon,
  ArrowBack,
  ArrowDownward,
  ArrowForward,
  ArrowUpward,
  LockOpenOutlined,
  LockOutlined,
  MapOutlined,
  Remove as MinusIcon,
} from '@mui/icons-material'
import useFitViewHelper from './ReactFlowHooks'
import DashboardIcon from '@mui/icons-material/Dashboard'
import LabelOffIcon from '@mui/icons-material/LabelOff'
import LabelIcon from '@mui/icons-material/Label'
import * as React from 'react'
import { LayoutOptions } from './LayoutOptions'
import { ReactComponent as ScreenshotIcon } from '../../assets/screenshot.svg'
import { ReactComponent as FitViewSvg } from '../../assets/latticeControls/fit-view.svg'

const LatticeControls = ({
  marginLeft = 0,
  marginRight = 0,
  showParams,
  toggleParams,
  showMinimap,
  toggleMinimap,
  direction,
  setDirection,
  algorithm,
  handleChangeAlgorithm,
  nodesDraggable,
  toggleNodesDraggable,
  open,
  handleClick,
  anchorEl,
  handleClose,
  handleHideLabels,
  hideLabels,
  toggleScreenShot,
}) => {
  const { zoomIn, zoomOut } = useReactFlow()
  const { fitView } = useFitViewHelper()
  return (
    <ToggleButtonGroup
      orientation="vertical"
      size="small"
      sx={{
        position: 'absolute',
        bottom: 12,
        left: 12 + marginLeft,
        zIndex: 5,
        opacity: 0.8,
        border: 'none',
        width: '50px',
        background: (theme) => theme.palette.background.default,

        '.MuiToggleButton-root': {
          border: '1px solid transparent ',
        },
      }}
    >
      <Hint title="Zoom in">
        <ToggleButton value="" onClick={() => zoomIn(300)}>
          <PlusIcon />
        </ToggleButton>
      </Hint>

      <Hint title="Zoom out">
        <ToggleButton value="" onClick={() => zoomOut(300)}>
          <MinusIcon />
        </ToggleButton>
      </Hint>
      <Hint title="Download Screenshot">
        <ToggleButton
          onClick={toggleScreenShot}
          value=""
          sx={{ height: '40px', color: 'white' }}
        >
          <ScreenshotIcon />
        </ToggleButton>
      </Hint>

      <Hint title="Fit to screen">
        <ToggleButton
          sx={{ height: '40px', color: 'white' }}
          value=""
          onClick={() => {
            fitView({ duration: 300, marginLeft, marginRight })
          }}
          data-testid="FullscreenIcon"
        >
          <SvgIcon
            sx={{
              fontSize: '33px',
              mt: 1.5,
              ml: 1.5,
            }}
          >
            <FitViewSvg />
          </SvgIcon>
        </ToggleButton>
      </Hint>
      <Hint title="Toggle minimap">
        <ToggleButton onClick={toggleMinimap} value="" selected={showMinimap}>
          <MapOutlined
            fontSize="small"
            sx={{ color: (theme) => theme.palette.text.primary }}
          />
        </ToggleButton>
      </Hint>
      <Hint title="Change layout">
        <ToggleButton data-testid="tooglebuttonclick" onClick={(e) => handleClick(e,marginLeft,marginRight)} value="">
          <DashboardIcon
          fontSize="small"
          sx={{ color: (theme) => theme.palette.text.primary }}
          />
        </ToggleButton>
      </Hint>

      <LayoutOptions
        algorithm={algorithm}
        open={open}
        anchorEl={anchorEl}
        handleClick={handleClick}
        handleClose={handleClose}
        handleChangeAlgorithm={handleChangeAlgorithm}
      />

      <Hint title="Change orientation">
        <ToggleButton
          data-testid="changeorientation"
          onClick={() => {
            switch (direction) {
              case 'UP':
                return setDirection('RIGHT',marginLeft,marginRight)
              case 'DOWN':
                return setDirection('LEFT',marginLeft,marginRight)
              case 'LEFT':
                return setDirection('UP',marginLeft,marginRight)
              case 'RIGHT':
                return setDirection('DOWN',marginLeft,marginRight)
              default:
            }
          }}
          value=""
        >
          {
            {
              DOWN: (
                <ArrowDownward
                  fontSize="small"
                  sx={{ color: (theme) => theme.palette.text.primary }}
                />
              ),
              UP: (
                <ArrowUpward
                  fontSize="small"
                  sx={{ color: (theme) => theme.palette.text.primary }}
                />
              ),
              RIGHT: (
                <ArrowForward
                  fontSize="small"
                  sx={{ color: (theme) => theme.palette.text.primary }}
                />
              ),
              LEFT: (
                <ArrowBack
                  fontSize="small"
                  sx={{ color: (theme) => theme.palette.text.primary }}
                />
              ),
            }[direction]
          }
        </ToggleButton>
      </Hint>

      <Hint
        data-testid="handlelabelhide"
        title={hideLabels ? 'Show labels' : 'Hide labels'}
      >
        <ToggleButton value="" onClick={() => handleHideLabels(marginLeft,marginRight)}>
          {hideLabels ? (
            <LabelOffIcon
              fontSize="small"
              sx={{ color: (theme) => theme.palette.text.primary }}
            />
          ) : (
            <LabelIcon
              fontSize="small"
              sx={{ color: (theme) => theme.palette.text.primary }}
            />
          )}
        </ToggleButton>
      </Hint>
      <Hint title="Toggle parameters">
        <ToggleButton
          data-testid="toggleparams"
          onClick={toggleParams}
          value=""
          selected={showParams}
        >
          P
        </ToggleButton>
      </Hint>
      <Hint title="Toggle draggable nodes">
        <ToggleButton
          data-testid="toggledragablenode"
          onClick={toggleNodesDraggable}
          value=""
        >
          {nodesDraggable ? (
            <LockOpenOutlined
              fontSize="small"
              sx={{ color: (theme) => theme.palette.text.primary }}
            />
          ) : (
            <LockOutlined
              fontSize="small"
              sx={{ color: (theme) => theme.palette.text.primary }}
            />
          )}
        </ToggleButton>
      </Hint>
    </ToggleButtonGroup>
  )
}

const Hint = (props) => <Tooltip arrow placement="right" {...props} />

export default LatticeControls
