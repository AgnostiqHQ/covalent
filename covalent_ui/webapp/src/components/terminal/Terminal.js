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

import React, { useRef, useEffect, memo } from 'react'
import { XTerm } from 'xterm-for-react'
import { FitAddon } from 'xterm-addon-fit'
import io from 'socket.io-client'
import './index.css'
export const Terminal = () => {
  const xtermRef = useRef()
  const fitAddon = new FitAddon()
  const socket = io(process.env.REACT_APP_SOCKET_URL, {
    // required for CORS
    withCredentials: true,
  })
  useEffect(() => {
    if (socket) {
      socket.on('connect', () => {
        console.debug(
          `socket ${socket.id} terminal connected: ${socket.connected}`
        )
        fitAddon.fit()
        const dims = {
          cols: xtermRef?.current?.terminal.cols,
          rows: xtermRef?.current?.terminal.rows,
        }
        if (dims.rows) {
          xtermRef?.current?.terminal.focus()
          socket.emit('start_terminal', dims)
          socket.emit('resize', dims)
        }
      })
    }
  })
  useEffect(() => {
    if (socket) {
      return () => {
        socket.disconnect()
      }
    }
  })
  useEffect(() => {
    if (socket) {
      socket.on('pty-output', function (data) {
        xtermRef?.current?.terminal.write(data.output)
      })
    }
  })
  return (
    <>
      {socket && (
        <XTerm
          data-testid="terminal"
          options={{
            cursorBlink: true,
            macOptionIsMeta: true,
            scrollback: 500,
            theme: {
              background: '#08081A',
              foreground: '#AEB6FF',
            },
          }}
          className="term"
          ref={xtermRef}
          onData={(data) => {
            socket.emit('pty-input', { input: data })
          }}
          addons={[fitAddon]}
        />
      )}
    </>
  )
}
export default memo(Terminal)
