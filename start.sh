#lsof -i tcp:5000
gunicorn -t 30 -w 1 -b 0.0.0.0:5000 \
    --chdir /Users/alejandroesquivel/Documents/agnostiq/covalent/covalent_dispatcher/_cli/../../covalent_ui \
    --pid /Users/alejandroesquivel/.cache/covalent/ui.pid \
    --reuse-port app:app \
    --log-level debug
