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

import { Paper } from '@mui/material'
import _ from 'lodash'
import { useEffect, useState } from 'react'

import api from '../utils/api'

const LogOutput = ({ path }) => {
  const [lines, setLines] = useState()

  useEffect(() => {
    const fetchLog = () => {
      api
        .get('/api/logoutput', { params: { path, n: 10 } })
        .then((res) => {
          setLines(res.lines)
        })
        .catch(() => {
          // TODO handle errors
        })
    }

    const intervalId = setInterval(() => {
      fetchLog()
    }, 1000)

    return () => {
      if (intervalId) {
        clearInterval(intervalId)
      }
    }
  }, [path])

  return (
    <div>
      <div>path: {path}</div>
      <Paper sx={{ fontSize: 12 }}>
        <pre>{_.join(lines, '\n')}</pre>
      </Paper>
    </div>
  )
}

export default LogOutput
