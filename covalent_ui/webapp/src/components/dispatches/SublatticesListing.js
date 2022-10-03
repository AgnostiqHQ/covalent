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

import _ from 'lodash'
import { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useParams } from 'react-router-dom'
import {
  Table,
  TableRow,
  TableHead,
  TableCell,
  Tooltip,
  TableBody,
  Typography,
  TableContainer,
  TableSortLabel,
  Box,
  styled,
  tableCellClasses,
  tableRowClasses,
  tableBodyClasses,
  tableSortLabelClasses,
  Skeleton,
  linkClasses,
  Grid,
} from '@mui/material'
import { sublatticeIcon } from '../../utils/misc'

import {
  sublatticesListDetails,
  sublatticesDispatchId,
} from '../../redux/latticeSlice'
import Runtime from './Runtime'
import OverflowTip from '../common/EllipsisTooltip'

const headers = [
  {
    id: 'lattice_name',
    getter: 'lattice.name',
    label: 'Title',
    sortable: true,
  },
  {
    id: 'runtime',
    getter: 'runtime',
    label: 'Runtime',
    sortable: true,
  },
  {
    id: 'total_electrons',
    getter: 'nodes',
    label: 'Nodes',
    sortable: true,
  },
]

const ResultsTableHead = ({ order, orderBy, onSort }) => {
  return (
    <TableHead>
      <TableRow>
        {_.map(headers, (header) => {
          return (
            <TableCell
              key={header.id}
              sx={(theme) => ({
                borderColor:
                  theme.palette.background.coveBlack03 + '!important',
              })}
            >
              {header.sortable ? (
                <TableSortLabel
                  active={orderBy === header.id}
                  direction={orderBy === header.id ? order : 'asc'}
                  onClick={() => onSort(header.id)}
                  sx={{
                    '.Mui-active': {
                      color: (theme) => theme.palette.text.secondary,
                    },
                  }}
                >
                  {header.label}
                </TableSortLabel>
              ) : (
                header.label
              )}
            </TableCell>
          )
        })}
      </TableRow>
    </TableHead>
  )
}

const StyledTable = styled(Table)(({ theme }) => ({
  // customize text
  [` & .${tableCellClasses.head}`]: {
    fontSize: '0.75rem',
  },
  [`& .${tableBodyClasses.root} .${tableRowClasses.root} `]: {
    fontSize: '0.875rem',
    padding: '0px',
  },

  // subdue header text
  [`& .${tableCellClasses.head}, & .${tableSortLabelClasses.active}`]: {
    color: theme.palette.text.tertiary,
    borderColor: theme.palette.background.default,
  },

  [`& .${tableBodyClasses.root} .${tableRowClasses.root}:hover`]: {
    backgroundColor: theme.palette.background.paper,
    cursor: 'pointer',

    [`& .${tableCellClasses.root}`]: {
      borderColor: theme.palette.background.default,
      color: theme.palette.text.secondary,
    },
    [`& .${linkClasses.root}`]: {
      color: theme.palette.text.secondary,
    },
  },

  // customize selected
  [`& .${tableBodyClasses.root} .${tableRowClasses.root}.Mui-selected`]: {
    backgroundColor: theme.palette.background.coveBlack02,
  },
  [`& .${tableBodyClasses.root} .${tableRowClasses.root}.Mui-selected:hover`]: {
    backgroundColor: theme.palette.background.coveBlack01,
  },

  [`& .${tableCellClasses.root}`]: {
    borderColor: theme.palette.background.default,
  },

  [`& .${tableCellClasses.root}:first-of-type`]: {
    borderTopLeftRadius: 8,
    borderBottomLeftRadius: 8,
  },
  [`& .${tableCellClasses.root}:last-of-type`]: {
    borderTopRightRadius: 8,
    borderBottomRightRadius: 8,
  },
}))

const SublatticesListing = () => {
  const { dispatchId } = useParams()
  const dispatch = useDispatch()
  const [sortColumn, setSortColumn] = useState('total_electrons')
  const [sortOrder, setSortOrder] = useState('desc')

  const sublatticesId = useSelector(
    (state) => state.latticeResults.sublatticesId
  )
  const sublatticesListView = useSelector(
    (state) => state.latticeResults.sublatticesList
  )?.map((e) => {
    return {
      dispatchId: e.dispatch_id,
      endTime: e.ended_at,
      latticeName: e.lattice_name,
      resultsDir: e.results_dir,
      status: e.status,
      error: e.error,
      runTime: e.runtime,
      startTime: e.started_at,
      totalElectrons: e.total_electrons,
      totalElectronsCompleted: e.total_electrons_completed,
    }
  })
  // get total records form dispatches api for pagination
  const isFetching = useSelector(
    (state) => state.latticeResults.sublatticesListResults.isFetching
  )

  // check if socket message is received and call API
  const callSocketApi = useSelector((state) => state.common.callSocketApi)
  const sublatticesListApi = () => {
    const bodyParams = {
      sort_by: sortColumn,
      direction: sortOrder,
      dispatchId,
    }
    dispatch(sublatticesListDetails(bodyParams))
  }

  useEffect(() => {
    sublatticesListApi()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sortColumn, sortOrder, callSocketApi])

  const handleChangeSort = (column) => {
    const isAsc = sortColumn === column && sortOrder === 'asc'
    setSortOrder(isAsc ? 'desc' : 'asc')
    setSortColumn(column)
  }

  const sublatticesDispatch = (sublatticeId) => {
    dispatch(sublatticesDispatchId(sublatticeId))
  }

  return (
    <>
      <Box>
        {sublatticesListView && (
          <>
            <TableContainer>
              <StyledTable>
                <ResultsTableHead
                  order={sortOrder}
                  orderBy={sortColumn}
                  onSort={handleChangeSort}
                />

                <TableBody
                  sx={{
                    '.MuiTableRow-root': {
                      borderBottom: '2 px solid red',
                    },
                  }}
                >
                  {sublatticesListView &&
                    sublatticesListView.map((result, index) => (
                      <Tooltip title="Click to view sublattices graph">
                        <TableRow
                          hover
                          key={result.dispatchId}
                          onClick={() => sublatticesDispatch(result)}
                          sx={{
                            borderRadius:
                              result.dispatchId === sublatticesId?.dispatchId
                                ? '16px'
                                : '',
                            border:
                              result.dispatchId === sublatticesId?.dispatchId
                                ? '2px solid #6473FF'
                                : '',
                            backgroundColor:
                              result.dispatchId === sublatticesId?.dispatchId
                                ? '#1C1C46'
                                : '',
                            color:
                              result.dispatchId === sublatticesId?.dispatchId
                                ? '#FFFFFF'
                                : '',
                          }}
                        >
                          <TableCell>
                            <Grid sx={{ display: 'flex', mt: 0.8, mb: 0 }}>
                              {' '}
                              {sublatticeIcon(result.status)}
                              <OverflowTip
                                width="70px"
                                fontSize="14px"
                                value={result.latticeName}
                              />
                            </Grid>
                          </TableCell>
                          <TableCell>
                            <Runtime
                              startTime={result.startTime}
                              endTime={result.endTime}
                            />
                          </TableCell>
                          <TableCell>
                            <OverflowTip
                              width="65px"
                              value={`${result.totalElectrons}/${result.totalElectronsCompleted}`}
                            />
                          </TableCell>
                        </TableRow>
                      </Tooltip>
                    ))}
                </TableBody>
              </StyledTable>
            </TableContainer>

            {_.isEmpty(sublatticesListView) && (
              <Typography
                sx={{
                  my: 3,
                  textAlign: 'center',
                  color: 'text.secondary',
                  fontSize: '0.825rem',
                }}
              >
                No results found.
              </Typography>
            )}
          </>
        )}
      </Box>

      {isFetching && _.isEmpty(sublatticesListView) && (
        <>
          {/*  */}
          {/* <Skeleton variant="rectangular" height={50} /> */}
          <TableContainer>
            <StyledTable>
              <TableBody>
                {[...Array(7)].map((_) => (
                  <TableRow key={Math.random()}>
                    <TableCell padding="checkbox">
                      <Skeleton sx={{ my: 2, mx: 1 }} />
                    </TableCell>
                    <TableCell sx={{ paddingTop: '6px !important' }}>
                      <Skeleton sx={{ my: 2, mx: 1 }} />
                    </TableCell>
                    <TableCell>
                      <Skeleton sx={{ my: 2, mx: 1 }} />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </StyledTable>
          </TableContainer>
        </>
      )}
    </>
  )
}

export default SublatticesListing
