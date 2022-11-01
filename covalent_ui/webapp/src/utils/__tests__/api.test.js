import axios from 'axios'
jest.mock('axios')

test('successful response', () => {
  axios.get.mockImplementation(() =>
    Promise.resolve({ status: 200, data: 'Sample' })
  )
})
