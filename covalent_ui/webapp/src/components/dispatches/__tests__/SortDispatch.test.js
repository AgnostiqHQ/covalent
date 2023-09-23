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
import React from 'react'
import { fireEvent, render, screen } from '@testing-library/react'
import App from '../SortDispatch'
import theme from '../../../utils/theme'
import ThemeProvider from '@mui/system/ThemeProvider'

function reduxRender(renderedComponent) {
  return render(
    <ThemeProvider theme={theme}>{renderedComponent}</ThemeProvider>
  )
}

const sortDispatchCases = [
  ['All', 'category'],
  [4, 'count'],
]

describe('sort dispatch', () => {
  test.each(sortDispatchCases)('render %p in %p section', (firstArg) => {
    reduxRender(<App title="All" count={4} isFetching={false} />)
    const element = screen.getByText(firstArg)
    expect(element).toBeInTheDocument()
  })

  it('click sort', () => {
    const setFilterValue = jest.fn()
    const setSelected = jest.fn()
    const setOffset = jest.fn()

    reduxRender(
      <App
        title="All"
        count={4}
        isFetching={false}
        setFilterValue={setFilterValue}
        setSelected={setSelected}
        setOffset={setOffset}
      />
    )
    const element = screen.getByTestId('sort')
    expect(element).toBeInTheDocument()
    fireEvent.click(element)
  })
})
