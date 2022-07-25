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
 import { SvgIcon} from '@mui/material'
 import { ReactComponent as ActivitySvg } from '../assets/status/activity.svg'
 import { ReactComponent as CheckSvg } from '../assets/status/checkmark.svg'
 import { ReactComponent as ErrorSvg } from '../assets/status/error.svg'
 import { ReactComponent as CancelSvg } from '../assets/status/stop.svg'
 import { ReactComponent as LoaderSvg } from '../assets/loader.svg'

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
     FAILED: theme.palette.error.main,
     CANCELLED:theme.palette.error.main
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
     }[status] || status
   )
 }

 export const statusIcon = (status) => {
   switch (status) {
     case 'RUNNING':
       return (
         <SvgIcon sx={{ fontSize: '16', mr: 0.5 }}>
           <LoaderSvg />
         </SvgIcon>
       )
     case 'NEW_OBJECT':
       return (
         <SvgIcon sx={{ fontSize: '16', mt: 1 }}>
           <ActivitySvg />
         </SvgIcon>
       )
     case 'COMPLETED':
       return (
         <SvgIcon sx={{ fontSize: '16', mr: 0.5 }}>
           <CheckSvg />
         </SvgIcon>
       )
     case 'FAILED':
       return (
         <SvgIcon sx={{ fontSize: '16', mt: 1 }}>
           <ErrorSvg />
         </SvgIcon>
       )
     case 'CANCELLED':
       return (
         <SvgIcon sx={{ fontSize: '16', mt: 1 }}>
           <CancelSvg />
         </SvgIcon>
       )
     default:
       return null
   }
 }
