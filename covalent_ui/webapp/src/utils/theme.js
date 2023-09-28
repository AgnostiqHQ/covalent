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
import { createTheme, emphasize } from '@mui/material/styles'
import { Link as RouterLink } from 'react-router-dom'

const LinkBehavior = React.forwardRef(({ href, ...props }, ref) => {
  // Map href (MUI) -> to (react-router)
  return <RouterLink ref={ref} to={href} {...props} />
})

const defaultTheme = createTheme({
  typography: {
    fontFamily: '"DM Sans", "Helvetica", "Arial", sans-serif',
    logsFont: '"Inter", "Arial", sans-serif',
    sidebarh1: '1rem',
    sidebarh2: '0.875rem',
    sidebarh3: '0.75rem',
  },
  palette: {
    mode: 'dark',
    primary: {
      light: '#AEB6FF',
      main: '#6D7CFF',
      dark: '#5552FF',
      blue04: '#6473FF',
      white: '#ffff',
      highlightBlue: '#1B2632',
      grey: '#AEB6FF4D',
      blue02: '#323267',
    },
    secondary: {
      light: '#DAC3FF',
      main: '#AD7BFF',
      dark: '#8B31FF',
    },
    background: {
      default: '#08081A',
      defaultLight: '#08081A66',
      paper: '#1C1C46',
      coveBlack01: '#464660',
      coveBlack02: '#303067',
      graphCanvas: '#464646',
      darkblackbg: '#101820',
      buttonBg: '#10102C',
      executorBg: '#1E1E2E',
      outRunBg: '#0B0B11',
      qelectronbg: '#30306780',
      qelectronDrawerbg: '#1C1C46CC',
      qListBg: '#08081A66',
    },
    error: {
      main: '#FF6464',
    },
    success: {
      main: '#55D899',
    },
    warning: {
      main: '#E39F50',
    },
    running: {
      main: '#dac3ff',
    },
    info: {
      main: '#CBCBD7',
    },
    queued: {
      main: '#FFC164',
    },
    text: {
      primary: '#CBCBD7',
      secondary: '#F1F1F6',
      tertiary: '#86869A',
    },
  },
})

const darkScrollbar = ({
  size = 6,
  border = 0,
  borderRadius = 8,
  thumbColor = emphasize(defaultTheme.palette.background.paper, 0.1),
  trackColor = emphasize(defaultTheme.palette.background.default, 0.1),
  active = emphasize(defaultTheme.palette.background.paper, 0.15),
} = {}) => {
  return {
    scrollbarColor: `${thumbColor} ${trackColor}`,
    '&::-webkit-scrollbar, & *::-webkit-scrollbar': {
      backgroundColor: trackColor,
      height: size,
      width: size,
    },
    '&::-webkit-scrollbar-thumb, & *::-webkit-scrollbar-thumb': {
      borderRadius,
      backgroundColor: thumbColor,
      minHeight: 24,
      border: `${border}px solid ${trackColor}`,
    },
    '&::-webkit-scrollbar-thumb:focus, & *::-webkit-scrollbar-thumb:focus': {
      backgroundColor: active,
    },
    '&::-webkit-scrollbar-thumb:active, & *::-webkit-scrollbar-thumb:active': {
      backgroundColor: active,
    },
    '&::-webkit-scrollbar-thumb:hover, & *::-webkit-scrollbar-thumb:hover': {
      backgroundColor: active,
    },
    '&::-webkit-scrollbar-corner, & *::-webkit-scrollbar-corner': {
      backgroundColor: trackColor,
    },
  }
}

const theme = createTheme(defaultTheme, {
  components: {
    MuiLink: {
      defaultProps: {
        component: LinkBehavior,
      },
    },
    MuiButtonBase: {
      defaultProps: {
        LinkComponent: LinkBehavior,
      },
    },
    MuiSnackbarContent: {
      styleOverrides: {
        root: {
          color: '#FAFAFA',
          backgroundColor: '#1c1c46',
          border: '1px solid #99daff',
        },
      },
    },
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          ...darkScrollbar(),
        },
      },
    },
    MuiTooltip: {
      defaultProps: {
        // The props to apply
        arrow: true,
      },
      styleOverrides: {
        tooltip: {
          backgroundColor: '#1C1C46',
          color: '#FAFAFA',
        },
        arrow: {
          color: '#1C1C46',
        },
      },
    },
    MuiPaginationItem: {
      styleOverrides: {
        root: {
          '&.Mui-selected': {
            backgroundColor: '#1C1C46',
            color: '#fafafa',
            border: '1px solid #AEB6FF',
          },
        },
      },
    },
  },
})

export const graphBgColor = theme.palette.background.default

export default theme
