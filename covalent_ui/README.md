# Covalent UI

## Running UI server

-   Start UI server

```shell
cd covalent_ui
flask run --port 48008
```

-   Open `http://localhost:48008` in your browser.
-   Dispatch workflows to explore them in the UI.

## Setup details

-   Ensure python environment is properly set up with all required packages installed.

```shell
conda activate <covalent-env>
pip install -r requirement.txt
```

-   The UI server does not require the **Covalent Dispatcher** to be running but it receives execution updates from it.

-   Results are currently persisted in the browser client's `localStorage`.

## Frontend development

-   The optimized production build of the UI web app lives under `covalent_ui/webapp/build`. It is statically served by the UI server by default.

-   See `covalent_ui/webapp/README.me` for details on how to build and run the development.
