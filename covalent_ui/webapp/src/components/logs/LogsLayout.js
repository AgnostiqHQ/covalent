import NavDrawer, { navDrawerWidth } from '../common/NavDrawer'
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
          fontSize="h4.fontSize"
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
