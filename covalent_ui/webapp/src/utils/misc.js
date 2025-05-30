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

import _ from 'lodash'
import { isValid, format, parseISO } from 'date-fns'
import theme from './theme'
import { SvgIcon } from '@mui/material'
import { ReactComponent as ActivitySvg } from '../assets/status/pending.svg'
import { ReactComponent as CheckSvg } from '../assets/status/checkmark.svg'
import { ReactComponent as ErrorSvg } from '../assets/status/error.svg'
import { ReactComponent as CancelSvg } from '../assets/status/stop.svg'
import { ReactComponent as LoaderSvg } from '../assets/status/running.svg'
import { ReactComponent as FunctionSvg } from '../assets/nodeType/fuction.svg'
import { ReactComponent as ParameterSvg } from '../assets/nodeType/parameter.svg'
import { ReactComponent as SubLattice } from '../assets/nodeType/sublattice.svg'
import { ReactComponent as RunningSvg } from '../assets/sublattice/running.svg'
import { ReactComponent as FailedSvg } from '../assets/sublattice/failed.svg'
import { ReactComponent as SuccessSvg } from '../assets/sublattice/success.svg'
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
import { ReactComponent as RunningTopBarSvg } from '../assets/sublattice/runningTopBar.svg'
import { ReactComponent as FailedTopBarSvg } from '../assets/sublattice/failedTopBar.svg'
import { ReactComponent as SuccessTopBarSvg } from '../assets/sublattice/successTopBar.svg'
import './style.css'

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

export const isPostProcess = (node) => node?.name.startsWith(':postprocess:')

export const displayStatus = (status) => _.startCase(_.lowerCase(status))

export const Prettify = (inputString, type) => {
  let stringWithoutUnderscores = inputString?.replace(/[_<>]/g, ' ')
  stringWithoutUnderscores = stringWithoutUnderscores?.replace(/:/g, ' ')
  if (type === 'sublattice') {
    stringWithoutUnderscores = stringWithoutUnderscores?.replace(
      /sublattice\s+/gi,
      'Sublattice '
    )
  }
  stringWithoutUnderscores = stringWithoutUnderscores?.replace(/parameter/g, '')

  // Capitalize the strings
  stringWithoutUnderscores = stringWithoutUnderscores
    ?.toLowerCase()
    .replace(/\b\w/g, (l) => l.toUpperCase())

  // Add a gap before the return statement
  if (stringWithoutUnderscores === inputString) {
    return inputString
  }

  return stringWithoutUnderscores
}

export const statusColor = (status) => {
  return {
    RUNNING: theme.palette.running.main,
    STARTING: theme.palette.running.main,
    NEW_OBJECT: theme.palette.queued.main,
    COMPLETED: theme.palette.success.main,
    FAILED: theme.palette.error.main,
    CANCELLED: theme.palette.error.main,
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
    WARNING: theme.palette.warning.main,
    INFO: theme.palette.info.main,
    DEBUG: theme.palette.info.main,
    WARN: theme.palette.warning.main,
    ERROR: theme.palette.error.main,
    CRITICAL: theme.palette.error.main,
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
        <SvgIcon
          aria-label={status}
          sx={{ mt: 0.6, mr: 0.7, fontSize: '18px' }}
        >
          <WarningSvg />
        </SvgIcon>
      )
    case 'INFO':
    case 'DEBUG':
      return (
        <SvgIcon aria-label={status} sx={{ mt: 0.6 }}>
          <InfoSvg />
        </SvgIcon>
      )
    case 'ERROR':
    case 'CRITICAL':
      return (
        <SvgIcon
          aria-label={status}
          sx={{ mt: 0.6, mr: 0.7, fontSize: '18px' }}
        >
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
        <LoaderSvg className='circleRunningStatus' aria-label={status} />
      )
    case 'NEW_OBJECT':
    case 'PENDING':
    case 'REGISTERING':
    case 'PENDING_BACKEND':
      return (
        <SvgIcon aria-label={status} sx={{ mt: 1 }}>
          <ActivitySvg />
        </SvgIcon>
      )
    case 'QUEUED':
    case 'PROVISIONING':
    case 'DEPROVISIONING':
      return (
        <SvgIcon aria-label={status} sx={{ mt: 1 }}>
          <QueuedSvg />
        </SvgIcon>
      )
    case 'COMPLETING':
      return (
        <SvgIcon aria-label={status} sx={{ mt: 1 }}>
          <CompletingSvg />
        </SvgIcon>
      )
    case 'COMPLETED':
    case 'POSTPROCESSING':
    case 'PENDING_POSTPROCESSING':
    case 'POSTPROCESSING_FAILED':
      return (
        <SvgIcon aria-label={status} sx={{ mt: 1 }}>
          <CheckSvg />
        </SvgIcon>
      )
    case 'FAILED':
    case 'REG_FAILED':
    case 'BOOT_FAILED':
    case 'PROVISION_FAILED':
    case 'DEPROVISION_FAILED':
      return (
        <SvgIcon aria-label={status} sx={{ mt: 1.3 }}>
          <ErrorSvg />
        </SvgIcon>
      )
    case 'CONNECTION_LOST':
      return (
        <SvgIcon aria-label={status} sx={{ mt: 1 }}>
          <ConnectionLostSvg />
        </SvgIcon>
      )
    case 'TIMEOUT':
      return (
        <SvgIcon aria-label={status} sx={{ mt: 1 }}>
          <TimeoutSvg />
        </SvgIcon>
      )
    case 'CANCELLED':
      return (
        <SvgIcon aria-label={status} sx={{ mt: 1 }}>
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
        <SvgIcon aria-label={type} sx={{ mt: 1.2 }}>
          <FunctionSvg />
        </SvgIcon>
      )
    case 'electron_list':
      return (
        <SvgIcon aria-label={type} sx={{ mt: 1 }}>
          <ElectronListSvg />
        </SvgIcon>
      )
    case 'parameter':
      return (
        <SvgIcon aria-label={type} sx={{ mt: 1.6 }}>
          <ParameterSvg />
        </SvgIcon>
      )
    case 'sublattice':
      return (
        <SvgIcon aria-label={type} sx={{ mt: 1 }}>
          <SubLattice />
        </SvgIcon>
      )
    case 'electron_dict':
      return (
        <SvgIcon aria-label={type} sx={{ mt: 1 }}>
          <ElectronDictSvg />
        </SvgIcon>
      )
    case 'attribute':
      return (
        <SvgIcon aria-label={type} sx={{ mt: 1 }}>
          <AttributeSvg />
        </SvgIcon>
      )
    case 'generated':
      return (
        <SvgIcon aria-label={type} sx={{ mt: 1 }}>
          <GeneratedSvg />
        </SvgIcon>
      )
    case 'subscripted':
      return (
        <SvgIcon aria-label={type} sx={{ mt: 1 }}>
          <SubLattice />
        </SvgIcon>
      )
    case 'arg':
      return (
        <SvgIcon aria-label={type} sx={{ mt: 1 }}>
          <ArgSvg />
        </SvgIcon>
      )
    default:
      return null
  }
}

export const sublatticeIcon = (type, sub) => {
  switch (type) {
    case 'COMPLETED':
      return (
        <SvgIcon aria-label="COMPLETED" sx={{ mr: 1, fontSize: '28px' }}>
          <SuccessSvg />
        </SvgIcon>
      )
    case 'FAILED':
      return (
        <SvgIcon aria-label="FAILED" sx={{ mr: 1, fontSize: '28px' }}>
          <FailedSvg />
        </SvgIcon>
      )
    case 'RUNNING':
      return (
        <SvgIcon aria-label="RUNNING" sx={{ mr: 1, fontSize: '28px' }}>
          <RunningSvg />
        </SvgIcon>
      )

    default:
      return null
  }
}

export const sublatticeIconTopBar = (type, sub) => {
  switch (type) {
    case 'COMPLETED':
      return (
        <SvgIcon
          aria-label="COMPLETED"
          sx={{ mr: 1, mt: 1, ml: 1, fontSize: '28px' }}
        >
          <SuccessTopBarSvg />
        </SvgIcon>
      )
    case 'FAILED':
      return (
        <SvgIcon
          aria-label="FAILED"
          sx={{ mr: 1, mt: 1, ml: 1, fontSize: '28px' }}
        >
          <FailedTopBarSvg />
        </SvgIcon>
      )
    case 'RUNNING':
      return (
        <SvgIcon
          aria-label="RUNNING"
          sx={{ mr: 1, mt: 1, ml: 1, fontSize: '28px' }}
        >
          <RunningTopBarSvg />
        </SvgIcon>
      )

    default:
      return null
  }
}

export const getLocalStartTime = (time) => {
  let startTimeToLocal = new Date((time = time + 'Z'))
  return startTimeToLocal.toISOString()
}
