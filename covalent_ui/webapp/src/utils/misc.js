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
import { ReactComponent as ActivitySvg } from '../assets/status/pending.svg'
import { ReactComponent as CheckSvg } from '../assets/status/checkmark.svg'
import { ReactComponent as ErrorSvg } from '../assets/status/error.svg'
import { ReactComponent as CancelSvg } from '../assets/status/stop.svg'
import { ReactComponent as LoaderSvg } from '../assets/loader.svg'
import { ReactComponent as FunctionSvg } from '../assets/nodeType/fuction.svg'
import { ReactComponent as ParameterSvg } from '../assets/nodeType/parameter.svg'
import { ReactComponent as SubLattice } from '../assets/nodeType/sublattice.svg'
import { ReactComponent as ArgSvg } from '../assets/nodeType/arg.svg'
import { ReactComponent as AttributeSvg } from '../assets/nodeType/attribute.svg'
import { ReactComponent as ElectronDictSvg } from '../assets/nodeType/electron-dict.svg'
import { ReactComponent as ElectronListSvg } from '../assets/nodeType/electron-list.svg'
import { ReactComponent as GeneratedSvg } from '../assets/nodeType/generated.svg'
import { ReactComponent as InfoSvg } from '../assets/status/info.svg'
import { ReactComponent as WarningSvg } from '../assets/status/warning.svg'
import { ReactComponent as ConnectionLostSvg } from '../assets/status/connectionLost.svg'
import { ReactComponent as TimeoutSvg } from '../assets/status/timeout.svg'
import { ReactComponent as QueuedSvg } from '../assets/status/queued.svg'
import { ReactComponent as CompletingSvg } from '../assets/status/completing.svg'

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

export const formatLogTime = (date) => {
  if (_.isString(date)) {
    date = parseISO(date)
  }
  return isValid(date) ? format(date, 'HH:mm:ss,SSS') : '-'
}
export const formatLogDate = (date) => {
  if (_.isString(date)) {
    date = parseISO(date)
  }
  return isValid(date) ? format(date, 'yyyy-MM-dd') : '-'
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
    STARTING: theme.palette.running.main,
    NEW_OBJECT: theme.palette.queued.main,
    COMPLETED: theme.palette.success.main,
    FAILED: theme.palette.error.main,
    CANCELLED: theme.palette.success.main,
    POSTPROCESSING: theme.palette.success.main,
    PENDING_POSTPROCESSING: theme.palette.success.main,
    POSTPROCESSING_FAILED: theme.palette.success.main,
    REGISTERING: theme.palette.queued.main,
    PENDING: theme.palette.queued.main,
    PENDING_BACKEND: theme.palette.queued.main,
    QUEUED: theme.palette.queued.main,
    PROVISIONING: theme.palette.queued.main,
    DEPROVISIONING: theme.palette.queued.main,
    COMPLETING: theme.palette.success.main,
    REG_FAILED: theme.palette.error.main,
    BOOT_FAILED: theme.palette.error.main,
    PROVISION_FAILED: theme.palette.error.main,
    DEPROVISION_FAILED: theme.palette.error.main,
    CONNECTION_LOST: theme.palette.error.main,
    TIMEOUT: theme.palette.error.main,
  }[status]
}

export const statusLabel = (status) => {
  return (
    {
      RUNNING: 'Running',
      STARTING: 'Starting',
      NEW_OBJECT: 'Pending',
      COMPLETED: 'Completed',
      FAILED: 'Failed',
      CANCELLED: 'Cancelled',
      POSTPROCESSING: 'Completed',
      PENDING_POSTPROCESSING: 'Completed',
      POSTPROCESSING_FAILED: 'Completed',
      REGISTERING: 'Registering',
      PENDING: 'Pending',
      PENDING_BACKEND: 'Pending Backend',
      QUEUED: 'Queued',
      PROVISIONING: 'Provisioning',
      DEPROVISIONING: 'Deprovisioning',
      COMPLETING: 'Completing',
      REG_FAILED: 'Registration Failed',
      BOOT_FAILED: 'Boot Failed',
      PROVISION_FAILED: 'Provision Failed',
      DEPROVISION_FAILED: 'Deprovision Failed',
      CONNECTION_LOST: 'Connection Lost',
      TIMEOUT: 'Timeout',
    }[status] || status
  )
}

export const logStatusLabel = (status) => {
  return (
    {
      INFO: 'Info',
      DEBUG: 'Debug',
      WARNING: 'Warning',
      WARN: 'Warn',
      ERROR: 'Error',
      CRITICAL: 'Critical',
    }[status] || status
  )
}

export const logStatusIcon = (status) => {
  switch (status) {
    case 'WARNING':
    case 'WARN':
      return (
        <SvgIcon sx={{ mt: 1 }}>
          <WarningSvg />
        </SvgIcon>
      )
    case 'INFO':
    case 'DEBUG':
      return (
        <SvgIcon sx={{ mt: 1.6 }}>
          <InfoSvg />
        </SvgIcon>
      )
    case 'ERROR':
    case 'CRITICAL':
      return (
        <SvgIcon sx={{ mt: 1 }}>
          <ErrorSvg />
        </SvgIcon>
      )
    default:
      return null
  }
}

export const statusIcon = (status) => {
  switch (status) {
    case 'RUNNING':
    case 'STARTING':
      return (
        <SvgIcon sx={{ mr: 0.5 }}>
          <LoaderSvg />
        </SvgIcon>
      )
    case 'NEW_OBJECT':
    case 'PENDING':
    case 'REGISTERING':
    case 'PENDING_BACKEND':
      return (
        <SvgIcon sx={{ mt: 1 }}>
          <ActivitySvg />
        </SvgIcon>
      )
    case 'QUEUED':
    case 'PROVISIONING':
    case 'DEPROVISIONING':
      return (
        <SvgIcon sx={{ mt: 1 }}>
          <QueuedSvg />
        </SvgIcon>
      )
    case 'COMPLETING':
      return (
        <SvgIcon sx={{ mt: 1 }}>
          <CompletingSvg />
        </SvgIcon>
      )
    case 'COMPLETED':
    case 'POSTPROCESSING':
    case 'PENDING_POSTPROCESSING':
    case 'POSTPROCESSING_FAILED':
      return (
        <SvgIcon sx={{ mt: 1 }}>
          <CheckSvg />
        </SvgIcon>
      )
    case 'FAILED':
    case 'REG_FAILED':
    case 'BOOT_FAILED':
    case 'PROVISION_FAILED':
    case 'DEPROVISION_FAILED':
      return (
        <SvgIcon sx={{ mt: 1 }}>
          <ErrorSvg />
        </SvgIcon>
      )
    case 'CONNECTION_LOST':
      return (
        <SvgIcon sx={{ mt: 1 }}>
          <ConnectionLostSvg />
        </SvgIcon>
      )
    case 'TIMEOUT':
      return (
        <SvgIcon sx={{ mt: 1 }}>
          <TimeoutSvg />
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
        <SvgIcon sx={{ mt: 1 }}>
          <FunctionSvg />
        </SvgIcon>
      )
    case 'electron_list':
      return (
        <SvgIcon sx={{ mt: 1 }}>
          <ElectronListSvg />
        </SvgIcon>
      )
    case 'parameter':
      return (
        <SvgIcon sx={{ mt: 1 }}>
          <ParameterSvg />
        </SvgIcon>
      )
    case 'sublattice':
      return (
        <SvgIcon sx={{ mt: 1 }}>
          <SubLattice />
        </SvgIcon>
      )
    case 'electron_dict':
      return (
        <SvgIcon sx={{ mt: 1 }}>
          <ElectronDictSvg />
        </SvgIcon>
      )
    case 'attribute':
      return (
        <SvgIcon sx={{ mt: 1 }}>
          <AttributeSvg />
        </SvgIcon>
      )
    case 'generated':
      return (
        <SvgIcon sx={{ mt: 1 }}>
          <GeneratedSvg />
        </SvgIcon>
      )
    case 'subscripted':
      return (
        <SvgIcon sx={{ mt: 1 }}>
          <SubLattice />
        </SvgIcon>
      )
    case 'arg':
      return (
        <SvgIcon sx={{ mt: 1 }}>
          <ArgSvg />
        </SvgIcon>
      )
    default:
      return null
  }
}
