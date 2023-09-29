/**
 * This file is part of Covalent.
 *
 * Licensed under the Apache License 2.0 (the "License"). A copy of the
 * License may be obtained with this software package or at
 *
 *     https://www.apache.org/licenses/LICENSE-2.0
 *
 * Use of this file is prohibited except in compliance with the License.
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
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
          width: props.width || '200px',
          '@media (min-width: 1500px)': {
            width: '280px',
          },
          '@media (min-width: 1700px)': {
            width: '300px',
          },
        }}
      >
        {props.value}
      </div>
    </Tooltip>
  )
}

export default OverflowTip
