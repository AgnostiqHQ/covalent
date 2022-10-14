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

import React, { useRef, useEffect, useState } from 'react'
import Tooltip from '@mui/material/Tooltip'
const OverflowTip = (props) => {
  // Create Ref
  const textElementRef = useRef()
  const compareSize = () => {
    const compare =
      textElementRef.current.scrollWidth > textElementRef.current.clientWidth
    setHover(compare)
  }

  // compare once and add resize listener on "componentDidMount"
  useEffect(() => {
    compareSize()
    window.addEventListener('resize', compareSize)
  }, [])

  // remove resize listener again on "componentWillUnmount"
  useEffect(
    () => () => {
      window.removeEventListener('resize', compareSize)
    },
    []
  )

  // Define state and function to update the value
  const [hoverStatus, setHover] = useState(false)

  return (
    <Tooltip
      data-testid="toolTip"
      title={props.value}
      disableHoverListener={!hoverStatus}
      style={{ fontSize: props.fontSize || '2em' }}
      >
      <div
        ref={textElementRef}
        style={{
          whiteSpace: 'nowrap',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          width: props.width || '200px'
        }}
      >
        {props.value}
      </div>
    </Tooltip>
  )
}

export default OverflowTip
