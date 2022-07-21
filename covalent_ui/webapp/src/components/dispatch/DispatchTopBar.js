import React from 'react'
import { useSelector } from 'react-redux'
import { Box, Typography, Skeleton } from '@mui/material'
import { statusIcon, statusColor, statusLabel } from '../../utils/misc'

const DispatchTopBar = () => {
  const drawerLatticeDetails = useSelector(
    (state) => state.latticeResults.latticeDetails
  )
  const drawerLatticeDetailsFetching = useSelector(
    (state) => state.latticeResults.latticeDetailsResults.isFetching
  )

  return (
    <>
      <Box
        sx={{
          position: 'absolute',
          top: 0,
          width: '100%',
          height: '55px',
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
        {/* status */}
        <Box>
          <LatticeStatusCard
            dispatchId={drawerLatticeDetails.dispatch_id}
            latDetails={drawerLatticeDetails}
            isFetching={drawerLatticeDetailsFetching}
          />
        </Box>
      </Box>
    </>
  )
}

export default DispatchTopBar

const LatticeStatusCard = ({ _dispatchId, latDetails, isFetching }) => {
  return (
    <Box sx={{ my: 0, pt: 1 }}>
      <Box
        sx={{
          display: 'flex',
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
          {isFetching ? (
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
          {isFetching ? (
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
