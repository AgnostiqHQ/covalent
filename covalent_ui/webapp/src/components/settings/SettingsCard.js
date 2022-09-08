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

import React, { useEffect, useState, useRef } from 'react';
import {
  Container, Grid, Box, Input, InputLabel, Radio, RadioGroup, Button,
  Stack, Snackbar, SvgIcon, Toolbar
} from '@mui/material';
import Typography from '@mui/material/Typography';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemText from '@mui/material/ListItemText';
import ListItemIcon from '@mui/material/ListItemIcon';
import Collapse from '@mui/material/Collapse';
import ExpandLess from '@mui/icons-material/ExpandLess';
import ExpandMore from '@mui/icons-material/ExpandMore';
import FormControlLabel from '@mui/material/FormControlLabel';
import FormControl from '@mui/material/FormControl';
import FormLabel from '@mui/material/FormLabel';
import { settingsResults, updateSettings } from '../../redux/settingsSlice';
import { useDispatch, useSelector } from 'react-redux';
import _ from 'lodash'
import Skeleton from '@mui/material/Skeleton';
import { ReactComponent as closeIcon } from '../../assets/close.svg'
import DialogBox from './DialogBox'
import { ReactComponent as ExitNewIcon } from '../../assets/exit.svg'

const DialogToolbar = ({
  openDialogBox,
  setOpenDialogBox,
  onClickHand,
}) => {
  return (
    <Toolbar disableGutters sx={{ mb: 1 }}>
      <Typography
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
      </Typography>
      <DialogBox
        openDialogBox={openDialogBox}
        setOpenDialogBox={setOpenDialogBox}
        handler={onClickHand}
        title="Leave settings?"
        message="You have unsaved changes. How do you want to proceed"
        icon={ExitNewIcon}
      />
    </Toolbar>
  )
}

const SettingsCard = () => {
  const dispatch = useDispatch()
  const [open, setOpen] = useState(false);
  const [subMenu, setSubMenu] = useState([]);
  const [resultKey, setResultKey] = useState("");
  const [resultOutput, setResultOutput] = useState();
  const settings_result = useSelector((state) => state.settingsResults.settingsList)
  const menuKeyName = Object.keys(settings_result)
  const callSocketApi = useSelector((state) => state.common.callSocketApi)
  const setting__ref = useRef(null);
  const [openSnackbar, setOpenSnackbar] = useState(false)
  const [snackbarMessage, setSnackbarMessage] = useState(null)
  const [isDisabled, setIsDisabled] = useState(false);
  const [handle, setHandle] = useState('');
  const [openDialogBox, setOpenDialogBox] = useState(false)

  useEffect(() => {
    dispatch(settingsResults())
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [callSocketApi])

  const handleSubmit = (event) => {
    const formData = new FormData(event.currentTarget);
    event.preventDefault();
    const formDataObj = {};
    formData.forEach((value, key) => (
      formDataObj[key] = value)
    );
    const updateData = {
      [resultKey]: formDataObj
    }
    dispatch(updateSettings(updateData)).then((action) => {
      if (action.type === updateSettings.fulfilled.type) {
        setOpenSnackbar(true)
        setSnackbarMessage('settings updated successfully')
        dispatch(settingsResults())
      } else if (action.type === updateSettings.rejected.type) {
        setOpenSnackbar(true)
        setSnackbarMessage('Something went wrong and could not settings updated!')
      }
    })
  };

  const popHandleSubmit = (event) => {
    const formData = new FormData(document.getElementById("get__pop_id"));
    event.preventDefault();
    const formDataObj = {};
    formData.forEach((value, key) => (
      formDataObj[key] = value)
    );
    const updateData = {
      [resultKey]: formDataObj
    }
    dispatch(updateSettings(updateData)).then((action) => {
      if (action.type === updateSettings.fulfilled.type) {
        setOpenSnackbar(true)
        setSnackbarMessage('settings updated successfully')
      } else if (action.type === updateSettings.rejected.type) {
        setOpenSnackbar(true)
        setSnackbarMessage('Something went wrong and could not settings updated!')
      }
    })
    setOpenDialogBox(false)
  };

  const getSubmenuName = (name) => {
    let formattedName = name;
    const uSpliit = name.includes("_");
    if (uSpliit) {
      var a = name.replace(name.at(0), name.at(0).toLocaleUpperCase()).
        substring(0, name.indexOf("_"))
      var b = name.replace(name.at(0), name.at(0).toLocaleUpperCase()).
        substring(name.indexOf("_") + 1, name.length)
      formattedName = a + " " + b.replace(b.at(0), b.at(0).toLocaleUpperCase())
    }
    else {
      if (name === 'slurm') {
        formattedName = name.toUpperCase();
      }
      else if (name === 'dask') {
        formattedName = name.toUpperCase();
      }
      else {
        formattedName = name.charAt(0).toUpperCase() + name.slice(1);
      }
    }
    return formattedName
  }
  const getLabelName = (name) => {
    let formattedName = name;
    const uSpliit = name.includes("_");
    if (uSpliit) {
      var a = name.replace(name.at(0), name.at(0).toLocaleUpperCase()).
        substring(0, name.indexOf("_"))
      var b = name.replace(name.at(0), name.at(0).toLocaleUpperCase()).
        substring(name.indexOf("_") + 1, name.length)
      formattedName = a + " " + b.replace(b.at(0), b.at(0))
    }
    else {
      if (name === 'sdk') {
        formattedName = name.toUpperCase();
      }
      else {
        formattedName = name.charAt(0).toUpperCase() + name.slice(1);
      }
    }
    if (formattedName === 'Cache dir') {
      formattedName = 'Cache directory'
    }
    else if (formattedName === 'Results dir') {
      formattedName = 'Results directory'
    }
    else if (formattedName === 'Log dir') {
      formattedName = 'Log directory'
    }
    else if (formattedName === 'Base dir') {
      formattedName = 'Base directory'
    }
    return formattedName
  }
  const getSettingsName = (name) => {
    let formattedName = name;
    const uSpliit = name.includes("_");
    if (uSpliit) {
      var a = name.replace(name.at(0), name.at(0).toLocaleUpperCase()).
        substring(0, name.indexOf("_"))
      var b = name.replace(name.at(0), name.at(0).toLocaleUpperCase()).
        substring(name.indexOf("_") + 1, name.length)
      formattedName = a + " " + b.replace(b.at(0), b.at(0).toLocaleUpperCase())
    }
    else {
      if (name === 'sdk') {
        formattedName = name.toUpperCase();
      }
      else {
        formattedName = name.charAt(0).toUpperCase() + name.slice(1);
      }
    }
    return formattedName
  }
  const isChildHasList = (item) => {
    let childIsObject = false;
    _.map(item, function (value) {
      if (_.isObject(value)) childIsObject = true;
    })
    return childIsObject;
  }

  const handleClick = (item) => {
    let tmpList = [];
    _.map(item, function (value, key) {
      if (_.isObject(value)) {
        setOpen(!open);
        tmpList.push(key)
      }
    })
    setSubMenu(tmpList);
  };

  const menuClick = (value, key) => {
    if (key === "sdk" || key === "executors") {
      setIsDisabled(false)
    }
    else {
      setIsDisabled(true)
    }

    if (handle) {
      setOpenDialogBox(true)
    } else {
      setOpenDialogBox(false)
      setResultKey(key)
      setResultOutput(value)
    }
  }

  const handleKeypress = (event) => {
    setHandle(event.key)
  }

  const cancelButton = () => {
    if (handle) {
      setOpenDialogBox(true)
    } else {
      setOpenDialogBox(false)
    }
  }

  return (
    <Container maxWidth="xl" sx={{ mb: 4, mt: 7.5, ml: 4 }}>
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
      <Typography variant="h4" component="h4">
        Settings
      </Typography>
      <Grid container spacing={3} sx={{ mt: 4 }}>

        <Grid item xs={3}
          sx={(theme) => ({
            borderRight: 1,
            borderColor: theme.palette.background.coveBlack02,
          })}
        >
          <List>
            {menuKeyName.length !== 0 ?
              <>
                {
                  _.map(settings_result, function (value, key) {
                    return (
                      <ListItem disablePadding>
                        <ListItemButton
                          onClick={isChildHasList ? () => handleClick(value) : () => { }}>
                          {isChildHasList(value) &&
                            <ListItemIcon>
                              {open ? <ExpandLess /> : <ExpandMore />}
                            </ListItemIcon>
                          }
                          <ListItemText inset primary={getSettingsName(key)}
                            onClick={() => menuClick(value, key)}
                            disableTypography
                            sx={{ pl: "0px", fontSize: '18px' }} />
                        </ListItemButton>
                      </ListItem>
                    )
                  })
                }
                {open &&
                  <Collapse in={open} timeout="auto" unmountOnExit>
                    <List component="div" disablePadding>
                      {
                        _.map(subMenu, function (value, key) {
                          return (
                            <ListItem disablePadding>
                              <ListItemButton sx={{ pl: 4, pt: 0.3, pb: 0.3 }}>
                                <ListItemText inset primary={getSubmenuName(value)}
                                  disableTypography
                                  sx={{ pl: "0px", fontSize: '18px' }} />
                              </ListItemButton>
                            </ListItem>
                          )
                        })
                      }
                    </List>
                  </Collapse>
                }
              </>
              :
              <Box sx={{ width: 300 }}>
                <Skeleton />
                <Skeleton animation="wave" />
                <Skeleton animation={false} />
              </Box>
            }
          </List>
        </Grid>

        <Grid item xs={9}>
          <Typography variant="h6" component="h6">
            {getSettingsName(resultKey)}
          </Typography>
          <Grid container spacing={3} sx={{ mt: 2 }}>
            <Grid item xs={7}>
              <form onSubmit={handleSubmit} id="get__pop_id">
                {
                  _.map(resultOutput, function (value, key) {

                    return (
                      <Box sx={{ mb: 3 }}>
                        {
                          _.isObject(value)
                            ?
                            <>
                              <Typography variant="h6" component="h6">
                                {getSettingsName(key)}
                              </Typography>
                              {
                                _.map(value, function (item, key) {
                                  return (
                                    <Box sx={{ mt: 3 }}>
                                      {value === "true" || value === "false" ?
                                        <FormControl>
                                          <FormLabel id="demo-row-radio-buttons-group-label"
                                            sx={(theme) => ({
                                              fontSize: '16px',
                                            })}> {getSettingsName(key)}</FormLabel>
                                          <RadioGroup
                                            row
                                            aria-labelledby="demo-row-radio-buttons-group-label"
                                            name="row-radio-buttons-group"
                                          >
                                            <FormControlLabel value="true"
                                              disabled={isDisabled} control={<Radio />} label="True" />
                                            <FormControlLabel value="false"
                                              disabled={isDisabled} control={<Radio />} label="False" />
                                          </RadioGroup>
                                        </FormControl>
                                        :
                                        <>
                                          <InputLabel variant="standard" htmlFor="uncontrolled-native"
                                            sx={{
                                              fontSize: '16px',
                                              mb: 1
                                            }}>
                                            {getLabelName(key)}
                                          </InputLabel>
                                          <Input sx={{
                                            px: 2,
                                            py: 0.5,
                                            width: "100%",
                                            height: '45px',
                                            border: '1px solid #303067',
                                            borderRadius: '60px',
                                          }}
                                            disabled={isDisabled}
                                            onKeyDown={handleKeypress}
                                            ref={setting__ref}
                                            name={key}
                                            defaultValue={item}
                                            disableUnderline
                                            placeholder="Log directroy" />
                                        </>
                                      }
                                    </Box>
                                  )
                                })
                              }
                            </>
                            :
                            <>
                              {value === "true" || value === "false" ?
                                <FormControl>
                                  <FormLabel id="demo-row-radio-buttons-group-label"
                                    sx={(theme) => ({
                                      fontSize: '16px',
                                    })}> {getSettingsName(key)}</FormLabel>
                                  <RadioGroup
                                    row
                                    aria-labelledby="demo-row-radio-buttons-group-label"
                                    name={key}
                                    ref={setting__ref}
                                    defaultValue={value}
                                  >
                                    <FormControlLabel disabled={isDisabled} value="true" control={<Radio />} label="True" />
                                    <FormControlLabel disabled={isDisabled} value="false" control={<Radio />} label="False" />
                                  </RadioGroup>
                                </FormControl>
                                :
                                <>
                                  <InputLabel variant="standard" htmlFor="uncontrolled-native"
                                    sx={{
                                      fontSize: '16px',
                                      mb: 1
                                    }}>
                                    {getLabelName(key)}
                                  </InputLabel>
                                  <Input sx={{
                                    px: 2,
                                    py: 0.5,
                                    width: "100%",
                                    height: '45px',
                                    border: '1px solid #303067',
                                    borderRadius: '60px',
                                  }}
                                    disabled={isDisabled}
                                    onKeyDown={handleKeypress}
                                    ref={setting__ref}
                                    name={key}
                                    defaultValue={value}
                                    disableUnderline
                                    placeholder={key} />
                                </>
                              }
                            </>
                        }

                      </Box>
                    )
                  })
                }

                <DialogToolbar
                  openDialogBox={openDialogBox}
                  setOpenDialogBox={setOpenDialogBox}
                  onClickHand={popHandleSubmit}
                />

                <Stack spacing={2} direction="row" sx={{ float: 'right' }}>
                  <Button variant="outlined"
                    onClick={cancelButton}
                    sx={(theme) => ({
                      padding: '8px 20px',
                      border: '1px solid #6473FF',
                      borderRadius: '60px',
                      color: 'white',
                      fontSize: '16px',
                      textTransform: 'capitalize'
                    })}>Cancel</Button>
                  <Button var
                    type="submit"
                    sx={(theme) => ({
                      background: '#5552FF',
                      borderRadius: '60px',
                      color: 'white',
                      padding: '8px 30px',
                      fontSize: '16px',
                      textTransform: 'capitalize'
                    })}>Save</Button>
                </Stack>
              </form>
            </Grid>
          </Grid>
        </Grid>
      </Grid>
    </Container >
  )
}

export default SettingsCard
