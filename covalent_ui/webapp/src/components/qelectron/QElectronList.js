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
  TableContainer,
  TableSortLabel,
  Box,
  styled,
  tableCellClasses,
  tableRowClasses,
  tableBodyClasses,
  tableSortLabelClasses,
  linkClasses,
  Grid,
  SvgIcon,
  Tooltip,
  Skeleton
} from '@mui/material'

import { statusIcon, getLocalStartTime, formatDate, truncateMiddle } from '../../utils/misc'
import { Table as RTable } from 'react-virtualized';
import { ReactComponent as FilterSvg } from '../../assets/qelectron/filter.svg'
import CopyButton from '../common/CopyButton'
import useMediaQuery from '@mui/material/useMediaQuery'
import {
  qelectronJobs,
} from '../../redux/electronSlice'

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

const ResultsTableHead = ({ order, orderBy, onSort }) => {
  return (
    <TableHead sx={{ position: 'sticky', zIndex: 19 }}>
      <TableRow>
        {_.map(headers, (header) => {
          return (
            <TableCell
              key={header.id}
              sx={(theme) => ({
                border: 'none',
                borderColor:
                  theme.palette.background.coveBlack03 + '!important',
                paddingLeft: header?.id === 'executor' ? '2.3rem' : header?.id === 'start_time' ? '0.5rem' : ''
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
    backgroundColor: 'transparent',
  },

  // copy btn on hover
  [`& .${tableBodyClasses.root} .${tableRowClasses.root}`]: {
    '& .copy-btn': { visibility: 'hidden' },
    '&:hover .copy-btn': { visibility: 'visible' },
  },

  // customize hover
  [`& .${tableBodyClasses.root} .${tableRowClasses.root}:hover`]: {
    backgroundColor: theme.palette.background.coveBlack02,

    [`& .${tableCellClasses.root}`]: {
      borderColor: 'transparent',
      paddingTop: 4,
      paddingBottom: 4,
    },
    [`& .${linkClasses.root}`]: {
      color: theme.palette.text.secondary,
    },
  },

  [`& .${tableBodyClasses.root} .${tableRowClasses.root}`]: {
    backgroundColor: 'transparent',
    cursor: 'pointer',

    [`& .${tableCellClasses.root}`]: {
      borderColor: 'transparent',
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
    backgroundColor: theme.palette.background.default,
  },

  // customize border
  [`& .${tableCellClasses.root}`]: {
    borderColor: 'transparent',
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

const QElectronList = ({ expanded, data, rowClick, electronId, dispatchId, setExpanded, defaultId, setOpenSnackbar, setSnackbarMessage }) => {
  const dispatch = useDispatch()
  const [selected, setSelected] = useState([])
  const [selectedId, setSelectedId] = useState(defaultId)
  const [sortColumn, setSortColumn] = useState('start_time')
  const [sortOrder, setSortOrder] = useState('DESC')
  const isHeightAbove850px = useMediaQuery('(min-height: 850px)')
  const isHeight900920px = useMediaQuery('(min-height: 900px) and (max-height: 920px)')
  const isHeight920940px = useMediaQuery('(min-height: 920px) and (max-height: 940px)')
  const isHeightAbove940px = useMediaQuery('(min-height: 940px)')
  const isHeightAbove945px = useMediaQuery('(min-height: 945px)')
  const isHeightAbove1024px = useMediaQuery('(min-height: 1024px)')
  const isHeightAbove1040px = useMediaQuery('(min-height: 1040px)')
  const isFetching = useSelector(
    (state) => state.electronResults.qelectronJobsList.isFetching
  )

  useEffect(() => {
    setSelectedId(defaultId)
  }, [defaultId])

  const isError = useSelector(
    (state) => state.electronResults.qelectronJobsList.error
  );

  // check if there are any API errors and show a sncakbar
  useEffect(() => {
    if (isError) {
      setOpenSnackbar(true)
      if (isError?.detail && isError?.detail?.length > 0 && isError?.detail[0] && isError?.detail[0]?.msg) {
        setSnackbarMessage(isError?.detail[0]?.msg)
      }
      else {
        setSnackbarMessage(
          'Something went wrong,please contact the administrator!'
        )
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isError]);

  useEffect(() => {
    if (electronId || electronId === 0) {
      const bodyParams = {
        sort_by: sortColumn,
        direction: sortOrder,
        offset: 0
      }
      dispatch(
        qelectronJobs({
          dispatchId,
          electronId,
          bodyParams
        })
      )
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sortColumn, sortOrder])

  const handleChangeSort = (column) => {
    setSelected([])
    const isAsc = sortColumn === column && sortOrder === 'asc'
    setSortOrder(isAsc ? 'desc' : 'asc')
    setSortColumn(column)
  }

  // const getHeight = () => {
  //   if (xlmatches) {
  //     return expanded ? '23rem' : '40rem'
  //   } else if (xxlmatches) {
  //     return expanded ? '63rem' : '40rem'
  //   } else if (slmatches) {
  //     return expanded ? '24rem' : '48rem'
  //   } else {
  //     return expanded ? '16rem' : '32rem'
  //   }
  // }

  const renderHeader = () => {
    return (<>
      {!(_.isEmpty(data)) &&
        <ResultsTableHead
          //   totalRecords={totalRecords}
          order={sortOrder}
          orderBy={sortColumn}
          numSelected={_.size(selected)}
          total={_.size(data)}
          onSort={handleChangeSort}
        />}
    </>
    )
  }

  const getReactVirHeight = () => {
    let height = !expanded ? 450 : 200
    if (isHeightAbove850px) {
      height = !expanded ? 550 : 310
    }
    if (isHeight900920px) {
      height = !expanded ? 583 : 360
    }
    if (isHeight920940px) {
      height = !expanded ? 610 : 360
    }
    if (isHeightAbove940px) {
      height = !expanded ? 600 : 400
    }
    if (isHeightAbove945px) {
      height = !expanded ? 660 : 410
    }
    if (isHeightAbove1024px) {
      height = !expanded ? 700 : 480
    }
    if (isHeightAbove1040px) {
      height = !expanded ? 750 : 500
    }
    return height;
  }

  const getReactVirCount = () => {
    let count = expanded ? 3 : 5;
    if (isHeightAbove940px) {
      count = !expanded ? 5 : 8
    }
    if (isHeightAbove1040px) {
      count = !expanded ? 8 : 11;
    }
    return count;
  }

  function renderRow({ index, key, style }) {
    const result = data[index]
    return (
      <div key={key} className="row" style={style}>
        <TableRow
          sx={{
            height: '1rem',
            width: "1480px",
            backgroundColor: 'transparent',
            '&.MuiTableRow-root:hover': {
              backgroundColor: (theme) => theme.palette.background.coveBlack02
            },
            '&.MuiTableRow-root.Mui-selected': {
              backgroundColor: (theme) => theme.palette.background.coveBlack02
            },
            '&.MuiTableRow-root.Mui-selected:hover': {
              backgroundColor: (theme) => theme.palette.background.default,
            },
            '& .MuiTableCell-root': {
              borderColor: 'transparent',
              paddingTop: 0.2,
              paddingBottom: 0.1,
              cursor: 'pointer'
            },
            '& .MuiTableCell-root:first-of-type': {
              borderTopLeftRadius: 8,
              borderBottomLeftRadius: 8,
            },
            '& .MuiTableCell-root:last-of-type': {
              borderTopRightRadius: 8,
              borderBottomRightRadius: 8,
            }
          }}
          data-testid="copyMessage"
          data-tip
          data-for="logRow"
          onClick={() => {
            setExpanded(true);
            setSelectedId(result?.job_id)
            rowClick(result?.job_id)
          }}
          hover
          selected={result?.job_id === selectedId}
          key={key}
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
              {statusIcon(result?.status)}
              <Tooltip title={result?.job_id} placement="left">
                <Typography
                  component="span"
                  sx={{
                    mx: 1,
                    verticalAlign: 'middle',
                    fontSize: '0.875rem',
                    color: (theme) => theme.palette.text.secondary,
                  }}
                  width="12rem"
                >
                  {truncateMiddle(result?.job_id, 8, 13)}
                </Typography>
              </Tooltip>
              <CopyButton
                isBorderPresent
                content={result?.job_id}
                backgroundColor='#08081A'
              />
            </Grid>
          </TableCell>
          <TableCell>
            <Box
              sx={{
                display: 'flex',
                fontSize: '14px',
                width: '7rem'
              }}
            >
              {formatDate(getLocalStartTime(result?.start_time))}
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
      </div >
    );
  }

  return (
    <Grid
      mt={3}
      px={0}
      sx={{
        height: expanded ? '17rem' : '33rem',
        ...(isHeightAbove850px && {
          height: expanded ? '23.5rem' : '39.25rem',
        }),
        ...(isHeight900920px && {
          height: expanded ? '27rem' : '42rem',
        }),
        ...(isHeight920940px && {
          height: expanded ? '27rem' : '44rem',
        }),
        ...(isHeightAbove940px && {
          height: expanded ? '29rem' : '44.75rem',
        }),
        ...(isHeightAbove945px && {
          height: expanded ? '32rem' : '48rem',
        }),
        ...(isHeightAbove1024px && {
          height: expanded ? '34rem' : '50rem',
        }),
        ...(isHeightAbove1040px && {
          height: expanded ? '36rem' : '51.5rem',
        }),
        background: (theme) => theme.palette.background.qListBg,
      }}
      data-testid="QelectronList-grid"
    >
      <Box data-testid="logsTable">
        {!isFetching && data && (
          <Grid sx={{
            height: expanded ? '17rem' : '33rem',
            ...(isHeightAbove850px && {
              height: expanded ? '23.5rem' : '39.25rem',
            }),
            ...(isHeight900920px && {
              height: expanded ? '27rem' : '42rem',
            }),
            ...(isHeight920940px && {
              height: expanded ? '27rem' : '44rem',
            }),
            ...(isHeightAbove940px && {
              height: expanded ? '29rem' : '44.75rem',
            }),
            ...(isHeightAbove945px && {
              height: expanded ? '29rem' : '48rem',
            }),
            ...(isHeightAbove1024px && {
              height: expanded ? '34rem' : '50rem',
            }),
            ...(isHeightAbove1040px && {
              height: expanded ? '36rem' : '51.5rem',
            })
          }}
            ml={1}
            data-testid="QelectronList-table"
          >

            {!_.isEmpty(data) && !isFetching &&
              <RTable
                width={680}
                height={getReactVirHeight()}
                rowHeight={50}
                // eslint-disable-next-line react/jsx-no-bind
                headerRowRenderer={renderHeader}
                // eslint-disable-next-line react/jsx-no-bind
                rowRenderer={renderRow}
                rowCount={data?.length}
                overscanRowCount={getReactVirCount()}
                rowGetter={({ index }) => data[index]}
              />}

            {_.isEmpty(data) && !isFetching && (
              <Typography
                sx={{
                  textAlign: 'center',
                  color: 'text.secondary',
                  fontSize: 'h6.fontSize',
                  paddingTop: 9,
                  paddingBottom: 2,
                }}
              >
                No results found.
              </Typography>
            )}
          </Grid>
        )
        }
      </Box >
      {isFetching && _.isEmpty(data) && (
        <>
          {/*  */}
          {/* <Skeleton variant="rectangular" height={50} /> */}
          <TableContainer>
            <StyledTable>
              <TableBody>
                {[...Array(3)].map(() => (
                  <TableRow key={Math.random()} sx={{
                    height: '2.5rem',
                  }}
                  >
                    <TableCell>
                      <Skeleton sx={{ my: 1, mx: 1 }} />
                    </TableCell>
                    <TableCell>
                      <Skeleton sx={{ my: 1, mx: 1 }} />
                    </TableCell>
                    <TableCell>
                      <Skeleton sx={{ my: 1, mx: 1 }} />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </StyledTable>
          </TableContainer>
        </>
      )
      }
    </Grid >
  )
}

export default QElectronList
