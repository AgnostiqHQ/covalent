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

import React from 'react'
import { createTheme, emphasize, darken } from '@mui/material/styles'
import { Link as RouterLink } from 'react-router-dom'

const LinkBehavior = React.forwardRef(({ href, ...props }, ref) => {
  // Map href (MUI) -> to (react-router)
  return <RouterLink ref={ref} to={href} {...props} />
})


const defaultTheme = createTheme({
  typography: {
    fontFamily: '"DM Sans", "Helvetica", "Arial", sans-serif',
  },
  palette: {
    mode: 'dark',
    primary: {
      light: '#AEB6FF',
      main: '#6D7CFF',
      dark: '#5552FF',
      blue04: '#6473FF',
      white:'#ffff',
    },
    secondary: {
      light: '#DAC3FF',
      main: '#AD7BFF',
      dark: '#8B31FF',
    },
    background: {
      default: '#08081A',
      paper: '#1C1C46',
      coveBlack01: '#464660',
      coveBlack02: '#303067',
      coveBlack03: '#1C1C46',
      graphCanvas: '#464646',
      darkblackbg:'#101820'
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
    text: {
      primary: '#F1F1F6',
      secondary: '#CBCBD7',
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
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          ...darkScrollbar(),
        },
      },
    },
    // MuiTabs: {
    //   styleOverrides: {
    //     root: {
    //       '& .MuiTabs-indicator': {
    //         backgroundColor: defaultTheme.palette.text.primary,
    //         height: 1,
    //       },
    //     },
    //   },
    // },
    // MuiTab: {
    //   styleOverrides: {
    //     root: {
    //       textTransform: 'none',
    //       '&.Mui-selected': {
    //         color: defaultTheme.palette.text.primary,
    //       },
    //     },
    //   },
    // },
  },
})

export const graphBgColor = darken(theme.palette.background.paper, 0.3)

export default theme
