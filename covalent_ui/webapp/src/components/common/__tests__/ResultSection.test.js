import { render, screen, fireEvent } from '@testing-library/react'
import App from '../ResultSection'

describe('Result Section', () => {
  test('renders component with isFetching false', () => {
    render(
      <App
        results={{
          data: '"Hello, World!"',
          python_object:
            "import pickle\npickle.loads(b'\\x80\\x05\\x95\\x11\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x8c\\rHello, World!\\x94.')",
        }}
        isFetching={false}
      />
    )
    const headerElement = screen.getByTestId('resultSection')
    expect(headerElement).toBeInTheDocument()
    const tooltipElement = screen.getByLabelText('Copy python object')
    expect(tooltipElement).toBeInTheDocument()
  })
  test('renders component with isFetching true', () => {
    render(
      <App
        results={{
          data: '"Hello, World!"',
          python_object:
            "import pickle\npickle.loads(b'\\x80\\x05\\x95\\x11\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x8c\\rHello, World!\\x94.')",
        }}
        isFetching={true}
      />
    )
    const element = screen.getByTestId('skeleton')
    expect(element).toBeInTheDocument()
  })
  test('on clicking copy', () => {
    render(
      <App
        results={{
          data: '"Hello, World!"',
          python_object:
            "import pickle\npickle.loads(b'\\x80\\x05\\x95\\x11\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x8c\\rHello, World!\\x94.')",
        }}
        isFetching={false}
      />
    )
    const jsdomAlert = window.prompt
    window.prompt = () => {}
    const tooltipElement = screen.getByLabelText('Copy python object')
    expect(tooltipElement).toBeInTheDocument()
    fireEvent.click(tooltipElement)
    const text = screen.getByLabelText('Python object copied')
    expect(text).toBeInTheDocument()
    window.prompt = jsdomAlert
  })
})
