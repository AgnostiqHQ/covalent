

import React, { useRef, useEffect, useState } from 'react'
import { XTerm } from 'xterm-for-react'
import { FitAddon } from 'xterm-addon-fit';
import { WebLinksAddon } from 'xterm-addon-web-links';
import socket from '../../utils/socket'
import { Container, Grid, Chip } from '@mui/material';
import Typography from '@mui/material/Typography';

const Terminal = () => {
    const xtermRef = useRef()
    const webLinksAddon = new WebLinksAddon()
    const fitAddon = new FitAddon();
    useEffect(() => {
        socket.emit('start_terminal', () => {
            fitAddon.fit();
            const dims = { cols: xtermRef.current.terminal.cols, rows: xtermRef.current.terminal.rows };
            socket.emit("resize", dims);
            console.debug(`socket ${socket.id} connected: ${socket.connected}`)
        })
        return () => {
            socket.emit('stop_terminal')
        }
    })
    useEffect(() => {
        socket.on("pty-output", function (data) {
            xtermRef.current.terminal.write(data.output);
        });
        return () => {
            socket.off('pty-output')
        }
    })
    return (
        <Container sx={{ mb: 4, mt: 7.5, ml: 5 }}>
            <Grid xs={12} sx={{ mb: 4 }}>
                <Typography sx={{ fontSize: '2rem' }} component="h4" display="inline">
                    Terminal
                </Typography>
                <Chip sx={{ height: '24px', ml: 1, mb: 1.5, fontSize: '0.75rem', color: '#FFFFFF' }} label='BETA' variant='outlined' />
            </Grid>
            <XTerm
                options={{
                    cursorBlink: true,
                    macOptionIsMeta: true,
                    scrollback: true,
                    theme: {
                        background: '#08081A'
                    },
                }}
                ref={xtermRef}
                onData={(data) => {
                    socket.emit("pty-input", { input: data })
                }}
                addons={[fitAddon, webLinksAddon]} />
        </Container>

    )
}
export default Terminal