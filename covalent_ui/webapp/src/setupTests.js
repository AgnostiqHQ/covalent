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

// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom'

import resultA from './utils/demo/result-a'
import resultB from './utils/demo/result-b'

import { rest } from 'msw'
import { setupServer } from 'msw/node'

// ResizeObserver not available during tests, provide polyfill
global.ResizeObserver = require('resize-observer-polyfill')

// silence console.debug
jest.spyOn(console, 'debug').mockImplementation(jest.fn())

const server = setupServer(
  // request handlers
  rest.get('/api/v0/workflow/results', (req, res, ctx) => {
    return res(ctx.json([resultA, resultB]))
  }),
  rest.get(
    `/api/v0/workflow/results/${resultA.dispatch_id}`,
    (req, res, ctx) => {
      return res(ctx.json(resultA))
    }
  )
)

beforeAll(() => {
  // Setup offset* properties
  // see: https://github.com/wbkd/react-flow/issues/716

  Object.defineProperties(window.HTMLElement.prototype, {
    offsetHeight: {
      get() {
        return parseFloat(this.style.height) || 1
      },
    },
    offsetWidth: {
      get() {
        return parseFloat(this.style.width) || 1
      },
    },
  })

  window.SVGElement.prototype.getBBox = () => ({
    x: 0,
    y: 0,
    width: 0,
    height: 0,
  })

  // Mock localStorage
  Object.defineProperty(window, 'localStorage', {
    value: {
      getItem: jest.fn(() => null),
      setItem: jest.fn(() => null),
    },
    writable: true,
  })
})

beforeAll(() => server.listen())
afterEach(() => server.resetHandlers())
afterAll(() => server.close())
