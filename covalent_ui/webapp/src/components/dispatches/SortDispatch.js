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

import React from 'react'
import { Typography, Chip, Skeleton } from '@mui/material'
import { Box } from '@mui/system'
const SortDispatch = (props) => {
  const {
    title,
    count,
    isFetching,
    setFilterValue,
    isSelected,
    setSelected,
    setOffset,
  } = props

  return (
    <Box
      onClick={() => {
        setFilterValue(title.toUpperCase())
        setSelected([])
        setOffset(0)
      }}
      sx={{
        display: 'flex',
        alignItems: 'center',
        cursor: 'default',
        fontWeight: 'bold',
        color: isSelected ? (theme) => theme.palette.text.secondary : null,
        '.title': {
          color: isSelected ? (theme) => theme.palette.text.secondary : null,
        },
        '.chipContainer': {
          cursor: isSelected ? 'pointer' : 'default',
          color: isSelected ? (theme) => theme.palette.text.secondary : null,
          fontWeight: isSelected ? 'bold' : null,
          background: (theme) => theme.palette.background.paper,
          border: '1 px solid',
          borderColor: (theme) =>
            isSelected
              ? theme.palette.primary.blue04
              : theme.palette.background.paper,
        },
        '&:hover': {
          '.title': {
            cursor: 'pointer',
            color: (theme) => theme.palette.text.secondary,
          },

          '.chipContainer': {
            cursor: 'pointer',
            color: (theme) => theme.palette.text.secondary,
            fontWeight: 'bold',
            border: '1 px solid',
            borderColor: (theme) => theme.palette.primary.blue04,
          },
        },
      }}
    >
      <Typography
        className="title"
        mr={1}
        sx={{
          color: (theme) => theme.palette.text.tertiary,
          fontSize: '0.875rem',
        }}
      >
        {title}
      </Typography>

      {!isFetching ? (
        <Chip
          label={count ? count : 0}
          className="chipContainer"
          sx={{
            minWidth: '24px',
            height: '24px',
            color: (theme) => theme.palette.text.tertiary,
            borderRadius: '8px',
            border: '1px solid ',
            borderColor: (theme) => theme.palette.background.coveBlack03,
            backgroundColor: (theme) => theme.palette.background.coveBlack03,
            '&:hover': {
              cursor: 'default',
              border: '1px solid ',
              borderColor: (theme) => theme.palette.primary.blue04,
            },
            '& .MuiChip-label': { fontSize: '14px', padding: '0' },
          }}
        />
      ) : (
        <Skeleton width={33} height={50} />
      )}
    </Box>
  )
}

export default SortDispatch
