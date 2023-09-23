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

// eslint-disable-next-line no-unused-vars
const parseDate = (date) => (_.isString(date) ? parseISO(date) : date)

const Runtime = ({ startTime, endTime, sx }) => {
  let startTimeToLocal = new Date((startTime = startTime + 'Z'))
  let endTimeToLocal = new Date((endTime = endTime + 'Z'))
  if (!isValid(startTimeToLocal)) {
    return ''
  }
  if (!isValid(endTimeToLocal)) {
    return <RuntimeTicker sx={sx} startTime={startTimeToLocal} />
  }
  return (
    <RuntimeConst
      sx={sx}
      startTime={startTimeToLocal}
      endTime={endTimeToLocal}
    />
  )
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
