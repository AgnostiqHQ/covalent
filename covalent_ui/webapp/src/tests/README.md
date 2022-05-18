# Running tests

- quick commands
  ```
  # run in watch mode
  yarn test

  # turn off watch mode
  yarn test --watchAll=false

  # run a single test file
  yarn test tests/dashboard.test.js

  # coverage
  yarn test --coverage
  ```

- Based on Create React App testing defaults
  - See details here: https://create-react-app.dev/docs/running-tests/
  - see `src/setupTests.js`

- Config
  - see `jest` top-level key inside `package.json`
  - https://create-react-app.dev/docs/running-tests/#configuration

# Testing libraries used

- Jest - base JavaScript testing framework
  - https://jestjs.io/docs/getting-started
  - https://jestjs.io/docs/api

- React Testing Library - React-specific companion library.
  - Setup: https://testing-library.com/docs/react-testing-library/setup/
  - API: https://testing-library.com/docs/react-testing-library/api

- Mock Service Worker - intercept requests on network level to mock all API services.
  - see https://mswjs.io/docs/#request-flow-diagram
  - see setup: `src/setupTests.js`
