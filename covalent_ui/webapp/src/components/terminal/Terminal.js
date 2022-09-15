

import React, { useRef, useEffect, useState } from 'react'
import { XTerm } from 'xterm-for-react'
import { FitAddon } from 'xterm-addon-fit';
import { WebLinksAddon } from 'xterm-addon-web-links';
import socket from '../../utils/socket'
import { Container, Grid } from '@mui/material';
import Typography from '@mui/material/Typography';

const Terminal = () => {
    const xtermRef = useRef()
    const webLinksAddon = new WebLinksAddon()
    const fitAddon = new FitAddon()
    const [status, setStatus] = useState('Disconnected')
    useEffect(() => {
        console.log(status)
    },[status])
    useEffect(() => {
        socket.on('disconnect', () => {
            setStatus('Disconnected')
        })
    })

    useEffect(() => {
        xtermRef.current.terminal.writeln(" Please press Enter to connect to the server terminal");
    }, [])
    useEffect(() => {
        socket.on("pty-output", function (data) {
            xtermRef.current.terminal.write(data.output);
        });
        return () => {
            socket.off('pty-output')
          }
    })
    return (
        <Container maxWidth="xl" sx={{ mb: 4, mt: 7.5, ml: 4 }}>
            <Typography variant="h4" component="h4">
                Terminal
            </Typography>
            <Grid container spacing={3} sx={{ mt: 4 }}>
                <XTerm
                    options={{
                        cursorBlink: true,
                        macOptionIsMeta: true,
                        scrollback: true,
                    }}
                    ref={xtermRef}
                    onData={(data) => {
                        socket.emit("pty-input", { input: data })
                    }}
                    addons={[fitAddon, webLinksAddon]} />
            </Grid>

        </Container>

    )
}
export default Terminal