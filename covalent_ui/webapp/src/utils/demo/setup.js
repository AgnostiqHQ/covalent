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

import resultA from './result-a'
import resultB from './result-b'
import resultC from './result-c'
import latticePreview from './draw-a'

/**
 * Demo mode switch based on build-time environment variable (see package.json).
 */
export const isDemo = _.toLower(process.env.REACT_APP_DEMO) === 'true'

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
  latticePreview,
}
