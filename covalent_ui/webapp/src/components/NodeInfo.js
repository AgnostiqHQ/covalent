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
import {
  Paper,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableRow,
} from '@mui/material'
import { TabContext, TabList, TabPanel } from '@mui/lab'
import { useState } from 'react'
import { useSelector } from 'react-redux'

import { Light as SyntaxHighlighter } from 'react-syntax-highlighter'
import python from 'react-syntax-highlighter/dist/esm/languages/hljs/python'
import dark from 'react-syntax-highlighter/dist/esm/styles/hljs/dark'
import { formatDate } from '../utils/misc'
import Runtime from './results/Runtime'
// import LogOutput from './LogOutput'

SyntaxHighlighter.registerLanguage('python', python)

const NodeInfo = ({ dispatchId, nodeId }) => {
  const node = useSelector((state) => {
    const result = state.results.cache[dispatchId]
    return _.find(_.get(result, 'graph.nodes'), (node) => {
      return String(_.get(node, 'id')) === String(nodeId)
    })
  })

  const [tab, setTab] = useState('details')

  if (!node) {
    return null
  }
  const src = node.function_string || String(node.output)

  return (
    <TabContext value={tab}>
      <TabList onChange={(e, newTab) => setTab(newTab)}>
        <Tab label="Details" value="details" />
        <Tab label="Code" value="code" />
        <Tab label="Output" value="output" />
      </TabList>

      <TabPanel value="code" sx={{ p: 0, fontSize: 14 }}>
        <SyntaxHighlighter language="python" style={dark}>
          {_.trim(src, '\n')}
        </SyntaxHighlighter>
      </TabPanel>

      <TabPanel value="details" sx={{ px: 0, py: 1 }}>
        <Paper sx={{ width: 'fit-content' }}>
          <Table size="small">
            <TableBody>
              {_.map(
                [
                  ['name', node.name],
                  ['status', node.status],
                  [
                    'runtime',
                    <Runtime
                      startTime={node.start_time}
                      endTime={node.end_time}
                    />,
                  ],
                  ['start', formatDate(node.start_time)],
                  ['end', formatDate(node.end_time)],
                  ['error', node.error],
                ],
                ([key, data]) => (
                  <TableRow hover key={key}>
                    <TableCell align="right">{key}</TableCell>
                    <TableCell>{data}</TableCell>
                  </TableRow>
                )
              )}
            </TableBody>
          </Table>
        </Paper>
      </TabPanel>

      <TabPanel value="output" sx={{ px: 0, py: 1 }}>
        {/* <LogOutput path="/home/valentin/code/TODO" /> */}
      </TabPanel>
    </TabContext>
  )
}

export default NodeInfo
