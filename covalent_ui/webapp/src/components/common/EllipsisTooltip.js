import React, { useRef, useEffect, useState } from 'react';
import Tooltip from '@mui/material/Tooltip';
const OverflowTip = props => {
    // Create Ref
    const textElementRef = useRef();
    const compareSize = () => {
        const compare =
            textElementRef.current.scrollWidth > textElementRef.current.clientWidth;
        setHover(compare);
    };

    // compare once and add resize listener on "componentDidMount"
    useEffect(() => {
        compareSize();
        window.addEventListener('resize', compareSize);
    }, []);

    // remove resize listener again on "componentWillUnmount"
    useEffect(() => () => {
        window.removeEventListener('resize', compareSize);
    }, []);

    // Define state and function to update the value
    const [hoverStatus, setHover] = useState(false);

    return (
        <Tooltip
            title={props.value}
            interactive
            disableHoverListener={!hoverStatus}
            style={{ fontSize: '2em' }}
        >
            <div
                ref={textElementRef}
                style={{
                    whiteSpace: 'nowrap',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    width: '200px'
                }}
            >
                {props.value}
            </div>
        </Tooltip>
    );
};

export default OverflowTip;
