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

import React, { useState } from 'react'
import {
  Drawer,
  List,
  ListItemButton,
  Tooltip,
  SvgIcon,
  Grid,
  Toolbar,
  Typography,
  Snackbar,
} from '@mui/material'
import { ReactComponent as Logo } from '../../assets/covalent-logo.svg'
import { ReactComponent as LogoOnHover } from '../../assets/covalent-logo-hover.svg'

import { ReactComponent as DispatchList } from '../../assets/dashboard.svg'
import { ReactComponent as DispatchPreview } from '../../assets/license.svg'
import { ReactComponent as NavSettings } from '../../assets/SettingsIcon.svg'
import { ReactComponent as Logs } from '../../assets/logs.svg'

import { ReactComponent as ExitNewIcon } from '../../assets/exit.svg'
import { ReactComponent as closeIcon } from '../../assets/close.svg'
import { useMatch, useNavigate } from 'react-router-dom'
import { useDispatch, useSelector } from 'react-redux'
import DialogBox from '../../components/settings/DialogBox'
import { updateSettings } from '../../redux/settingsSlice'
import { toggleLatticeDrawer } from '../../redux/popupSlice'

export const navDrawerWidth = 60

const NavDrawer = () => {
  return (
    <Drawer
      data-testid="navDrawer"
      variant="permanent"
      anchor="left"
      className="side-drawernav"
      sx={{
        width: navDrawerWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: navDrawerWidth,
          boxSizing: 'border-box',
          border: 'none',
          backgroundColor: 'background.default',
        },
      }}
    >
      <List>
        <LinkButton title="Logo" path="/" icon={Logo} />

        <LinkButton
          title="Dispatch list"
          path="/"
          icon={DispatchList}
          paddingTop="5px"
          paddingLeft="3px"
          paddingRight="0px"
          paddingBottom="0px"
          position="fixed"
          bottom="68%"
        />

        <LinkButton
          title="Lattice draw preview"
          path="/preview"
          icon={DispatchPreview}
          paddingTop="5px"
          paddingLeft="3px"
          paddingRight="0px"
          paddingBottom="0px"
          position="fixed"
          bottom="60%"
        />

        <LinkButton
          title="Settings"
          path="/settings"
          icon={NavSettings}
          position="fixed"
          bottom={54}
          paddingTop="3px"
          paddingLeft="2px"
          paddingRight="3px"
          paddingBottom="6px"
        />
        <Grid>
          <LinkButton
            title="Logs"
            path="/logs"
            icon={Logs}
            paddingTop="8px"
            paddingLeft="5px"
            paddingRight="0px"
            paddingBottom="0px"
            position="fixed"
            bottom={0}
          />
        </Grid>
      </List>
    </Drawer>
  )
}

export const DialogToolbar = ({
  openDialogBox,
  setOpenDialogBox,
  onClickHand,
  handleClose,
  handlePopClose,
}) => {
  return (
    <Toolbar data-testid="toolBar" disableGutters sx={{ mb: 1 }}>
      <Typography
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      ></Typography>
      <DialogBox
        openDialogBox={openDialogBox}
        setOpenDialogBox={setOpenDialogBox}
        handler={onClickHand}
        handleClose={handleClose}
        title="Leave settings?"
        message="You have unsaved changes. How do you want to proceed"
        icon={ExitNewIcon}
        handlePopClose={handlePopClose}
      />
    </Toolbar>
  )
}

export const LinkButton = ({
  title,
  icon,
  path,
  margintop,
  paddingRight,
  paddingBottom,
  paddingTop,
  paddingLeft,
  position,
  bottom,
}) => {
  const dispatch = useDispatch()
  const selected = useMatch(path)
  const dRes = useSelector((state) => state.dataRes.popupData)
  const [popupShow, setPopupShow] = useState(false)
  const [openSnackbar, setOpenSnackbar] = useState(false)
  const [snackbarMessage, setSnackbarMessage] = useState(null)
  const [hovered, sethovered] = useState(false)
  let navigate = useNavigate()

  const menuClick = (pathname) => {
    if (dRes === null) {
      navigate(pathname)
    } else if (dRes.isChanged === true) {
      if (pathname === '/settings') {
        setPopupShow(false)
      } else {
        setPopupShow(true)
      }
    } else {
      navigate(pathname)
    }
  }

  const popHandleSubmit = (event) => {
    const updateData = {
      [dRes.mainKey]: {
        [dRes.nodeName]: dRes.data,
      },
    }
    dispatch(updateSettings(updateData)).then((action) => {
      if (action.type === updateSettings.fulfilled.type) {
        setOpenSnackbar(true)
        setSnackbarMessage('Settings updated successfully')
        setPopupShow(false)
        const settingObj = {
          isChanged: false,
        }
        dispatch(toggleLatticeDrawer(settingObj))
        navigate(path)
      } else if (action.type === updateSettings.rejected.type) {
        setOpenSnackbar(true)
        setSnackbarMessage(
          'Something went wrong and settings could not be updated.'
        )
        setPopupShow(false)
        const settingObj = {
          isChanged: false,
        }
        dispatch(toggleLatticeDrawer(settingObj))
      }
    })
  }

  const handleClose = (event) => {
    setPopupShow(false)
  }

  const handlePopClose = () => {
    setPopupShow(false)
    const settingObj = {
      isChanged: false,
    }
    dispatch(toggleLatticeDrawer(settingObj))
    navigate(path)
  }

  return (
    <>
      {popupShow && (
        <DialogToolbar
          openDialogBox={popupShow}
          setOpenDialogBox={popupShow}
          onClickHand={popHandleSubmit}
          handleClose={handleClose}
          handlePopClose={handlePopClose}
        />
      )}
      <Snackbar
        data-testid="snackbar"
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
      {title === 'Logo' ? (
        <ListItemButton
          data-testid="LogoListItemButton"
          sx={{
            position: 'fixed',
            top: 5,
            background: (theme) => theme.palette.background.default,
            '&:hover': {
              background: (theme) => theme.palette.background.default,
            },
          }}
          onClick={() => menuClick(path)}
          onMouseEnter={() => sethovered(true)}
          onMouseLeave={() => sethovered(false)}
        >
          {hovered ? (
            <LogoOnHover
              data-testid="covalentLogoHover"
              style={{ width: '30px' }}
            />
          ) : (
            <Logo data-testid="covalentLogo" style={{ width: '30px' }} />
          )}
        </ListItemButton>
      ) : (
        <Tooltip
          title={title}
          placement="right"
          arrow
          enterDelay={500}
          enterNextDelay={750}
        >
          <ListItemButton
            data-testid="SpecificListItemButton"
            disableRipple
            sx={{
              textAlign: 'left',
              position: position,
              left: -10,
              bottom: bottom,
              marginTop: margintop ? margintop : '0px',
              '&:hover': {
                background: (theme) => theme.palette.background.default,
              },
            }}
            onClick={() => menuClick(path)}
            selected={!!selected}
          >
            {!!selected ? (
              <SvgIcon
                sx={{
                  mx: 0.5,
                  border: '1px solid #998AFF',
                  width: '30px',
                  height: '30px',
                  paddingTop: paddingTop,
                  paddingRight: paddingRight,
                  paddingLeft: paddingLeft,
                  paddingBottom: paddingBottom,
                  borderRadius: '6px',
                  my: 2,
                }}
                component={icon}
              />
            ) : (
              <SvgIcon
                sx={{
                  mx: 'auto',
                  my: 2,
                  marginLeft: '4px',
                  border: '1px solid',
                  borderColor: (theme) => theme.palette.background.default,
                  width: '30px',
                  height: '30px',
                  paddingTop: paddingTop,
                  paddingRight: paddingRight,
                  paddingLeft: paddingLeft,
                  paddingBottom: paddingBottom,
                  borderRadius: '6px',

                  '&:hover': {
                    border: '1px solid #998AFF',
                    my: 2,
                  },
                }}
                component={icon}
              />
            )}
          </ListItemButton>
        </Tooltip>
      )}
    </>
  )
}
export default NavDrawer
