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

import { Box, SvgIcon } from '@mui/material'

import { ReactComponent as AtomSvg } from '../../assets/atom.svg'

const ErrorCard = ({ showElectron = false, error }) => {
  if (!error) {
    return null
  }

  return (
    <Box
    data-testid="errorCard"
      sx={{
        fontSize: 'body2.fontSize',
        display: 'flex',
        whiteSpace: 'pre-line',
        alignItems: 'center',
        mt: 2,
        mb: 2,
        px: 2,
        py: 1,
        border: '0.5px solid rgba(227, 80, 80, 0.5)',
        borderRadius: '4px',
        overflowWrap: 'anywhere',
        background:
          'linear-gradient(90deg, rgba(73, 12, 12, 0.5) 0%, rgba(4, 4, 6, 0.5) 100%)',
      }}
    >
      {showElectron && (
        <SvgIcon data-testid='electronIcon' sx={{ fontSize: 'inherit', mr: 1.5 }}>
          <AtomSvg />
        </SvgIcon>
      )}
      {error}
    </Box>
  )
}

export default ErrorCard
