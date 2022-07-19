import React from 'react'
import { useSelector } from 'react-redux'
import {
  Box,
  CircularProgress,
  IconButton,
  Tooltip,
  Typography,
  SvgIcon,
  Skeleton,
} from '@mui/material'
import { ChevronLeft } from '@mui/icons-material'
import CopyButton from '../common/CopyButton'
import {
  statusIcon,
  truncateMiddle,
  statusColor,
  statusLabel,
} from '../../utils/misc'
import { ReactComponent as TreeSvg } from '../../assets/tree.svg'

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
          justifyContent: 'space-evenly',
          zIndex: 95,
          display: 'flex',
          alignItems: 'center',
          mt: 0,
          pt: 0,
          ml: 7,
          backgroundColor: (theme) => theme.palette.background.default,
        }}
      >
        <Box sx={{ width: '35%', display: 'flex', alignItems: 'center' }}>
          <IconButton href="/" sx={{ color: 'text.disabled', mr: 1 }}>
            <ChevronLeft />
          </IconButton>

          <SvgIcon
            component={TreeSvg}
            sx={{ verticalAlign: 'middle', marginTop: 1 }}
          />
          {drawerLatticeDetailsFetching ? (
            <Skeleton width={200} />
          ) : (
            <Tooltip title={drawerLatticeDetails?.dispatch_id} placement="top">
              <Typography
                component="span"
                sx={{ mx: 1, verticalAlign: 'middle' }}
              >
                {truncateMiddle(drawerLatticeDetails.dispatch_id, 8, 13)}
              </Typography>
            </Tooltip>
          )}

          <CopyButton
            content={drawerLatticeDetails.dispatch_id}
            size="small"
            title="Copy dispatch Id"
            isBorderPresent
          />
        </Box>

        {/* status */}
        <Box sx={{ width: '20%', ml: 20, my: 2 }}>
          <LatticeStatusCard
            dispatchId={drawerLatticeDetails.dispatch_id}
            latDetails={drawerLatticeDetails}
            isFetching={drawerLatticeDetailsFetching}
          />
        </Box>
        <Box sx={{ width: '30%' }}></Box>
      </Box>
    </>
  )
}

export default DispatchTopBar

const LatticeStatusCard = ({ dispatchId, latDetails, isFetching }) => {
  return (
    <Box sx={{ my: 0 }}>
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: 'repeat(2, 1fr)',
        }}
      >
        <Box sx={{ borderRight: '1px solid #303067' }}>
          {isFetching ? (
            <Skeleton
              width={150}
              height={60}
              sx={{
                alignItems: 'center',
                py: 2,
                mr: 2,
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
                py: 1.5,
              }}
            >
              {statusIcon(latDetails.status)}
              &nbsp;
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
                py: 1,
              }}
            >
              <Typography fontSize="body2.fontSize">
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

              <Box sx={{ ml: 2, position: 'relative' }}>
                <CircularProgress
                  variant="determinate"
                  sx={(theme) => ({
                    color: theme.palette.secondary.main,
                  })}
                  size="2rem"
                  value={100}
                />
                <CircularProgress
                  style={{ color: statusColor(latDetails.status) }}
                  sx={{ position: 'absolute', left: 0 }}
                  variant="determinate"
                  size="2rem"
                  value={
                    (latDetails.total_electrons_completed * 100) /
                    latDetails.total_electrons
                  }
                />
              </Box>
            </Box>
          )}
        </Box>
      </Box>
    </Box>
  )
}
