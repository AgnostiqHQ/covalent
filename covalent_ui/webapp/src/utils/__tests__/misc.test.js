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

import '@testing-library/jest-dom'
import {
  logStatusLabel,
  isParameter,
  isPostProcess,
  formatDate,
  formatLogDate,
  sublatticeIconTopBar,
  sublatticeIcon,
  displayStatus,
  formatLogTime,
  secondsToHms,
  truncateMiddle,
  logStatusIcon,
  statusIcon,
  nodeLabelIcon,
  allowSublatticeAndGeneralNodes,
  allowPostProcessAndSubgraph,
  allowParameterAndSubgraph,
  allowSystemGeneratedAlone,
  allowSystemGenAndPostprocess,
  allowSystemGenAndParameter,
  getLocalStartTime,
  allowOtherThanSystemGen
} from '../misc'
import { render, screen } from '@testing-library/react'

describe('testing misc', () => {
  test('secondsToHms less than 1sec', () => {
    expect(secondsToHms(500)).toEqual('< 1sec')
  }, 5000)
  test('secondsToHms between 0 and 60 sec', () => {
    expect(secondsToHms(1500)).toEqual('< 1min')
  }, 5000)
  test('secondsToHms between 60 and 3600 sec', () => {
    expect(secondsToHms(360000)).toEqual('6m')
  }, 5000)
  test('secondsToHms between 3600 and 86400 sec', () => {
    expect(secondsToHms(3700000)).toEqual('1h 1m')
  }, 5000)
  test('secondsToHms between 86400 and 172800 sec', () => {
    expect(secondsToHms(99000000)).toEqual('> 1 day')
  }, 5000)
  test('secondsToHms > than 172800 sec', () => {
    expect(secondsToHms(360000000)).toEqual('4 days')
  }, 5000)

  test('truncate Middle of string', () => {
    jest.useFakeTimers('legacy')
    expect(truncateMiddle('sampleString', 0, 4)).toEqual('…ring')
  })
  test('truncate with start and end 0 case', () => {
    expect(truncateMiddle('sample', 0, 0)).toEqual('sample')
  })
  test('truncate with !end case', () => {
    expect(truncateMiddle('sample', 2)).toEqual('sa…')
  })
  test('truncate with empty string case', () => {
    expect(truncateMiddle('', 0, 4)).toEqual('')
  })
  test('testing isParameter: checks the input value', () => {
    const node = { name: ':parameter:' }
    expect(isParameter(node)).toEqual(true)
  })
  test('testing isParameter: null check', () => {
    const node = { name: ':parameter:' }
    expect(isParameter(node)).toBe(true)
  })
  test('testing isPostProcess: checks the input value', () => {
    const node = { name: ':postprocess:' }
    expect(isPostProcess(node)).toEqual(true)
  })
  test('testing isPostProcess: null check', () => {
    const node = { name: ':postprocess:' }
    expect(isPostProcess(node)).toBe(true)
  })
  test('testing allowSublatticeAndGeneralNodes: checks the input value', () => {
    const node = [{ name: ':sublattice:' }, { name: ':mui:' }]
    expect(allowSublatticeAndGeneralNodes(node)).toEqual(true)
  })
  test('testing allowSublatticeAndGeneralNodes: null check', () => {
    const node = [{ name: ':sublattice:' }, { name: ':mui:' }]
    expect(allowSublatticeAndGeneralNodes(node)).toBe(true)
  })
  test('testing allowPostProcessAndSubgraph: checks the input value', () => {
    const node = [{ name: ':sublattice:' }, { name: ':mui:' }, { name: ':postprocess' }]
    expect(allowPostProcessAndSubgraph(node)).toEqual(true)
  })
  test('testing allowPostProcessAndSubgraph: null check', () => {
    const node = [{ name: ':sublattice:' }, { name: ':mui:' }, { name: ':postprocess' }]
    expect(allowPostProcessAndSubgraph(node)).toBe(true)
  })
  test('testing allowParameterAndSubgraph: checks the input value', () => {
    const node = [{ name: ':sublattice:' }, { name: ':mui:' }, { name: ':parameter' }]
    expect(allowParameterAndSubgraph(node)).toEqual(true)
  })
  test('testing allowParameterAndSubgraph: null check', () => {
    const node = [{ name: ':sublattice:' }, { name: ':mui:' }, { name: ':parameter' }]
    expect(allowParameterAndSubgraph(node)).toBe(true)
  })
  test('testing allowSystemGeneratedAlone: checks the input value', () => {
    const node = [{ name: ':sublattice:' }, { name: ':mui:' }]
    expect(allowSystemGeneratedAlone(node)).toEqual(true)
  })
  test('testing allowSystemGeneratedAlone: null check', () => {
    const node = [{ name: ':sublattice:' }, { name: ':mui:' }]
    expect(allowSystemGeneratedAlone(node)).toBe(true)
  })
  test('testing allowSystemGenAndPostprocess: checks the input value', () => {
    const node = [{ name: ':mui:' }]
    expect(allowSystemGenAndPostprocess(node)).toEqual(true)
  })
  test('testing allowSystemGenAndPostprocess: null check', () => {
    const node = [{ name: ':mui:' }]
    expect(allowSystemGenAndPostprocess(node)).toBe(true)
  })
  test('testing allowSystemGenAndParameter: checks the input value', () => {
    const node = [{ name: ':parameter' }]
    expect(allowSystemGenAndParameter(node)).toEqual(true)
  })
  test('testing allowOtherThanSystemGen: checks the input value parameter', () => {
    const node = { name: ':parameter' }
    expect(allowOtherThanSystemGen(node)).toEqual(true)
  })
  test('testing allowOtherThanSystemGen: checks the input value postprocess', () => {
    const node = { name: ':postprocess' }
    expect(allowOtherThanSystemGen(node)).toEqual(true)
  })
  test('testing allowOtherThanSystemGen: checks the input value sublattice', () => {
    const node = { name: ':sublattice' }
    expect(allowOtherThanSystemGen(node)).toEqual(true)
  })
  test('allowOtherThanSystemGen null check', () => {
    expect(allowOtherThanSystemGen()).toBe(true)
  })
})

describe('testing logStatusLabel', () => {
  const resultListCases = [
    'INFO',
    'DEBUG',
    'WARNING',
    'WARN',
    'ERROR',
    'CRITICAL',
  ]
  test.each(resultListCases)('returns correct value', (arg) => {
    expect(logStatusLabel(arg).toLowerCase()).toMatch(arg.toLowerCase())
  })
  test('default case', () => {
    expect(logStatusLabel('sample')).toEqual('sample')
  })
})

describe('testing displayStatus', () => {
  test('returns the status value', () => {
    expect(displayStatus('sample--text')).toEqual('Sample Text')
  })
})

describe('testing formatDate', () => {
  test('testing formatted date', () => {
    expect(formatDate(new Date(2022, 12, 13))).toEqual('Jan 13, 00:00:00')
  })
  test('testing formatted invalid date', () => {
    expect(formatDate(new Date(''))).toEqual('-')
  })
})

describe('testing formatLogTime', () => {
  test('testing formatted log time', () => {
    expect(formatLogTime(new Date('Wed, 27 July 2016 13:30:00'))).toEqual(
      '13:30:00,000'
    )
  })
  test('testing formatted invalid log time', () => {
    expect(formatLogTime(new Date(''))).toEqual('-')
  })
})

describe('testing formatLogDate', () => {
  test('testing formatted Log date', () => {
    expect(formatLogDate(new Date(2022, 1, 11))).toEqual('2022-02-11')
  })
  test('testing formatted invalid log date', () => {
    expect(formatDate(new Date(''))).toEqual('-')
  })
})

describe('testing sublatticeIconTopBar', () => {
  const testData = ['COMPLETED', 'FAILED', 'RUNNING']
  test.each(testData)('testing icon render', (arg) => {
    render(sublatticeIconTopBar(arg))
    const element = screen.getByLabelText(arg)
    expect(element).toBeInTheDocument()
  })
  test('default case', () => {
    expect(sublatticeIconTopBar('')).toBeNull()
  })
})

describe('testing sublatticeIcon', () => {
  const testData = ['COMPLETED', 'FAILED', 'RUNNING']
  test.each(testData)('testing icon render', (arg) => {
    render(sublatticeIcon(arg))
    const element = screen.getByLabelText(arg)
    expect(element).toBeInTheDocument()
  })
  test('default case', () => {
    expect(sublatticeIcon('')).toBeNull()
  })
})

describe('testing logStatusIcon', () => {
  const testData = ['WARNING', 'WARN', 'INFO', 'DEBUG', 'ERROR', 'CRITICAL']
  test.each(testData)('testing icon render', (arg) => {
    render(logStatusIcon(arg))
    const element = screen.getByLabelText(arg)
    expect(element).toBeInTheDocument()
  })
  test('default case', () => {
    expect(logStatusIcon('')).toBeNull()
  })
})

describe('testing getLocalStartTime', () => {
  test('testing getLocalStartTime', () => {
    expect(getLocalStartTime(new Date('Wed, 27 July 2016 13:30:00'))).toEqual(
      '2016-07-27T13:30:00.000Z'
    )
  })
})

describe('testing statusIcon', () => {
  const testData = [
    'RUNNING',
    'STARTING',
    'NEW_OBJECT',
    'PENDING',
    'REGISTERING',
    'PENDING_BACKEND',
    'QUEUED',
    'PROVISIONING',
    'DEPROVISIONING',
    'COMPLETING',
    'COMPLETED',
    'POSTPROCESSING',
    'PENDING_POSTPROCESSING',
    'POSTPROCESSING_FAILED',
    'FAILED',
    'REG_FAILED',
    'BOOT_FAILED',
    'PROVISION_FAILED',
    'DEPROVISION_FAILED',
    'CONNECTION_LOST',
    'TIMEOUT',
    'CANCELLED',
  ]
  test.each(testData)('testing icon render', (arg) => {
    render(statusIcon(arg))
    const element = screen.getByLabelText(arg)
    expect(element).toBeInTheDocument()
  })
  test('default case', () => {
    expect(statusIcon('')).toBeNull()
  })
})

describe('testing nodeLabelIcon', () => {
  const testData = [
    'function',
    'electron_list',
    'parameter',
    'sublattice',
    'electron_dict',
    'attribute',
    'generated',
    'subscripted',
    'arg',
  ]
  test.each(testData)('testing icon render', (arg) => {
    render(nodeLabelIcon(arg))
    const element = screen.getByLabelText(arg)
    expect(element).toBeInTheDocument()
  })
  test('default case', () => {
    expect(nodeLabelIcon('')).toBeNull()
  })
})
