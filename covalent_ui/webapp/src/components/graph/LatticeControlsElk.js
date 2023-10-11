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

import { useZoomPanHelper } from 'react-flow-renderer'
import {
  ToggleButton,
  ToggleButtonGroup,
  Tooltip,
  SvgIcon,
} from '@mui/material'
import {
  ArrowBack,
  ArrowDownward,
  ArrowForward,
  ArrowUpward,
  LockOpenOutlined,
  LockOutlined,
  MapOutlined,
} from '@mui/icons-material'
import useFitViewHelper from './ReactFlowHooks'
import DashboardIcon from '@mui/icons-material/Dashboard'
import LabelOffIcon from '@mui/icons-material/LabelOff'
import LabelIcon from '@mui/icons-material/Label'
import * as React from 'react'
import { LayoutOptions } from './LayoutOptions'
import { ReactComponent as ScreenshotIcon } from '../../assets/screenshot.svg'
import { ReactComponent as FitViewSvg } from '../../assets/latticeControls/fit-view.svg'
import { ReactComponent as ZoomInSvg } from '../../assets/latticeControls/zoom-in.svg'
import { ReactComponent as ZoomOutSvg } from '../../assets/latticeControls/zoom-out.svg'
import { ReactComponent as PostProcessSvg } from '../../assets/latticeControls/post-process.svg'
import { ReactComponent as PrettifySvg } from '../../assets/latticeControls/prettify.svg'
import { ReactComponent as ParameterSvg } from '../../assets/latticeControls/parameter.svg'

const LatticeControls = ({
  marginLeft = 0,
  marginRight = 0,
  showParams,
  toggleParams,
  showPostProcess,
  togglePostProcess,
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
  togglePrettify,
  prettify,
}) => {
  const { zoomIn, zoomOut } = useZoomPanHelper()
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
        <ToggleButton
          value=""
          onClick={() => zoomIn(300)}
          sx={{ height: '40px', color: 'white' }}
        >
          <SvgIcon
            data-testid="AddIcon"
            sx={{
              fontSize: '35px',
              mt: 3,
              ml: 2.5,
            }}
          >
            <ZoomInSvg />
          </SvgIcon>{' '}
        </ToggleButton>
      </Hint>

      <Hint title="Zoom out">
        <ToggleButton
          value=""
          onClick={() => zoomOut(300)}
          sx={{ height: '40px', color: 'white' }}
        >
          <SvgIcon
            data-testid="RemoveIcon"
            sx={{
              fontSize: '35px',
              mt: 4,
              ml: 2.5,
            }}
          >
            <ZoomOutSvg />
          </SvgIcon>{' '}
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
        <ToggleButton
          data-testid="tooglebuttonclick"
          onClick={(e) => handleClick(e)}
          value=""
        >
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
                return setDirection('RIGHT')
              case 'DOWN':
                return setDirection('LEFT')
              case 'LEFT':
                return setDirection('UP')
              case 'RIGHT':
                return setDirection('DOWN')
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
        <ToggleButton value="" onClick={() => handleHideLabels()}>
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
          <SvgIcon
            data-testid="Postprocess toggle button"
            sx={{
              pt: 0.5,
              mt: 0,
              mb: 0,
              ml: 1,
            }}
          >
            <ParameterSvg />
          </SvgIcon>{' '}
        </ToggleButton>
      </Hint>
      <Hint title="Toggle Postprocess">
        <ToggleButton
          data-testid="togglepostprocess"
          onClick={togglePostProcess}
          value=""
          selected={showPostProcess}
        >
          <SvgIcon
            data-testid="Postprocess toggle button"
            sx={{
              pt: 0.5,
              mt: 0,
              mb: 0,
              ml: 1,
            }}
          >
            <PostProcessSvg />
          </SvgIcon>{' '}
        </ToggleButton>
      </Hint>
      <Hint title="Prettify">
        <ToggleButton
          data-testid="prettify"
          value=""
          onClick={togglePrettify}
          selected={prettify}
        >
          <SvgIcon
            data-testid="Postprocess toggle button"
            sx={{
              pt: 0.5,
              mt: 0,
              mb: 0,
              ml: 1,
            }}
          >
            <PrettifySvg />
          </SvgIcon>{' '}
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
