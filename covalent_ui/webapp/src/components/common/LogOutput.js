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
import { Paper, Typography } from '@mui/material'
import { useEffect, useRef, useState } from 'react'
import { useSelector } from 'react-redux'

import api from '../../utils/api'
import Heading from './Heading'
import { isParameter } from '../../utils/misc'
import { isDemo } from '../../utils/demo/setup'

const FETCH_INTERVAL_MS = 2000
const MAX_LINES = 80

/**
 * Temporary solution to log output until backend file logs are sorted out. See
 * LogOutput below.
 */
export const LatticeOutput = ({ dispatchId }) => {
  const output = useSelector((state) => {
    const result = state.results.cache[dispatchId]
    return _.reduce(
      _.get(result, 'graph.nodes'),
      (logs, node) => {
        _.each(
          [{ key: 'stdout' }, { key: 'stderr', isErr: true }],
          ({ key, isErr }) => {
            const text = node[key]
            if (text) {
              logs.push({
                name: `${node.name} [${key}]`,
                lines: _.split(text, '\n'),
                isErr,
              })
            }
          }
        )
        return logs
      },
      []
    )
  })

  return _.map(output, (node) => <NodeOutput node={node} />)
}

const NodeOutput = ({ node }) => {
  const { name, lines, isErr } = node

  // auto-scroll to last line on updates
  const bottomRef = useRef(null)
  useEffect(() => {
    bottomRef.current.scrollIntoView({ behavoir: 'smooth' })
  }, [lines])

  return (
    <div key={name}>
      <Heading>{name}</Heading>
      <Paper>
        <Typography
          sx={{
            fontSize: 'small',
            overflow: 'auto',
            maxHeight: 200,
            whiteSpace: 'nowrap',
            color: isErr ? 'error.light' : 'inherit',
            p: 1,
          }}
        >
          {_.map(lines, (line, index) => (
            <span key={index}>
              {line}
              <br />
            </span>
          ))}
          <div ref={bottomRef} />
        </Typography>
      </Paper>
    </div>
  )
}

const LogOutput = ({ dispatchId }) => {
  const isRunning = useSelector(
    (state) => _.get(state.results.cache[dispatchId], 'status') === 'RUNNING'
  )
  const logs = useSelector((state) => {
    const result = state.results.cache[dispatchId]
    return _.reduce(
      [
        _.get(result, 'lattice'),
        // electrons
        ..._.filter(_.get(result, 'graph.nodes'), (node) => !isParameter(node)),
      ],
      (logs, node) => {
        const executor = _.get(node, 'metadata.executor')
        // log types
        _.each(['log_stdout', 'log_stderr'], (logType) => {
          const path = _.get(executor, logType)
          if (path) {
            logs.set(path, logType)
          }
        })
        return logs
      },
      // logs map: path -> log type
      new Map()
    )
  })

  return (
    <>
      {_.map([...logs.entries()], ([path, logType], index) => {
        return (
          <TailFile
            dispatchId={dispatchId}
            key={index}
            path={path}
            isRunning={isRunning}
            isStdErr={logType === 'log_stderr'}
          />
        )
      })}
    </>
  )
}

const TailFile = ({ dispatchId, path, isRunning, isStdErr }) => {
  const [lines, setLines] = useState()
  const bottomRef = useRef(null)

  const scrollToBottom = () => {
    bottomRef.current.scrollIntoView({ behavoir: 'smooth' })
  }

  // auto-scroll to last line on updates
  useEffect(() => {
    scrollToBottom()
  }, [lines])

  // tail file
  useEffect(() => {
    const fetchLog = () => {
      // TODO use demo mock api instead
      if (isDemo) {
        setLines(
          isStdErr
            ? ['Unable to fetch remote resource.']
            : _.map(_.range(20), (i) => `iteration ${i}`)
        )
        return
      }

      api
        .get(`/api/logoutput/${dispatchId}`, { params: { path, n: MAX_LINES } })
        .then((res) => {
          setLines(res.lines)
        })
        .catch((error) => {
          setLines([error && error.message])
        })
    }

    fetchLog()

    // schedule periodic fetch if running
    let intervalId = 0
    if (isRunning) {
      intervalId = setInterval(() => {
        fetchLog()
      }, FETCH_INTERVAL_MS)
    }

    return () => {
      // cancel periodic fetch
      if (intervalId) {
        clearInterval(intervalId)
      }
    }
  }, [path, isRunning, dispatchId, isStdErr])

  return (
    <div>
      <Heading>{path}</Heading>
      <Paper>
        <Typography
          sx={{
            fontSize: 'small',
            overflow: 'auto',
            maxHeight: 200,
            whiteSpace: 'nowrap',
            // color: isStdErr ? 'error.light' : 'inherit',
            p: 1,
          }}
        >
          {_.map(lines, (line, index) => (
            <span key={index}>
              {line}
              <br />
            </span>
          ))}
          <div ref={bottomRef} />
        </Typography>
      </Paper>
    </div>
  )
}

export default LogOutput
