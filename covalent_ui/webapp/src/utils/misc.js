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

import _ from 'lodash'
import { isValid, format, parseISO } from 'date-fns'
import theme from './theme'
import { SvgIcon } from '@mui/material'
import { ReactComponent as ActivitySvg } from '../assets/status/activity.svg'
import { ReactComponent as CheckSvg } from '../assets/status/checkmark.svg'
import { ReactComponent as ErrorSvg } from '../assets/status/error.svg'
import { ReactComponent as CancelSvg } from '../assets/status/stop.svg'
import { ReactComponent as LoaderSvg } from '../assets/loader.svg'
import { ReactComponent as FunctionSvg } from '../assets/nodeType/fuction.svg'
import { ReactComponent as ParameterSvg } from '../assets/nodeType/parameter.svg'
import { ReactComponent as SubLattice } from '../assets/nodeType/sublattice.svg'

export const secondsToHms = (ms) => {
  let time = ''
  const sec = Math.floor(ms / 1000)
  const days = Math.floor(sec / (3600 * 24))
  const hours = Math.floor(sec / 3600)
  const minutes = ('0' + (Math.floor(sec / 60) % 60)).slice(-2)
  if (ms < 1000) {
    time = '< 1sec'
  } else if (sec > 0 && sec < 60) {
    time = '< 1min'
  } else if (sec > 60 && sec < 3600) {
    time = `${Math.round(minutes)}m`
  } else if (sec > 3600 && sec < 86400) {
    time = `${Math.round(hours)}h ${Math.round(minutes)}m`
  } else if (sec > 86400 && sec < 172800) {
    time = '> 1 day'
  } else if (sec > 172800) {
    time = `${Math.round(days)} days`
  }
  return time
}

export const formatDate = (date) => {
  if (_.isString(date)) {
    date = parseISO(date)
  }
  return isValid(date) ? format(date, 'MMM dd, HH:mm:ss') : '-'
}

export const truncateMiddle = (s, start, end, omission = '…') => {
  if (!s) {
    return ''
  }
  const len = s.length
  if ((start === 0 && end === 0) || start + end >= len) {
    return s
  }
  if (!end) {
    return s.slice(0, start) + omission
  }
  return s.slice(0, start) + omission + s.slice(-end)
}

export const isParameter = (node) => _.startsWith(node.name, ':parameter:')

export const displayStatus = (status) => _.startCase(_.lowerCase(status))

export const statusColor = (status) => {
  return {
    RUNNING: theme.palette.running.main,
    NEW_OBJECT: theme.palette.running.main,
    COMPLETED: theme.palette.success.main,
    POSTPROCESSING: theme.palette.success.main,
    PENDING_POSTPROCESSING: theme.palette.success.main,
    POSTPROCESSING_FAILED: theme.palette.success.main,
    FAILED: theme.palette.error.main,
    CANCELLED: theme.palette.error.main,
  }[status]
}

export const statusLabel = (status) => {
  return (
    {
      RUNNING: 'Running',
      NEW_OBJECT: 'Pending',
      COMPLETED: 'Completed',
      FAILED: 'Failed',
      CANCELLED: 'Cancelled',
      POSTPROCESSING: 'Completed',
      PENDING_POSTPROCESSING: 'Completed',
      POSTPROCESSING_FAILED: 'Completed',
    }[status] || status
  )
}

export const statusIcon = (status) => {
  switch (status) {
    case 'RUNNING':
      return (
        <SvgIcon sx={{ mr: 0.5 }}>
          <LoaderSvg />
        </SvgIcon>
      )
    case 'NEW_OBJECT':
      return (
        <SvgIcon sx={{  mt: 1 }}>
          <ActivitySvg />
        </SvgIcon>
      )
    case 'COMPLETED':
      return (
        <SvgIcon sx={{  mt: 1 }}>
          <CheckSvg />
        </SvgIcon>
      )
    case 'POSTPROCESSING':
      return (
        <SvgIcon sx={{  mt: 1 }}>
          <CheckSvg />
        </SvgIcon>
      )
    case 'PENDING_POSTPROCESSING':
      return (
        <SvgIcon sx={{  mt: 1 }}>
          <CheckSvg />
        </SvgIcon>
      )
    case 'POSTPROCESSING_FAILED':
      return (
        <SvgIcon sx={{  mt: 1 }}>
          <CheckSvg />
        </SvgIcon>
      )
    case 'FAILED':
      return (
        <SvgIcon sx={{ mt: 1 }}>
          <ErrorSvg />
        </SvgIcon>
      )
    case 'CANCELLED':
      return (
        <SvgIcon sx={{ mt: 1 }}>
          <CancelSvg />
        </SvgIcon>
      )
    default:
      return null
  }
}

export const nodeLabelIcon = (type) => {
  switch (type) {
    case 'function':
      return (
        <SvgIcon sx={{mt:0.8}}>
          <FunctionSvg />
        </SvgIcon>
      )
    case 'electron_list':
      return (
        <SvgIcon sx={{mt:0.8}}>
          <FunctionSvg /> 
        </SvgIcon>
      )
    case 'parameter':
      return (
        <SvgIcon sx={{mt:1.5}}>
          <ParameterSvg />
        </SvgIcon>
      )
    case "sublattice":
      return (
        <SvgIcon  sx={{mt:0.8}}>
          <SubLattice />
        </SvgIcon>
      )
    default:
      return null
  }
}