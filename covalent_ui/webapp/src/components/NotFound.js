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

import {
  AppBar,
  Container,
  Link,
  Paper,
  Toolbar,
  Typography,
} from '@mui/material'

import { ReactComponent as Logo } from '../assets/covalent-full-logo.svg'
import NavDrawer from '../components/common/NavDrawer'

const NotFound = ({ text = 'Page not found.', children }) => {
  return (
    <>
      <NavDrawer />
      <Container
        maxWidth="xl"
        sx={{
          mb: 4,
          mt: 7,
          ml: 10,
          width: '70%',
          '@media (min-width: 1700px)': {
            ml: '12%',
          },
        }}
      >
        <AppBar position="static" color="transparent">
          <Toolbar disableGutters sx={{ my: 2 }}>
            <Link href="/">
              <Logo data-testid="logo" />
            </Link>
          </Toolbar>
        </AppBar>

        <Paper elevation={4} sx={{ p: 2 }}>
          {children || (
            <Typography data-testid="message" variant="h5">
              {text}
            </Typography>
          )}
        </Paper>
      </Container>
    </>
  )
}

export default NotFound
