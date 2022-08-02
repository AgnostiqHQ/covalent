# Covalent UI

## Setup

-   Clone the repo
-   Install the dependencies

```shell
cd /covalent
pip install -e .
```

-   Install `node` (v16 or later) and `npm`:

```shell
# Linux
curl -sL https://deb.nodesource.com/setup_16.x | bash -
apt-get install -y nodejs

# macOS
brew install node
```

-   Install `yarn`:

```shell
npm install --global yarn
```

## Build web app

```
cd covalent_ui/webapp
yarn install
yarn build
```

## Run web app

```shell
yarn start
```
## Run server
Recomended python version is 3.8
```shell
cd covalent_ui
python app.py
```

-   Open `http://localhost:<port>` in your browser.
-   Dispatch workflows to explore them in the UI.

## Frontend development

-   The optimized production build of the UI web app lives under `covalent_ui/webapp/build`. It is statically served by the server by default.

-   For the development version of the web app, see `covalent_ui/webapp/README.me`
