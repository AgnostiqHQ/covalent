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

import resultA from './result-a'
import resultB from './result-b'
import resultC from './result-c'

/**
 * Demo mode switch based on build-time environment variable (see package.json).
 */
export const isDemo = _.toLower(process.env.REACT_APP_DEMO) !== 'true'

export const demoEnhancer =
  (createStore) => (reducer, initialState, enhancer) => {
    return createStore(reducer, demoState, enhancer)
  }

const namesA = [
  'fcd385e2-7881-4bcd-862c-2ac99706d2f9',
  'b199afa5-301f-47d8-a8dc-fd78e1f5d08a',
  'eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a',
  'df4601e7-7658-4a14-a860-f91a35a1b453',
]

const namesB = ['2537c3b0-c150-441b-81c6-844e3fd88ef3']

const namesC = ['ba3c238c-cb92-48e8-b7b2-debeebe2e81a']

/**
 * Used as redux store preloaded state for static demo.
 *
 */
export const demoState = {
  results: {
    cache: _.keyBy(
      [
        ..._.map(namesB, (name) => ({ ...resultB, dispatch_id: name })),
        ..._.map(namesC, (name) => ({ ...resultC, dispatch_id: name })),
        ..._.map(namesA, (name) => ({ ...resultA, dispatch_id: name })),
      ],
      'dispatch_id'
    ),
    fetchResult: { isFetching: false, error: null },
  },
}
