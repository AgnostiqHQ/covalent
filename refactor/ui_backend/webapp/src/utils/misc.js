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
import { CircularProgress } from '@mui/material'
import {
  CancelOutlined,
  CheckCircleOutline,
  WarningAmber,
} from '@mui/icons-material'

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
    RUNNING: theme.palette.primary.main,
    COMPLETED: theme.palette.success.main,
    FAILED: theme.palette.error.main,
  }[status]
}

export const statusLabel = (status) => {
  return (
    {
      RUNNING: 'Running',
      COMPLETED: 'Completed',
      FAILED: 'Failed',
      NEW_OBJECT: 'Pending',
    }[status] || status
  )
}

export const statusIcon = (status) => {
  switch (status) {
    case 'RUNNING':
      return <CircularProgress size="1rem" />
    case 'COMPLETED':
      return <CheckCircleOutline />
    case 'FAILED':
      return <WarningAmber />
    case 'CANCELLED':
      return <CancelOutlined />
    default:
      return null
  }
}
