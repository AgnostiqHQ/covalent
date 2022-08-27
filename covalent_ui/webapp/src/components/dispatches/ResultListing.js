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
import { useDebounce } from 'use-debounce'
import {
  Table,
  Link,
  TableRow,
  TableHead,
  TableCell,
  TableBody,
  Typography,
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
  Pagination,
  linkClasses,
  Grid,
  Skeleton,
  Snackbar,
  SvgIcon,
} from '@mui/material'
import { Clear as ClearIcon, Search as SearchIcon } from '@mui/icons-material'
import {
  fetchDashboardList,
  deleteDispatches,
  dispatchesDeleted,
} from '../../redux/dashboardSlice'
import CopyButton from '../common/CopyButton'
import { formatDate, secondsToHms } from '../../utils/misc'
import ResultProgress from './ResultProgress'
import SortDispatch from './SortDispatch'
import DialogBox from '../common/DialogBox'
import { ReactComponent as DeleteNewIcon } from '../../assets/delete.svg'
import { ReactComponent as closeIcon } from '../../assets/close.svg'
import Runtime from './Runtime'
import OverflowTip from '../common/EllipsisTooltip'

const headers = [
  {
    id: 'dispatchId',
    getter: 'dispatch_id',
    label: 'Dispatch ID',
  },
  {
    id: 'lattice_name',
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
    id: 'runtime',
    getter: 'runtime',
    label: 'Runtime',
    sortable: true,
  },
  {
    id: 'started_at',
    getter: 'start_time',
    label: 'Started',
    sortable: true,
  },
  {
    id: 'ended_at',
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
        <TableCell
          padding="checkbox"
          sx={(theme) => ({
            borderColor: theme.palette.background.coveBlack03 + '!important',
          })}
        >
          <Checkbox
            disableRipple
            indeterminate={numSelected > 0 && numSelected < total}
            checked={numSelected > 0 && numSelected === total}
            onClick={onSelectAllClick}
            size="small"
            sx={(theme) => ({
              color: theme.palette.text.tertiary,
            })}
          />
        </TableCell>

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
  onSearch,
  setQuery,
  numSelected,
  onDeleteSelected,
  runningDispatches,
  completedDispatches,
  failedDispatches,
  allDispatches,
  openDialogBox,
  setOpenDialogBox,
  dashboardOverviewFetching,
}) => {
  return (
    <Toolbar disableGutters sx={{ mb: 1 }}>
      {numSelected > 0 && (
        <Typography
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          {numSelected} selected
          <Tooltip
            title="Delete selected"
            placement="right"
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <IconButton
              onClick={() => setOpenDialogBox(true)}
              mt={2}
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <DeleteNewIcon
                style={{ margin: 'auto', width: '25px', height: '25px' }}
              />
            </IconButton>
          </Tooltip>
        </Typography>
      )}
      <DialogBox
        openDialogBox={openDialogBox}
        setOpenDialogBox={setOpenDialogBox}
        title="Delete"
        handler={onDeleteSelected}
        totalItems={numSelected}
        message="Are you sure about deleting"
        icon={DeleteNewIcon}
      />
      <Grid
        ml={2}
        container
        direction="row"
        justifyContent="space-between"
        alignItems="center"
        sx={{ width: '35%' }}
      >
        <SortDispatch
          title="All"
          count={allDispatches}
          isFetching={!dashboardOverviewFetching}
        />
        <SortDispatch
          title="Running"
          count={runningDispatches}
          isFetching={!dashboardOverviewFetching}
        />
        <SortDispatch
          title="Completed"
          count={completedDispatches}
          isFetching={!dashboardOverviewFetching}
        />
        <SortDispatch
          title="Failed"
          count={failedDispatches}
          isFetching={!dashboardOverviewFetching}
        />
      </Grid>
      <Input
        sx={{
          ml: 'auto',
          px: 1,
          py: 0.5,
          maxWidth: 260,
          height: '32px',
          border: '1px solid #303067',
          borderRadius: '60px',
        }}
        disableUnderline
        placeholder="Search"
        value={query}
        onChange={(e) => onSearch(e)}
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
              <ClearIcon fontSize="inherit" sx={{ color: 'text.secondary' }} />
            </IconButton>
          </InputAdornment>
        }
      />
    </Toolbar>
  )
}

const StyledTable = styled(Table)(({ theme }) => ({
  // stripe every odd body row except on select and hover
  // [`& .MuiTableBody-root .MuiTableRow-root:nth-of-type(odd):not(.Mui-selected):not(:hover)`]:
  //   {
  //     backgroundColor: theme.palette.background.paper,
  //   },

  // customize text
  [`& .${tableBodyClasses.root} .${tableCellClasses.root}, & .${tableCellClasses.head}`]:
  {
    fontSize: '1rem',
  },

  // subdue header text
  [`& .${tableCellClasses.head}, & .${tableSortLabelClasses.active}`]: {
    color: theme.palette.text.tertiary,
  },

  // copy btn on hover
  [`& .${tableBodyClasses.root} .${tableRowClasses.root}`]: {
    '& .copy-btn': { visibility: 'hidden' },
    '&:hover .copy-btn': { visibility: 'visible' },
  },

  // customize hover
  [`& .${tableBodyClasses.root} .${tableRowClasses.root}:hover`]: {
    backgroundColor: theme.palette.background.paper,
    cursor: 'pointer',

    [`& .${tableCellClasses.root}`]: {
      borderColor: theme.palette.background.default,
      paddingTop: 2,
      paddingBottom: 2,
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

  // customize border
  [`& .${tableCellClasses.root}`]: {
    borderColor: theme.palette.background.default,
    paddingTop: 2,
    paddingBottom: 2,
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
  const [selected, setSelected] = useState([])
  const [page, setPage] = useState(1)
  const [searchKey, setSearchKey] = useState('')
  const [searchValue] = useDebounce(searchKey, 1000)
  const [sortColumn, setSortColumn] = useState('started_at')
  const [sortOrder, setSortOrder] = useState('desc')
  const [offset, setOffset] = useState(0)
  const [openDialogBox, setOpenDialogBox] = useState(false)
  const isError = useSelector(
    (state) => state.dashboard.fetchDashboardList.error
  )
  const [openSnackbar, setOpenSnackbar] = useState(Boolean(isError))
  const [snackbarMessage, setSnackbarMessage] = useState(null)

  //check if any dispatches are deleted and call the API
  const isDeleted = useSelector((state) => state.dashboard.dispatchesDeleted)

  const dashboardListView = useSelector(
    (state) => state.dashboard.dashboardList
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

  const dashboardOverviewFetching = useSelector(
    (state) => state.dashboard.dashboardOverview
  )

  const allDispatches = useSelector(
    (state) => state.dashboard.dashboardOverview.total_jobs
  )
  const runningDispatches = useSelector(
    (state) => state.dashboard.dashboardOverview.total_jobs_running
  )
  const completedDispatches = useSelector(
    (state) => state.dashboard.dashboardOverview.total_jobs_completed
  )
  const failedDispatches = useSelector(
    (state) => state.dashboard.dashboardOverview.total_jobs_failed
  )
  // get total records form dispatches api for pagination
  const totalRecords = useSelector((state) => state.dashboard.totalDispatches)

  const isFetching = useSelector(
    (state) => state.dashboard.fetchDashboardList.isFetching
  )

  // check if socket message is received and call API
  const callSocketApi = useSelector((state) => state.common.callSocketApi)
  const dashboardListAPI = () => {
    const bodyParams = {
      count: 10,
      offset,
      sort_by: sortColumn,
      search: searchKey,
      direction: sortOrder,
    }
    if (searchValue?.length === 0 || searchValue?.length >= 3) {
      dispatch(fetchDashboardList(bodyParams))
    }
  }

  const onSearch = (e) => {
    setSearchKey(e.target.value)
    if (e.target.value.length > 3) {
      setSelected([])
      setOffset(0)
    }
  }

  useEffect(() => {
    dashboardListAPI()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sortColumn, sortOrder, page, searchValue, isDeleted, callSocketApi])

  // check if there are any API errors and show a sncakbar
  useEffect(() => {
    if (isError) {
      setOpenSnackbar(true)
      setSnackbarMessage(
        'Something went wrong,please contact the administrator!'
      )
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isError])


  useEffect(() => {
    if (offset === 0) setPage(1)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [offset])

  const handlePageChanges = (event, pageValue) => {
    setPage(pageValue)
    setSelected([])
    const offsetValue = pageValue === 1 ? 0 : pageValue * 10 - 10
    setOffset(offsetValue)
  }

  const handleChangeSelection = (dispatchId) => {
    if (_.includes(selected, dispatchId)) {
      setSelected(_.without(selected, dispatchId))
    } else {
      setSelected(_.concat(selected, dispatchId))
    }
  }

  const handleChangeSort = (column) => {
    setSelected([])
    setPage(1)
    setOffset(0)
    const isAsc = sortColumn === column && sortOrder === 'asc'
    setSortOrder(isAsc ? 'desc' : 'asc')
    setSortColumn(column)
  }

  const handleSelectAllClick = () => {
    if (_.size(selected) < _.size(dashboardListView)) {
      setSelected(_.map(dashboardListView, 'dispatchId'))
    } else {
      setSelected([])
    }
  }

  const handleDeleteSelected = () => {
    dispatch(deleteDispatches({ dispatches: selected })).then((action) => {
      if (action.type === deleteDispatches.fulfilled.type) {
        setOpenSnackbar(true)
        setSnackbarMessage('Dispatches have been deleted successfully!')
        if (selected.length === dashboardListView.length) {
          setOffset(0)
        }
        setSelected([])
        setOpenDialogBox(false)
        dispatch(dispatchesDeleted())
      } else if (action.type === deleteDispatches.rejected.type) {
        setOpenSnackbar(true)
        setSnackbarMessage(
          'Something went wrong and could not delete dispatches!'
        )
        setOpenDialogBox(false)
      }
    })
  }

  return (
    <>
      <Snackbar
        open={openSnackbar}
        autoHideDuration={3000}
        message={snackbarMessage}
        onClose={() => setOpenSnackbar(false)}
        action={
          <SvgIcon
            sx={{
              mt: 2,
              zIndex: 2,
              cursor: 'pointer',
            }}
            component={closeIcon}
            onClick={() => setOpenSnackbar(false)}
          />
        }
      />
      <Box>
        <ResultsTableToolbar
          query={searchKey}
          totalRecords={totalRecords}
          onSearch={onSearch}
          setQuery={setSearchKey}
          numSelected={_.size(selected)}
          onDeleteSelected={handleDeleteSelected}
          allDispatches={allDispatches}
          runningDispatches={runningDispatches}
          completedDispatches={completedDispatches}
          failedDispatches={failedDispatches}
          openDialogBox={openDialogBox}
          setOpenDialogBox={setOpenDialogBox}
          dashboardOverviewFetching={dashboardOverviewFetching}
        />
        {dashboardListView && (
          <Grid>
            <TableContainer>
              <StyledTable>
                <ResultsTableHead
                  order={sortOrder}
                  orderBy={sortColumn}
                  numSelected={_.size(selected)}
                  total={_.size(dashboardListView)}
                  onSort={handleChangeSort}
                  onSelectAllClick={handleSelectAllClick}
                />

                <TableBody>
                  {dashboardListView &&
                    dashboardListView.map((result, index) => (
                      <TableRow hover key={result.dispatchId}>
                        <TableCell padding="checkbox">
                          <Checkbox
                            disableRipple
                            checked={_.includes(selected, result.dispatchId)}
                            onClick={() =>
                              handleChangeSelection(result.dispatchId)
                            }
                            size="small"
                            sx={(theme) => ({
                              color: theme.palette.text.tertiary,
                            })}
                          />
                        </TableCell>

                        <TableCell sx={{ paddingTop: '6px !important' }}>
                          <Link
                            underline="none"
                            href={`/${result.dispatchId}`}
                            sx={{ color: 'text.primary' }}
                          >
                            {result.dispatchId}
                          </Link>
                          <CopyButton
                            sx={{ ml: 1, color: 'text.tertiary' }}
                            content={result.dispatchId}
                            size="small"
                            className="copy-btn"
                            title="Copy ID"
                            isBorderPresent={true}
                          />
                        </TableCell>

                        <TableCell>
                          <OverflowTip value={result.latticeName} />
                        </TableCell>
                        {result.status === 'RUNNING' ? (
                          <TableCell>
                            <Runtime
                              startTime={result.startTime}
                              endTime={result.endTime}
                            />
                          </TableCell>
                        ) : (
                          <TableCell>{secondsToHms(result.runTime)}</TableCell>
                        )}

                        <TableCell>{formatDate(result.startTime)}</TableCell>

                        <TableCell>{formatDate(result.endTime)}</TableCell>

                        <TableCell>
                          <ResultProgress result={result} />
                        </TableCell>
                      </TableRow>
                    ))}
                </TableBody>
              </StyledTable>
            </TableContainer>

            {_.isEmpty(dashboardListView) && (
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
            <Grid
              container
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'flex-end',
                paddingTop: '10px',
              }}
            >
              <Pagination
                color="primary"
                shape="rounded"
                variant="outlined"
                count={
                  totalRecords && totalRecords > 10
                    ? Math.ceil(totalRecords / 10)
                    : 1
                }
                page={page}
                onChange={handlePageChanges}
                showFirstButton
                showLastButton
                siblingCount={2}
                boundaryCount={2}
              />
            </Grid>
          </Grid>
        )}
      </Box>

      {isFetching && _.isEmpty(dashboardListView) && (
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
                    <TableCell>
                      <Skeleton sx={{ my: 2, mx: 1 }} />
                    </TableCell>
                    <TableCell>
                      <Skeleton sx={{ my: 2, mx: 1 }} />
                    </TableCell>
                    <TableCell>
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

export default ResultListing
