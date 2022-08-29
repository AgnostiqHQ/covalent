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
import { Typography } from '@mui/material'
import { differenceInMilliseconds, isValid, parseISO } from 'date-fns'
import humanizeDuration from 'humanize-duration'
import { useEffect, useState } from 'react'

export const humanize = humanizeDuration.humanizer({
  largest: 3,
  round: true,
  delimiter: ' ',
  spacer: '',
  units: ['h', 'm', 's'],
  language: 'shortEn',
  languages: {
    shortEn: {
      y: () => 'y',
      mo: () => 'mo',
      w: () => 'w',
      d: () => 'd',
      h: () => 'h',
      m: () => 'm',
      s: () => 's',
      ms: () => 'ms',
    },
  },
})

const parseDate = (date) => (_.isString(date) ? parseISO(date) : date)

const Runtime = ({ startTime, endTime, sx }) => {
  startTime = parseDate(startTime)
  endTime = parseDate(endTime)

  if (!isValid(startTime)) {
    return ''
  }
  if (!isValid(endTime)) {
    return <RuntimeTicker sx={sx} startTime={startTime} />
  }
  return <RuntimeConst sx={sx} startTime={startTime} endTime={endTime} />
}

const RuntimeConst = ({ startTime, endTime, sx }) => {
  const diffMs = differenceInMilliseconds(startTime, endTime)
  return (
    <Typography data-testid="runTime" sx={sx}>
      {humanize(diffMs)}
    </Typography>
  )
}

const RuntimeTicker = ({ startTime, sx }) => {
  const [now, setNow] = useState(new Date())

  useEffect(() => {
    const intervalId = setInterval(() => {
      setNow(new Date())
    }, 1000)

    return () => {
      if (intervalId) {
        clearInterval(intervalId)
      }
    }
  })

  return <RuntimeConst sx={sx} startTime={startTime} endTime={now} />
}

export default Runtime
