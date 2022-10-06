

import React, { useRef, useEffect, useState } from 'react'
import { XTerm } from 'xterm-for-react'
import { FitAddon } from 'xterm-addon-fit';
import io from 'socket.io-client'
import './index.css';
const Terminal = () => {
    const xtermRef = useRef()
    const fitAddon = new FitAddon();
    const socket = io(process.env.REACT_APP_SOCKET_URL, {
        // required for CORS
        withCredentials: true,
    })
    useEffect(() => {
        if (socket) {
            socket.on('connect', () => {
                console.debug(`socket ${socket.id} terminal connected: ${socket.connected}`)
                fitAddon.fit();
                const dims = { cols: xtermRef?.current?.terminal.cols, rows: xtermRef?.current?.terminal.rows };
                if (dims.rows) {
                    socket.emit('start_terminal', dims);
                    socket.emit("resize", dims);
                }
            })
        }
    })
    useEffect(() => {
        if (socket) {
            return () => {
                socket.emit('stop_terminal')
            }
        }

    })
    useEffect(() => {
        if (socket) {
            socket.on("pty-output", function (data) {
                xtermRef?.current?.terminal.write(data.output);
            });
        }
    })
    return (
        <>
            {socket && (
                <XTerm
                    options={{
                        cursorBlink: true,
                        macOptionIsMeta: true,
                        scrollback: 500,
                        theme: {
                            background: '#08081A',
                        }
                    }}
                    className='term'
                    ref={xtermRef}
                    onData={(data) => {
                        socket.emit("pty-input", { input: data })
                    }}
                    addons={[fitAddon]} />
            )}
        </>
    )
}
export default Terminal
