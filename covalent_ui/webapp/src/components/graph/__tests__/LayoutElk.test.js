import '@testing-library/jest-dom'
import {
  allowSublatticeAndGeneralNodes, allowPostProcessAndSubgraph,
  allowParameterAndSubgraph, allowSystemGeneratedAlone, allowSystemGenAndPostprocess,
  allowSystemGenAndParameter
} from '../../../utils/misc'

describe('testing layoutElk files', () => {
  test('allowSublatticeAndGeneralNodes returns value', () => {
    expect(allowSublatticeAndGeneralNodes()).toEqual(true)
  })
  test('allowPostProcessAndSubgraph returns value', () => {
    expect(allowPostProcessAndSubgraph()).toEqual(true)
  })
  test('allowParameterAndSubgraph returns value', () => {
    expect(allowParameterAndSubgraph()).toEqual(true)
  })
  test('allowSystemGeneratedAlone returns value', () => {
    expect(allowSystemGeneratedAlone()).toEqual(true)
  })
  test('allowSystemGenAndPostprocess returns value', () => {
    expect(allowSystemGenAndPostprocess()).toEqual(true)
  })
  test('allowSystemGenAndParameter returns value', () => {
    expect(allowSystemGenAndParameter()).toEqual(true)
  })
})
