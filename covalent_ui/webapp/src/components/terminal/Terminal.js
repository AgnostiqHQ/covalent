

import React, { useRef, useEffect } from 'react'
import { XTerm } from 'xterm-for-react'
import { FitAddon } from 'xterm-addon-fit';
import './index.css';
const Terminal = () => {
    const xtermRef = useRef()
    const fitAddon = new FitAddon();
    useEffect(() => {
        fitAddon.fit();
        xtermRef?.current?.terminal.writeln("$ This is just a static terminal"
        );
        xtermRef?.current?.terminal.writeln("$ Please install Covalent to use this exciting new feature!"
        );
        xtermRef?.current?.terminal.writeln("$ npm install -g mimik"
        );
        xtermRef?.current?.terminal.writeln("$ pip show covalent"
        );
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
