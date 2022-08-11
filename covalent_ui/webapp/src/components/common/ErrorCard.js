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

import { Box, SvgIcon } from '@mui/material'

import { ReactComponent as AtomSvg } from '../../assets/atom.svg'

const ErrorCard = ({ showElectron = false, error }) => {
  if (!error) {
    return null
  }

  return (
    <Box
      sx={{
        fontSize: 'body2.fontSize',
        display: 'flex',
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
        <SvgIcon sx={{ fontSize: 'inherit', mr: 1.5 }}>
          <AtomSvg />
        </SvgIcon>
      )}
      {error}
    </Box>
  )
}

export default ErrorCard
