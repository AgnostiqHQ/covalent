# Covalent UI

## Setup

-   Activate conda environment and install required packages:

```shell
conda activate <covalent-env>
pip install -r requirement.txt
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

## Run server

```shell
cd covalent_ui
python app.py -p <port>
```

-   Open `http://localhost:<port>` in your browser.
-   Dispatch workflows to explore them in the UI.

## Frontend development

-   The optimized production build of the UI web app lives under `covalent_ui/webapp/build`. It is statically served by the server by default.

-   For the development version of the web app, see `covalent_ui/webapp/README.me`
