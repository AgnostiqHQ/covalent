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
import { parseISO } from 'date-fns'
import {
  Table,
  Link,
  TableRow,
  TableHead,
  TableCell,
  TableBody,
  Typography,
  Paper,
  IconButton,
  Input,
  InputAdornment,
  TableContainer,
  TableSortLabel,
  Tooltip,
  Toolbar,
  Checkbox,
  Box,
  styled,
  tableCellClasses,
  tableRowClasses,
  tableBodyClasses,
  tableSortLabelClasses,
  TablePagination,
} from '@mui/material'
import {
  Clear as ClearIcon,
  Delete as DeleteIcon,
  Search as SearchIcon,
} from '@mui/icons-material'
import Fuse from 'fuse.js'
import { createSelector } from '@reduxjs/toolkit'

import { fetchResult, removeResult } from '../../redux/resultsSlice'
import CopyButton from '../CopyButton'
import { formatDate } from '../../utils/misc'
import Runtime from './Runtime'
import ResultProgress from './ResultProgress'

const selectResultsCache = (state) => state.results.cache
const selectQuery = (state, query) => query

const selectNormQuery = createSelector(selectQuery, (query) => _.trim(query))

const selectItems = createSelector(selectResultsCache, (cache) => _.map(cache))

const selectSearchIndex = createSelector(selectItems, (items) => {
  return new Fuse(items, {
    includeMatches: true,
    threshold: 0.4,
    ignoreLocation: true,
    keys: [
      { name: 'dispatch_id', weight: 1 },
      { name: 'lattice.name', weight: 1 },
    ],
  })
})

// search query is present
const selectSearchResults = createSelector(
  selectSearchIndex,
  selectNormQuery,
  (index, normQuery) => index.search(normQuery)
)

// search query is empty: emulate search results format
const selectResults = createSelector(selectItems, (items) =>
  _.map(items, (result) => ({
    item: result,
  }))
)

const headers = [
  {
    id: 'dispatchId',
    getter: 'dispatch_id',
    label: 'Dispatch ID',
  },
  {
    id: 'lattice',
    getter: 'lattice.name',
    label: 'Lattice',
    sortable: true,
  },
  // {
  //   id: 'resultsDir',
  //   getter: 'results_dir',
  //   label: 'Results directory',
  //   sortable: true,
  // },
  {
    id: 'runTime',
    label: 'Runtime',
  },
  {
    id: 'startTime',
    getter: 'start_time',
    label: 'Started',
    sortable: true,
  },
  {
    id: 'endTime',
    getter: 'end_time',
    label: 'Ended',
    sortable: true,
  },
  {
    id: 'status',
    getter: 'status',
    label: 'Status',
    sortable: true,
  },
]

const ResultsTableHead = ({
  order,
  orderBy,
  onSort,
  onSelectAllClick,
  numSelected,
  total,
}) => {
  return (
    <TableHead>
      <TableRow>
        <TableCell padding="checkbox">
          <Checkbox
            indeterminate={numSelected > 0 && numSelected < total}
            checked={numSelected > 0 && numSelected === total}
            onClick={onSelectAllClick}
          />
        </TableCell>

        {_.map(headers, (header) => {
          return (
            <TableCell key={header.id}>
              {header.sortable ? (
                <TableSortLabel
                  active={orderBy === header.id}
                  direction={orderBy === header.id ? order : 'asc'}
                  onClick={() => onSort(header.id)}
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

const ResultsTableToolbar = ({
  query,
  setQuery,
  numSelected,
  onDeleteSelected,
}) => {
  return (
    <Toolbar disableGutters sx={{ mb: 1 }}>
      {numSelected > 0 && (
        <Typography>
          {numSelected} selected
          <Tooltip title="Delete selected" placement="right">
            <IconButton onClick={onDeleteSelected}>
              <DeleteIcon />
            </IconButton>
          </Tooltip>
        </Typography>
      )}

      <Paper sx={{ ml: 'auto', px: 1, py: 0.5, maxWidth: 240 }}>
        <Input
          disableUnderline
          placeholder="Search"
          value={query}
          onChange={(event) => {
            setQuery(event.target.value)
          }}
          startAdornment={
            <InputAdornment position="start">
              <SearchIcon sx={{ color: 'text.secondary', fontSize: 16 }} />
            </InputAdornment>
          }
          endAdornment={
            <InputAdornment
              position="end"
              sx={{ visibility: !!query ? 'visible' : 'hidden' }}
            >
              <IconButton size="small" onClick={() => setQuery('')}>
                <ClearIcon
                  fontSize="inherit"
                  sx={{ color: 'text.secondary' }}
                />
              </IconButton>
            </InputAdornment>
          }
        />
      </Paper>
    </Toolbar>
  )
}

const StyledTable = styled(Table)(({ theme }) => ({
  // stripe every odd body row except on select and hover
  [`& .MuiTableBody-root .MuiTableRow-root:nth-of-type(odd):not(.Mui-selected):not(:hover)`]:
    {
      backgroundColor: theme.palette.background.paper,
    },

  // subdue header text
  [`& .${tableCellClasses.head}, & .${tableSortLabelClasses.active}`]: {
    color: theme.palette.text.secondary,
  },

  // copy btn on hover
  [`& .${tableBodyClasses.root} .${tableRowClasses.root}`]: {
    '& .copy-btn': { visibility: 'hidden' },
    '&:hover .copy-btn': { visibility: 'visible' },
  },

  // customize border
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

const ResultListing = () => {
  const dispatch = useDispatch()

  const [query, setQuery] = useState('')
  const [order, setOrder] = useState('desc')
  const [selected, setSelected] = useState([])
  const [orderBy, setOrderBy] = useState('startTime')
  const [page, setPage] = useState(0)
  const [rowsPerPage, setRowsPerPage] = useState(10)

  const runningResults = useSelector((state) =>
    _.filter(
      state.results.cache,
      (result) => _.get(result, 'status') === 'RUNNING'
    )
  )

  const results = useSelector((state) =>
    !selectNormQuery(state, query)
      ? selectResults(state)
      : selectSearchResults(state, query)
  )

  // refresh still-running results on first render
  useEffect(() => {
    _.each(runningResults, (result) => {
      dispatch(
        fetchResult({
          dispatchId: result.dispatch_id,
          resultsDir: result.results_dir,
        })
      )
    })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [dispatch])

  const getter = _.get(_.find(headers, { id: orderBy }), 'getter')
  const rows = _.chain(results)
    .orderBy(({ item }) => _.get(item, getter), order)
    .slice(page * rowsPerPage, (page + 1) * rowsPerPage)
    .value()

  const handleChangeSort = (headerId) => {
    const isAsc = orderBy === headerId && order === 'asc'
    setOrder(isAsc ? 'desc' : 'asc')
    setOrderBy(headerId)
  }
  const handleChangePage = (event, newPage) => {
    setPage(newPage)
  }
  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value))
    setPage(0)
  }
  const handleChangeSelection = (dispatchId) => {
    if (_.includes(selected, dispatchId)) {
      setSelected(_.without(selected, dispatchId))
    } else {
      setSelected(_.concat(selected, dispatchId))
    }
  }
  const handleDeleteSelected = () => {
    dispatch(removeResult(selected))
    // move to last page if necessary
    const lastPage =
      Math.ceil((_.size(results) - _.size(selected)) / rowsPerPage) - 1
    setPage(Math.min(page, lastPage))
    setSelected([])
  }

  const handleSelectAllClick = () => {
    if (_.size(selected) < _.size(results)) {
      setSelected(_.map(results, 'item.dispatch_id'))
    } else {
      setSelected([])
    }
  }

  return (
    <>
      <Box sx={{ mb: 3 }}>
        <ResultsTableToolbar
          query={query}
          setQuery={setQuery}
          numSelected={_.size(selected)}
          onDeleteSelected={handleDeleteSelected}
        />

        <TableContainer>
          <StyledTable>
            <ResultsTableHead
              order={order}
              orderBy={orderBy}
              numSelected={_.size(selected)}
              total={_.size(results)}
              onSort={handleChangeSort}
              onSelectAllClick={handleSelectAllClick}
            />

            <TableBody>
              {_.map(rows, ({ item: result }) => {
                const dispatchId = result.dispatch_id
                const isSelected = _.includes(selected, dispatchId)
                const startTime = parseISO(result.start_time)
                const endTime = parseISO(result.end_time)

                return (
                  <TableRow hover key={dispatchId} selected={isSelected}>
                    <TableCell padding="checkbox">
                      <Checkbox
                        checked={isSelected}
                        onClick={() => handleChangeSelection(dispatchId)}
                      />
                    </TableCell>

                    <TableCell>
                      <Link underline="none" href={`/${dispatchId}`}>
                        {dispatchId}
                      </Link>

                      <CopyButton
                        content={dispatchId}
                        size="small"
                        className="copy-btn"
                        title="Copy ID"
                      />
                    </TableCell>

                    <TableCell>{_.get(result, 'lattice.name')}</TableCell>

                    {/* <TableCell>
                      <Tooltip title={result.results_dir}>
                        <Box
                          component="span"
                          sx={{
                            color: 'text.secondary',
                            fontSize: 12,
                            fontFamily: 'monospace',
                          }}
                        >
                          {truncateMiddle(result.results_dir, 10, 16)}
                        </Box>
                      </Tooltip>
                      <CopyButton
                        content={result.results_dir}
                        size="small"
                        className="copy-btn"
                        title="Copy results directory"
                      />
                    </TableCell> */}

                    <TableCell>
                      <Runtime startTime={startTime} endTime={endTime} />
                    </TableCell>

                    <TableCell>{formatDate(startTime)}</TableCell>

                    <TableCell>{formatDate(endTime)}</TableCell>

                    <TableCell>
                      <ResultProgress dispatchId={dispatchId} />
                    </TableCell>
                  </TableRow>
                )
              })}
            </TableBody>
          </StyledTable>
        </TableContainer>

        {_.isEmpty(rows) && (
          <Typography
            sx={{
              my: 3,
              textAlign: 'center',
              color: 'text.secondary',
              fontSize: 'h6.fontSize',
            }}
          >
            No results found.
          </Typography>
        )}
        <TablePagination
          rowsPerPageOptions={[10, 15, 20]}
          component="div"
          count={_.size(results)}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </Box>
    </>
  )
}

export default ResultListing
