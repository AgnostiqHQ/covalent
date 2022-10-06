

import React, { useRef, useEffect } from 'react'
import { XTerm } from 'xterm-for-react'
import { FitAddon } from 'xterm-addon-fit';
import './index.css';
const Terminal = () => {
    const xtermRef = useRef()
    const fitAddon = new FitAddon();
    useEffect(() => {
        xtermRef?.current?.terminal.write("This is just a static terminal and won't perform any commands. Install Covalent to use this exciting new feature !");
    })
    return (
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
            addons={[fitAddon]} />
    )
}
export default Terminal
