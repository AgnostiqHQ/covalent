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

import React from 'react'
import { useSelector, useDispatch } from 'react-redux'
import { Box, Typography, Skeleton, SvgIcon, Tooltip } from '@mui/material'
import {
  statusIcon,
  statusColor,
  statusLabel,
  sublatticeIconTopBar,
} from '../../utils/misc'
import { resetSublatticesId } from '../../redux/latticeSlice'
import { ReactComponent as BackButton } from '../../assets/back.svg'
import OverflowTip from '../common/EllipsisTooltip'

const DispatchTopBar = () => {
  const dispatch = useDispatch()
  const drawerLatticeDetails = useSelector(
    (state) => state.latticeResults.latticeDetails
  )
  const drawerLatticeDetailsFetching = useSelector(
    (state) => state.latticeResults.latticeDetailsResults.isFetching
  )
  const sublatticesDispatchId = useSelector(
    (state) => state.latticeResults.sublatticesId
  )

  return (
    <>
      <div>
        <Box
          data-testid="topbar"
          sx={{
            position: 'absolute',
            top: 0,
            width: '100%',
            height: '75px',
            justifyContent: 'center',
            zIndex: 95,
            display: 'flex',
            alignItems: 'center',
            mt: 0,
            paddingLeft: '27%',
            ml: 0,
            backgroundColor: (theme) => theme.palette.background.default,
          }}
        >
          <Box>
            <LatticeStatusCard
              dispatchId={drawerLatticeDetails.dispatch_id}
              latDetails={drawerLatticeDetails}
              isFetching={drawerLatticeDetailsFetching}
              sublatticesDispatchId={sublatticesDispatchId}
              dispatch={dispatch}
            />
          </Box>
        </Box>
      </div>
    </>
  )
}

export default DispatchTopBar

const LatticeStatusCard = ({
  latDetails,
  isFetching,
  sublatticesDispatchId,
  dispatch,
}) => {
  return (
    <Box sx={{ my: 0, pt: 2 }} data-testid="topbarcard">
      <Box sx={{ position: 'absolute', left: 490, mt: 1 }}>
        {sublatticesDispatchId && (
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
            }}
          >
            <Typography sx={{ display: 'flex' }}>Viewing:</Typography>
            {sublatticeIconTopBar(sublatticesDispatchId?.status, true)}

            <Typography sx={{ display: 'flex' }}>
              <OverflowTip
                width="70px"
                fontSize="14px"
                value={sublatticesDispatchId?.latticeName}
              />
            </Typography>
            <Tooltip title="Revert back to main lattice">
              <SvgIcon
                onClick={() => dispatch(resetSublatticesId())}
                sx={{
                  cursor: 'pointer',
                  width: '50px',
                  fontSize: '30px',
                }}
              >
                <BackButton />
              </SvgIcon>
            </Tooltip>
          </Box>
        )}
      </Box>
      <Box
        sx={{
          display: 'flex',
          mt: 1.5,
        }}
      >
        <Box
          sx={{
            borderRight: !isFetching ? '1px solid #303067' : 'none',
            height: '25px',
            display: 'flex',
            alignItems: 'center',
            pr: 4.4,
          }}
        >
          {!latDetails && isFetching ? (
            <Skeleton
              width={150}
              height={60}
              sx={{
                alignItems: 'center',
                py: 2,
                mt: 4,
              }}
            />
          ) : (
            <Box
              sx={{
                color: statusColor(latDetails.status),
                display: 'flex',
                fontSize: '1.125rem',
                alignItems: 'center',
                justifySelf: 'center',
              }}
            >
              {/* {statusIcon(latDetails.status)}
                &nbsp; */}
              {statusLabel(latDetails.status)}
            </Box>
          )}
        </Box>

        <Box sx={{ justifySelf: 'center' }}>
          {!latDetails &&isFetching ? (
            <Skeleton
              width={150}
              height={60}
              sx={{
                alignItems: 'center',
                py: 2,
                ml: 2,
              }}
            />
          ) : (
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                pl: 4.4,
                height: '25px',
              }}
            >
              {statusIcon(latDetails.status)}
              <Typography fontSize="body2.fontSize" sx={{ ml: 1 }}>
                <Box
                  component="span"
                  sx={{
                    color:
                      latDetails.status !== 'COMPLETED'
                        ? statusColor(latDetails.status)
                        : '',
                  }}
                >
                  {latDetails.total_electrons_completed}
                </Box>
                &nbsp;/ {latDetails.total_electrons}
              </Typography>
            </Box>
          )}
        </Box>
      </Box>
    </Box>
  )
}
