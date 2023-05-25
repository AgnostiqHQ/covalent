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
import { statusColor, statusIcon } from '../../utils/misc'
import copy from 'copy-to-clipboard'
import { ReactComponent as FilterSvg } from '../../assets/qelectron/filter.svg'
import CopyButton from '../common/CopyButton'
import useMediaQuery from '@mui/material/useMediaQuery'

const headers = [
  {
    id: 'job_id',
    getter: 'job_id',
    label: 'Job Id / Status',
    sortable: true,
  },
  {
    id: 'start_time',
    getter: 'start_time',
    label: 'Start Time',
    sortable: true,
  },
  {
    id: 'executor',
    getter: 'executor',
    label: 'Executor',
    sortable: true,
  },
]

// const ResultsTableToolbar = ({ query, onSearch, setQuery }) => {
//   return (
//     <Toolbar disableGutters sx={{ mb: 1, width: '260px', height: '32px' }}>
//       <Input
//         fullWidth
//         sx={{
//           px: 1,
//           py: 0.5,
//           height: '32px',
//           border: '1px solid #303067',
//           borderRadius: '60px',
//         }}
//         disableUnderline
//         placeholder="Search in logs"
//         value={query}
//         onChange={(e) => onSearch(e)}
//         startAdornment={
//           <InputAdornment position="start">
//             <SearchIcon sx={{ color: 'text.secondary', fontSize: 16 }} />
//           </InputAdornment>
//         }
//         endAdornment={
//           <InputAdornment
//             position="end"
//             sx={{ visibility: !!query ? 'visible' : 'hidden' }}
//           >
//             <IconButton
//               size="small"
//               onClick={() => setQuery('')}
//               data-testid="clear"
//             >
//               <ClearIcon fontSize="inherit" sx={{ color: 'text.secondary' }} />
//             </IconButton>
//           </InputAdornment>
//         }
//       />
//     </Toolbar>
//   )
// }

const ResultsTableHead = ({ order, orderBy, onSort }) => {
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
                  data-testid="tableHeader"
                  active={orderBy === header.id}
                  direction={orderBy === header.id ? order : 'asc'}
                  onClick={() => onSort(header.id)}
                  sx={{
                    fontSize: '12px',
                    width: '100%',
                    mr: header.id === 'job_id' ? 20 : null,
                    '.Mui-active': {
                      color: (theme) => theme.palette.text.secondary,
                    },
                  }}
                >
                  {header.id === 'job_id' && (
                    <span style={{ flex: 'none' }}>
                      <SvgIcon
                        aria-label="view"
                        sx={{
                          display: 'flex',
                          justifyContent: 'flex-end',
                          mr: 0,
                          mt: 0.8,
                          pr: 0,
                        }}
                      >
                        <FilterSvg />
                      </SvgIcon>
                    </span>
                  )}
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
    backgroundColor: theme.palette.background.paper,
  },

  // copy btn on hover
  [`& .${tableBodyClasses.root} .${tableRowClasses.root}`]: {
    '& .copy-btn': { visibility: 'hidden' },
    '&:hover .copy-btn': { visibility: 'visible' },
  },

  // customize hover
  [`& .${tableBodyClasses.root} .${tableRowClasses.root}:hover`]: {
    backgroundColor: theme.palette.background.default,

    [`& .${tableCellClasses.root}`]: {
      borderColor: theme.palette.background.paper,
      paddingTop: 4,
      paddingBottom: 4,
    },
    [`& .${linkClasses.root}`]: {
      color: theme.palette.text.secondary,
    },
  },

  [`& .${tableBodyClasses.root} .${tableRowClasses.root}`]: {
    backgroundColor: theme.palette.background.paper,
    cursor: 'pointer',

    [`& .${tableCellClasses.root}`]: {
      borderColor: theme.palette.background.paper,
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
    borderColor: theme.palette.background.paper,
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

const QElectronList = ({ expanded }) => {
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

  const xlmatches = useMediaQuery('(min-height:850px)')
  const xxlmatches = useMediaQuery('(min-height:940px)')
  const slmatches = useMediaQuery('(min-height:1060px)')
  

  const data = [
    {
      job_id: '123yrhe383u2h8ssdfsd...',
      start_time: '03 Feb, 12:05:38 ',
      executor: 'IBM Quantum',
      status: 'RUNNING',
    },
    {
      job_id: '123yrhe383u2h8ssdfsd...',
      start_time: '03 Feb, 12:05:38 ',
      executor: 'IBM Quantum',
      status: 'RUNNING',
    },
    {
      job_id: '123yrhe383u2h8ssdfsd...',
      start_time: '03 Feb, 12:05:38 ',
      executor: 'IBM Quantum',
      status: 'RUNNING',
    },
    {
      job_id: '123yrhe383u2h8ssdfsd...',
      start_time: '03 Feb, 12:05:38 ',
      executor: 'IBM Quantum',
      status: 'RUNNING',
    },
    {
      job_id: '123yrhe383u2h8ssdfsd...',
      start_time: '03 Feb, 12:05:38 ',
      executor: 'IBM Quantum',
      status: 'RUNNING',
    },
    {
      job_id: '123yrhe383u2h8ssdfsd...',
      start_time: '03 Feb, 12:05:38 ',
      executor: 'IBM Quantum',
      status: 'RUNNING',
    },
    {
      job_id: '123yrhe383u2h8ssdfsd...',
      start_time: '03 Feb, 12:05:38 ',
      executor: 'IBM Quantum',
      status: 'RUNNING',
    },
    {
      job_id: '123yrhe383u2h8ssdfsd...',
      start_time: '03 Feb, 12:05:38 ',
      executor: 'IBM Quantum',
      status: 'RUNNING',
    },
    {
      job_id: '123yrhe383u2h8ssdfsd...',
      start_time: '03 Feb, 12:05:38 ',
      executor: 'IBM Quantum',
      status: 'RUNNING',
    },
    {
      job_id: '123yrhe383u2h8ssdfsd...',
      start_time: '03 Feb, 12:05:38 ',
      executor: 'IBM Quantum',
      status: 'RUNNING',
    },
    {
      job_id: '123yrhe383u2h8ssdfsd...',
      start_time: '03 Feb, 12:05:38 ',
      executor: 'IBM Quantum',
      status: 'RUNNING',
    },
    {
      job_id: '123yrhe383u2h8ssdfsd...',
      start_time: '03 Feb, 12:05:38 ',
      executor: 'IBM Quantum',
      status: 'RUNNING',
    },
    {
      job_id: '123yrhe383u2h8ssdfsd...',
      start_time: '03 Feb, 12:05:38 ',
      executor: 'IBM Quantum',
      status: 'RUNNING',
    },
    {
      job_id: '123yrhe383u2h8ssdfsd...',
      start_time: '03 Feb, 12:05:38 ',
      executor: 'IBM Quantum',
      status: 'RUNNING',
    },
    {
      job_id: '123yrhe383u2h8ssdfsd...',
      start_time: '03 Feb, 12:05:38 ',
      executor: 'IBM Quantum',
      status: 'RUNNING',
    },
    {
      job_id: '123yrhe383u2h8ssdfsd...',
      start_time: '03 Feb, 12:05:38 ',
      executor: 'IBM Quantum',
      status: 'RUNNING',
    },
    {
      job_id: '123yrhe383u2h8ssdfsd...',
      start_time: '03 Feb, 12:05:38 ',
      executor: 'IBM Quantum',
      status: 'RUNNING',
    },
    {
      job_id: '123yrhe383u2h8ssdfsd...',
      start_time: '03 Feb, 12:05:38 ',
      executor: 'IBM Quantum',
      status: 'RUNNING',
    },
    {
      job_id: '123yrhe383u2h8ssdfsd...',
      start_time: '03 Feb, 12:05:38 ',
      executor: 'IBM Quantum',
      status: 'RUNNING',
    },
    {
      job_id: '123yrhe383u2h8ssdfsd...',
      start_time: '03 Feb, 12:05:38 ',
      executor: 'IBM Quantum',
      status: 'RUNNING',
    },
    {
      job_id: '123yrhe383u2h8ssdfsd...',
      start_time: '03 Feb, 12:05:38 ',
      executor: 'IBM Quantum',
      status: 'RUNNING',
    },
    {
      job_id: '123yrhe383u2h8ssdfsd...',
      start_time: '03 Feb, 12:05:38 ',
      executor: 'IBM Quantum',
      status: 'RUNNING',
    },
    {
      job_id: '123yrhe383u2h8ssdfsd...',
      start_time: '03 Feb, 12:05:38 ',
      executor: 'IBM Quantum',
      status: 'RUNNING',
    },
    {
      job_id: '123yrhe383u2h8ssdfsd...',
      start_time: '03 Feb, 12:05:38 ',
      executor: 'IBM Quantum',
      status: 'RUNNING',
    },
    {
      job_id: '123yrhe383u2h8ssdfsd...',
      start_time: '03 Feb, 12:05:38 ',
      executor: 'IBM Quantum',
      status: 'RUNNING',
    },
    {
      job_id: '123yrhe383u2h8ssdfsd...',
      start_time: '03 Feb, 12:05:38 ',
      executor: 'IBM Quantum',
      status: 'RUNNING',
    },
  ]
  //   // reset store values to initial state when moved to another page
  //   useEffect(() => {
  //     return () => {
  //       dispatch(resetLogs())
  //     }
  //     // eslint-disable-next-line react-hooks/exhaustive-deps
  //   }, [sortColumn, sortOrder, searchValue, page])

  //   useEffect(() => {
  //     if (logFinalFile) {
  //       const link = document.createElement('a')
  //       const blob = new Blob([logFinalFile])
  //       const url = URL.createObjectURL(blob)
  //       link.setAttribute('href', url)
  //       link.setAttribute('download', 'covalent_ui.log')
  //       link.style.visibility = 'hidden'
  //       document.body.appendChild(link)
  //       link.click()
  //       document.body.removeChild(link)
  //       dispatch(resetLogs())
  //       setDisableDownload(false)
  //     }
  //     // eslint-disable-next-line react-hooks/exhaustive-deps
  //   }, [logFinalFile])

  //   const downloadLogFile = () => {
  //     setDisableDownload(true)
  //     dispatch(downloadCovalentLogFile()).then((action) => {
  //       if (action.type === downloadCovalentLogFile.rejected.type) {
  //         setOpenSnackbar(true)
  //         setSnackbarMessage(
  //           'Something went wrong and could not download the file!'
  //         )
  //         setDisableDownload(false)
  //       }
  //     })
  //   }

  //   const logListView = useSelector((state) => state.logs.logList)?.map((e) => {
  //     return {
  //       logDate: e.log_date,
  //       status: e.status,
  //       message: e.message,
  //     }
  //   })

  //   const totalRecords = useSelector((state) => state.logs.totalLogs)

  //   const isFetching = useSelector((state) => state.logs.fetchLogList.isFetching)

  //   const logListAPI = () => {
  //     const bodyParams = {
  //       count: 70,
  //       offset,
  //       sort_by: sortColumn,
  //       search: searchKey,
  //       direction: sortOrder,
  //     }
  //     if (searchValue?.length === 0 || searchValue?.length >= 3) {
  //       dispatch(fetchLogsList(bodyParams))
  //     }
  //   }

  //   const handlePageChanges = (event, pageValue) => {
  //     setPage(pageValue)
  //     setSelected([])
  //     const offsetValue = pageValue === 1 ? 0 : pageValue * 70 - 70
  //     setOffset(offsetValue)
  //   }

  //   useEffect(() => {
  //     if (offset === 0) setPage(1)
  //     // eslint-disable-next-line react-hooks/exhaustive-deps
  //   }, [offset])

  //   const onSearch = (e) => {
  //     setSearchKey(e.target.value)
  //     if (e.target.value.length > 3) {
  //       setSelected([])
  //       setOffset(0)
  //     }
  //   }

  //   useEffect(() => {
  //     logListAPI()
  //     // eslint-disable-next-line react-hooks/exhaustive-deps
  //   }, [sortColumn, sortOrder, searchValue, page])

  const handleChangeSort = (column) => {
    setSelected([])
    setOffset(0)
    const isAsc = sortColumn === column && sortOrder === 'asc'
    setSortOrder(isAsc ? 'desc' : 'asc')
    setSortColumn(column)
  }

  const getHeight = () => {
    if (xlmatches) {
      return expanded ? '23rem' : '40rem'
    } else if (xxlmatches) {
      return expanded ? '63rem' : '40rem'
    } else if (slmatches) {
      return expanded ? '24rem' : '48rem'
    } else {
      return expanded ? '16rem' : '32rem'
    }
  }

  return (
    <Grid mt={3} px={2} sx={{ height: getHeight(), overflow: 'auto' }}>
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
        {/* <ResultsTableToolbar
        //   totalRecords={totalRecords}
          query={searchKey}
          onSearch={onSearch}
          setQuery={setSearchKey}
        /> */}

        {data && (
          <Grid>
            <TableContainer
              sx={{
                width: _.isEmpty(data) ? '40%' : null,
                borderRadius: _.isEmpty(data) && !data ? '0px' : '8px',
              }}
            >
              <StyledTable stickyHeader>
                <ResultsTableHead
                  //   totalRecords={totalRecords}
                  order={sortOrder}
                  orderBy={sortColumn}
                  numSelected={_.size(selected)}
                  total={_.size(data)}
                  onSort={handleChangeSort}
                />

                <TableBody>
                  {data &&
                    data.map((result, index) => (
                      <>
                        <TableRow
                          sx={{ height: '2.5rem' }}
                          data-testid="copyMessage"
                          data-tip
                          data-for="logRow"
                          onClick={() => {
                            copy(result.job_id)
                            setCopied(true)
                            setTimeout(() => setCopied(false), 300)
                          }}
                          hover
                          key={index}
                        >
                          <TableCell
                            sx={{
                              fontFamily: (theme) => theme.typography.logsFont,
                            }}
                          >
                            <Grid
                              sx={{
                                fontSize: '14px',
                                display: 'flex',
                                alignItems: 'center',
                              }}
                            >
                              {statusIcon(result.status)}
                              {result.job_id}
                              <CopyButton isBorderPresent />
                            </Grid>
                          </TableCell>
                          <TableCell>
                            <Box
                              sx={{
                                display: 'flex',
                                fontSize: '14px',
                              }}
                            >
                              {result.start_time}
                            </Box>
                          </TableCell>
                          <TableCell>
                            <Box
                              sx={{
                                display: 'flex',
                                fontSize: '14px',
                              }}
                            >
                              {result.executor}
                            </Box>
                          </TableCell>
                        </TableRow>
                        {/* <ReactTooltip
                          id="logRow"
                          place="top"
                          effect="float"
                          arrowColor="#1C1C46"
                          backgroundColor="#1C1C46"
                          delayShow={300}
                        >
                          {!copied ? 'Click to copy log message' : 'Copied'}
                        </ReactTooltip> */}
                      </>
                    ))}
                </TableBody>
              </StyledTable>
            </TableContainer>

            {_.isEmpty(data) && (
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
          </Grid>
        )}
      </Box>
    </Grid>
  )
}

export default QElectronList
