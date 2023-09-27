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
import { useEffect } from 'react'
import { useDispatch } from 'react-redux'
import CssBaseline from '@mui/material/CssBaseline'
import ThemeProvider from '@mui/system/ThemeProvider'
import { Helmet, HelmetProvider } from 'react-helmet-async'
import { Routes, Route, useLocation } from 'react-router-dom'
import './App.css'
import Dashboard from './components/dashboard/Dashboard'
import socket from './utils/socket'
import { setLattice } from './redux/latticePreviewSlice'
import { socketAPI } from './redux/commonSlice'
import theme from './utils/theme'
import { ReactFlowProvider } from 'react-flow-renderer'
import LatticePreviewLayout from './components/preview/LatticePreviewLayout'
import {DispatchLayoutValidate} from './components/dispatch/DispatchLayout'
import TerminalLayout from './components/terminal/TerminalLayout'
import SettingsLayout from './components/settings/SettingsLayout'
import NotFound from './components/NotFound'
import LogsLayout from './components/logs/LogsLayout'
import { differenceInSeconds } from 'date-fns'
const App = () => {
  const dispatch = useDispatch()
  const pathName = useLocation()
  useEffect(() => {
    let lastCalledOn = null
    var onUpdate = (update) => {
      let canCallAPI = false
      if (
        pathName.pathname === '/' ||
        (pathName.pathname !== '/' &&
          pathName.pathname === `/${update.result.dispatch_id}`)
      ) {
        let currentTime = new Date()
        let compareTime = new Date(lastCalledOn)
        const diffInSec = differenceInSeconds(currentTime, compareTime)
        if (diffInSec >= 3 || update.result.status !== 'RUNNING') {
          canCallAPI = true
        } else {
          canCallAPI = false
        }
      }
      if (canCallAPI) {
        lastCalledOn = new Date()
        dispatch(socketAPI())
      }
    }
    socket.on('result-update', onUpdate)
    return () => {
      socket.off('result-update', onUpdate)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pathName])

  useEffect(() => {
    const onDrawRequest = (request) => {
      dispatch(setLattice(request.payload))
    }
    socket.on('draw_request', onDrawRequest)
    return () => {
      socket.off('draw_request', onDrawRequest)
    }
  })
  return (
    <HelmetProvider>
      <ReactFlowProvider>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <Helmet defaultTitle="Covalent" titleTemplate="%s - Covalent" />
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/:dispatchId" element={<DispatchLayoutValidate />} />
            <Route path="/preview" element={<LatticePreviewLayout />} />
            <Route path="/terminal" element={<TerminalLayout />} />
            <Route path="/settings" element={<SettingsLayout />} />
            <Route path="/logs" element={<LogsLayout />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </ThemeProvider>
      </ReactFlowProvider>
    </HelmetProvider>
  )
}
export default App
