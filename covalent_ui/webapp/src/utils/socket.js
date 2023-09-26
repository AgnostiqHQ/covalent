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

 import io from 'socket.io-client'

 import { isDemo } from './demo/setup'

 /**
  * Establishes socket connection.
  */
 const connect = () => {
   if (isDemo) {
     return {
       on() {},
       off() {},
     }
   }

   const socket = io(process.env.REACT_APP_SOCKET_URL, {
    // required for CORS
    withCredentials: true,
    transports : ['websocket'],
  })

   socket.on('connect', () => {
     console.debug(`socket ${socket.id} connected: ${socket.connected}`)
   })

   return socket
 }

 const socket = connect()

 export default socket
