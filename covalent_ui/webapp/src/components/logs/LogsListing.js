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
} from '@mui/material'
import { Clear as ClearIcon, Search as SearchIcon } from '@mui/icons-material'
import { useDebounce } from 'use-debounce'
import { fetchLogsList } from '../../redux/logsSlice'
import DownloadButton from '../common/DownloadButton'
import CopyButton from '../common/CopyButton'
import {
  logStatusIcon,
  logStatusLabel,
  formatLogDate,
  formatLogTime,
} from '../../utils/misc'

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

const ResultsTableHead = ({ order, orderBy, onSort, logListView }) => {
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

  const logListView = useSelector((state) => state.logs.logList)?.map((e) => {
    return {
      logDate: e.log_date,
      status: e.status,
      message: e.message,
    }
  })

  const isFetching = useSelector((state) => state.logs.fetchLogList.isFetching)

  const logListAPI = () => {
    const bodyParams = {
      offset,
      sort_by: sortColumn,
      search: searchKey,
      direction: sortOrder,
    }
    if (searchValue?.length === 0 || searchValue?.length >= 3) {
      dispatch(fetchLogsList(bodyParams))
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
    logListAPI()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sortColumn, sortOrder, searchValue])

  const handleChangeSort = (column) => {
    setSelected([])
    setOffset(0)
    const isAsc = sortColumn === column && sortOrder === 'asc'
    setSortOrder(isAsc ? 'desc' : 'asc')
    setSortColumn(column)
  }

  return (
    <>
      <Box>
        <ResultsTableToolbar
          query={searchKey}
          onSearch={onSearch}
          setQuery={setSearchKey}
        />
        {logListView && (
          <Grid>
            <TableContainer
              sx={{
                height: _.isEmpty(logListView) ? 50 : '62vh',
                '@media (min-width: 1700px)': {
                  height: _.isEmpty(logListView) ? 50 : '68vh',
                },
                width: _.isEmpty(logListView) ? '40%' : null,

                borderRadius:
                  _.isEmpty(logListView) && !isFetching ? '0px' : '8px',
              }}
            >
              <StyledTable stickyHeader>
                <ResultsTableHead
                  order={sortOrder}
                  orderBy={sortColumn}
                  numSelected={_.size(selected)}
                  total={_.size(logListView)}
                  onSort={handleChangeSort}
                  logListView={logListView}
                />

                <TableBody>
                  {logListView &&
                    logListView.map((result, index) => (
                      <TableRow hover key={index} sx={{ height: '50px' }}>
                        <TableCell
                          style={{
                            width: 180,
                            verticalAlign: 'center',
                          }}
                        >
                          <Grid>{formatLogTime(result.logDate)}</Grid>
                          <Grid
                            sx={{
                              color: (theme) => theme.palette.text.tertiary,
                              fontSize: '14px',
                            }}
                          >
                            {formatLogDate(result.logDate)}
                          </Grid>
                        </TableCell>
                        <TableCell
                          style={{ width: 180, verticalAlign: 'center' }}
                        >
                          <Box
                            sx={{
                              display: 'flex',
                              alignItems: 'center',
                            }}
                          >
                            {logStatusIcon(result.status)}
                            &nbsp;
                            {logStatusLabel(result.status)}
                          </Box>
                        </TableCell>
                        <TableCell
                          sx={{
                            color: (theme) => theme.palette.primary.white,
                            whiteSpace: 'pre-wrap',
                          }}
                        >
                          {result.message}
                        </TableCell>
                        <TableCell sx={{ width: '15px' }}>
                          <CopyButton
                            data-testid="copyMessage"
                            content={result.message}
                            size="small"
                            title="Copy message"
                            isBorderPresent
                          />
                        </TableCell>
                      </TableRow>
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
                {[...Array(7)].map((_) => (
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
                    <TableCell sx={{ width: '5%' }}>
                      <Skeleton sx={{ my: 1, py: 2, px: 0.5 }} />
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
