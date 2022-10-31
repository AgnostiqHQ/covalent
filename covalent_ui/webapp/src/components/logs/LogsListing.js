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
import {
  Table,
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
  Toolbar,
  Box,
  styled,
  tableCellClasses,
  tableRowClasses,
  tableBodyClasses,
  tableSortLabelClasses,
  linkClasses,
  Grid,
  Skeleton,
  Snackbar,
  SvgIcon,
  Pagination,
} from '@mui/material'
import { Clear as ClearIcon, Search as SearchIcon } from '@mui/icons-material'
import ReactTooltip from 'react-tooltip'
import { useDebounce } from 'use-debounce'
import {
  fetchLogsList,
  downloadCovalentLogFile,
  resetLogs,
} from '../../redux/logsSlice'
import DownloadButton from '../common/DownloadButton'
import { ReactComponent as closeIcon } from '../../assets/close.svg'
import {
  logStatusIcon,
  logStatusLabel,
  formatLogDate,
  formatLogTime,
  statusColor,
} from '../../utils/misc'
import copy from 'copy-to-clipboard'

const headers = [
  {
    id: 'log_date',
    getter: 'log_date',
    label: 'Time',
    sortable: true,
  },
  {
    id: 'status',
    getter: 'status',
    label: 'Status',
    sortable: true,
  },
  {
    id: 'log',
    getter: 'log',
    label: 'Log',
  },
]

const ResultsTableToolbar = ({ query, onSearch, setQuery }) => {
  return (
    <Toolbar disableGutters sx={{ mb: 1, width: '260px', height: '32px' }}>
      <Input
        fullWidth
        sx={{
          px: 1,
          py: 0.5,
          height: '32px',
          border: '1px solid #303067',
          borderRadius: '60px',
        }}
        disableUnderline
        placeholder="Search in logs"
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

const ResultsTableHead = ({
  order,
  orderBy,
  onSort,
  logListView,
  onDownload,
  disableDownload,
}) => {
  return (
    <TableHead sx={{ position: 'sticky', zIndex: 19 }}>
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
        {!_.isEmpty(logListView) && (
          <TableCell align="right">
            <DownloadButton
              data-testid="downloadButton"
              size="small"
              title="Download log"
              isBorderPresent
              onClick={onDownload}
              disabled={disableDownload}
            />
          </TableCell>
        )}
      </TableRow>
    </TableHead>
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
    backgroundColor: theme.palette.background.default,
  },

  // copy btn on hover
  [`& .${tableBodyClasses.root} .${tableRowClasses.root}`]: {
    '& .copy-btn': { visibility: 'hidden' },
    '&:hover .copy-btn': { visibility: 'visible' },
  },

  // customize hover
  [`& .${tableBodyClasses.root} .${tableRowClasses.root}:hover`]: {
    backgroundColor: theme.palette.background.paper,

    [`& .${tableCellClasses.root}`]: {
      borderColor: theme.palette.background.default,
      paddingTop: 4,
      paddingBottom: 4,
    },
    [`& .${linkClasses.root}`]: {
      color: theme.palette.text.secondary,
    },
  },

  [`& .${tableBodyClasses.root} .${tableRowClasses.root}`]: {
    backgroundColor: theme.palette.background.default,
    cursor: 'pointer',

    [`& .${tableCellClasses.root}`]: {
      borderColor: theme.palette.background.default,
      paddingTop: 4,
      paddingBottom: 4,
    },
    // [`& .${linkClasses.root}`]: {
    //   color: theme.palette.text.secondary,
    // },
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
    paddingTop: 4,
    paddingBottom: 4,
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

const LogsListing = () => {
  const dispatch = useDispatch()
  const [selected, setSelected] = useState([])
  const [searchKey, setSearchKey] = useState('')
  const [searchValue] = useDebounce(searchKey, 1000)
  const [sortColumn, setSortColumn] = useState('log_date')
  const [sortOrder, setSortOrder] = useState('desc')
  const [offset, setOffset] = useState(0)
  const [page, setPage] = useState(1)
  const logFinalFile = useSelector((state) => state.logs.logFile)
  const [openSnackbar, setOpenSnackbar] = useState(false)
  const [snackbarMessage, setSnackbarMessage] = useState(null)
  const [disableDownload, setDisableDownload] = useState(false)
  const [copied, setCopied] = useState(false)
  // reset store values to initial state when moved to another page
  useEffect(() => {
    return () => {
      dispatch(resetLogs())
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sortColumn, sortOrder, searchValue, page])

  useEffect(() => {
    if (logFinalFile) {
      const link = document.createElement('a')
      const blob = new Blob([logFinalFile])
      const url = URL.createObjectURL(blob)
      link.setAttribute('href', url)
      link.setAttribute('download', 'covalent_ui.log')
      link.style.visibility = 'hidden'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      dispatch(resetLogs())
      setDisableDownload(false)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [logFinalFile])

  const downloadLogFile = () => {
    setDisableDownload(true)
    dispatch(downloadCovalentLogFile()).then((action) => {
      if (action.type === downloadCovalentLogFile.rejected.type) {
        setOpenSnackbar(true)
        setSnackbarMessage(
          'Something went wrong and could not download the file!'
        )
        setDisableDownload(false)
      }
    })
  }

  const logListView = useSelector((state) => state.logs.logList)?.map((e) => {
    return {
      logDate: e.log_date,
      status: e.status,
      message: e.message,
    }
  })

  const totalRecords = useSelector((state) => state.logs.totalLogs)

  const isFetching = useSelector((state) => state.logs.fetchLogList.isFetching)

  const logListAPI = () => {
    const bodyParams = {
      count: 70,
      offset,
      sort_by: sortColumn,
      search: searchKey,
      direction: sortOrder,
    }
    if (searchValue?.length === 0 || searchValue?.length >= 3) {
      dispatch(fetchLogsList(bodyParams))
    }
  }

  const handlePageChanges = (event, pageValue) => {
    setPage(pageValue)
    setSelected([])
    const offsetValue = pageValue === 1 ? 0 : pageValue * 70 - 70
    setOffset(offsetValue)
  }

  useEffect(() => {
    if (offset === 0) setPage(1)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [offset])

  const onSearch = (e) => {
    setSearchKey(e.target.value)
    if (e.target.value.length > 3) {
      setSelected([])
      setOffset(0)
    }
  }

  useEffect(() => {
    logListAPI()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sortColumn, sortOrder, searchValue, page])

  const handleChangeSort = (column) => {
    setSelected([])
    setOffset(0)
    const isAsc = sortColumn === column && sortOrder === 'asc'
    setSortOrder(isAsc ? 'desc' : 'asc')
    setSortColumn(column)
  }
  return (
    <>
      <Box data-testid="logsTable">
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
        <ResultsTableToolbar
          totalRecords={totalRecords}
          query={searchKey}
          onSearch={onSearch}
          setQuery={setSearchKey}
        />
        {logListView && (
          <Grid>
            <TableContainer
              sx={{
                height: _.isEmpty(logListView) ? 50 : '61vh',
                '@media (min-width: 1700px)': {
                  height: _.isEmpty(logListView) ? 50 : '66vh',
                },
                '@media (min-height: 900px)': {
                  height: _.isEmpty(logListView) ? 50 : '72vh',
                },
                width: _.isEmpty(logListView) ? '40%' : null,

                borderRadius:
                  _.isEmpty(logListView) && !isFetching ? '0px' : '8px',
              }}
            >
              <StyledTable stickyHeader>
                <ResultsTableHead
                  totalRecords={totalRecords}
                  order={sortOrder}
                  orderBy={sortColumn}
                  numSelected={_.size(selected)}
                  total={_.size(logListView)}
                  onSort={handleChangeSort}
                  logListView={logListView}
                  onDownload={downloadLogFile}
                  disableDownload={disableDownload}
                />

                <TableBody>
                  {logListView &&
                    logListView.map((result, index) => (
                      <>
                        <TableRow
                          data-tip
                          data-for="logRow"
                          onClick={() => {
                            copy(result.message)
                            setCopied(true)
                            setTimeout(() => setCopied(false), 300)
                          }}
                          hover
                          key={index}
                        >
                          <TableCell
                            sx={{
                              width: 180,
                              verticalAlign: 'top',
                              fontFamily: (theme) => theme.typography.logsFont,
                            }}
                          >
                            <Grid
                              sx={{
                                fontSize: '12px',
                              }}
                            >
                              {formatLogTime(result.logDate)}
                            </Grid>
                            <Grid
                              sx={{
                                color: (theme) => theme.palette.text.tertiary,
                                fontSize: '10px',
                              }}
                            >
                              {formatLogDate(result.logDate)}
                            </Grid>
                          </TableCell>
                          <TableCell
                            style={{ width: 180, verticalAlign: 'top' }}
                          >
                            <Box
                              sx={{
                                display: 'flex',
                                alignItems: 'top',
                                fontSize: '14px',
                                color: statusColor(result.status),
                              }}
                            >
                              {logStatusIcon(result.status)}
                              &nbsp;
                              {logStatusLabel(result.status)}
                            </Box>
                          </TableCell>

                          <TableCell
                            colSpan={2}
                            sx={{
                              verticalAlign: 'top',
                              color: (theme) => theme.palette.primary.white,
                              whiteSpace: 'pre-wrap',
                            }}
                          >
                            <Typography
                              sx={{
                                fontSize: '12px',
                                fontFamily: (theme) =>
                                  theme.typography.logsFont,
                              }}
                            >
                              {result.message}
                            </Typography>
                          </TableCell>
                        </TableRow>
                        <ReactTooltip
                          id="logRow"
                          place="top"
                          effect="float"
                          arrowColor="#1C1C46"
                          backgroundColor="#1C1C46"
                          delayShow={300}
                        >
                          {!copied ? 'Click to copy log message' : 'Copied'}
                        </ReactTooltip>
                      </>
                    ))}
                </TableBody>
              </StyledTable>
            </TableContainer>

            {_.isEmpty(logListView) && !isFetching && (
              <Typography
                sx={{
                  textAlign: 'center',
                  color: 'text.secondary',
                  fontSize: 'h6.fontSize',
                  paddingTop: 4,
                  paddingBottom: 2,
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
              {!_.isEmpty(logListView) && (
                <Pagination
                  color="primary"
                  shape="rounded"
                  variant="outlined"
                  count={
                    totalRecords && totalRecords > 70
                      ? Math.ceil(totalRecords / 70)
                      : 1
                  }
                  disabled={totalRecords <= 70}
                  page={page}
                  onChange={handlePageChanges}
                  showFirstButton
                  showLastButton
                  siblingCount={2}
                  boundaryCount={2}
                />
              )}
            </Grid>
          </Grid>
        )}
      </Box>

      {isFetching && _.isEmpty(logListView) && (
        <>
          {/*  */}
          {/* <Skeleton variant="rectangular" height={50} /> */}
          <TableContainer sx={{ width: '99.5%' }}>
            <StyledTable>
              <TableBody>
                {[...Array(7)].map(() => (
                  <TableRow key={Math.random()}>
                    <TableCell sx={{ width: '13%' }}>
                      <Skeleton sx={{ my: 2 }} />
                    </TableCell>
                    <TableCell sx={{ width: '13%' }}>
                      <Skeleton sx={{ my: 2 }} />
                    </TableCell>
                    <TableCell>
                      <Skeleton sx={{ my: 2 }} />
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

export default LogsListing
