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
import { ReactComponent as DispatchList } from '../../assets/dashboard.svg'
import { ReactComponent as DispatchPreview } from '../../assets/license.svg'
import { ReactComponent as NavSettings } from '../../assets/SettingsIcon.svg'
import { ReactComponent as Logs } from '../../assets/logs.svg'

import { ReactComponent as ExitNewIcon } from '../../assets/exit.svg'
import { ReactComponent as closeIcon } from '../../assets/close.svg'
import { useMatch } from 'react-router-dom'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate } from 'react-router-dom'
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
        <LinkButton
          title="Logo"
          path="/"
          icon={Logo}
          margintop={8}
          paddingTop="5px"
          paddingLeft="3px"
          paddingRight="0px"
          paddingBottom="0px"
          position="unset"
          bottom={0}
        />

        <LinkButton
          title="Dispatch list"
          path="/"
          icon={DispatchList}
          margintop={8}
          paddingTop="5px"
          paddingLeft="3px"
          paddingRight="0px"
          paddingBottom="0px"
          position="unset"
          bottom={0}
        />

        <LinkButton
          title="Lattice draw preview"
          path="/preview"
          icon={DispatchPreview}
          paddingTop="5px"
          paddingLeft="3px"
          paddingRight="0px"
          paddingBottom="0px"
          position="unset"
          bottom={0}
        />

        <LinkButton
          title="Settings"
          path="/settings"
          icon={NavSettings}
          position="fixed"
          bottom={0}
          paddingTop="4px"
          paddingLeft="2px"
          paddingRight="4px"
          paddingBottom="4px"
        />
        <Grid>
          <LinkButton
            title="Logs"
            path="/logs"
            icon={Logs}
            paddingTop="7px"
            paddingLeft="4px"
            paddingRight="0px"
            paddingBottom="0px"
            position="fixed"
            bottom={70}
          />
        </Grid>
      </List>
    </Drawer>
  )
}

const DialogToolbar = ({
  openDialogBox,
  setOpenDialogBox,
  onClickHand,
  handleClose,
  handlePopClose,
}) => {
  return (
    <Toolbar disableGutters sx={{ mb: 1 }}>
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

const LinkButton = ({
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
  let navigate = useNavigate()

  const menuClick = (path) => {
    // navigate(path);
    if (dRes === null) {
      navigate(path)
    } else if (dRes.isChanged === true) {
      setPopupShow(true)
    } else {
      navigate(path)
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
          'Something went wrong and could not update settings!'
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
    navigate(path)
    const settingObj = {
      isChanged: false,
    }
    dispatch(toggleLatticeDrawer(settingObj))
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
        <ListItemButton sx={{ my: 2.5, mb: 6 }} onClick={() => menuClick(path)}>
          <Logo data-testid="covalentLogo" style={{ margin: 'auto' }} />
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
            disableRipple
            sx={{
              textAlign: 'left',
              position: position,
              bottom: bottom,
              '&:hover': {
                background: (theme) => theme.palette.background.default,
              },
            }}
            onClick={() => menuClick(path)}
            // component={Link}
            // to={path}
            selected={!!selected}
          >
            {!!selected ? (
              <SvgIcon
                sx={{
                  mx: 'auto',
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
                  marginLeft: title === 'Settings' ? '0px' : '4px',
                  '&:hover': {
                    mx: 'auto',
                    border: '1px solid #998AFF',
                    width: '30px',
                    height: '30px',
                    paddingTop: paddingTop,
                    paddingRight: paddingRight,
                    paddingLeft: paddingLeft,
                    paddingBottom: paddingBottom,
                    borderRadius: '6px',
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
