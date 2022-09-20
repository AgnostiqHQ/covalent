import NavDrawer from '../common/NavDrawer'
import { Container } from '@mui/material'
import { Box } from '@mui/system'
import { Typography } from '@mui/material'
import LogsListing from './LogsListing'

const LogsLayout = () => {
  return (
    <Box sx={{ display: 'flex' }} data-testid="dashboard">
      <NavDrawer />
      <Container maxWidth="xl" sx={{ mb: 4, mt: 7 }}>
        <Typography
          fontSize="32px"
          sx={{ color: (theme) => theme.palette.primary.white, mb: 4 }}
        >
          Logs{' '}
        </Typography>
        <LogsListing />
      </Container>
    </Box>
  )
}

export default LogsLayout
