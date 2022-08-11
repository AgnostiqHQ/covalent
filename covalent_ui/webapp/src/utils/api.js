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

import axios from 'axios'

const API = axios.create({
  baseURL: process.env.REACT_APP_API_URL,
})

API.interceptors.response.use(
  // unwrap response data
  ({ data }) => data,

  // catch statusCode != 200 responses and format error
  (error) => {
    if (error.response) {
      const errorData = {
        ...error.response.data,
        status: error.response.status
      }
      return Promise.reject(errorData)
    }
    return Promise.reject({ message: error.message })
  }
)

export default API
