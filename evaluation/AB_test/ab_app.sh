#/bin/bash

PORT=8001

export FLASK_APP=web_ui.py


echo "Please refresh the url 'localhost:$PORT' after a few seconds"
(sleep 1 && firefox localhost:$PORT) &
flask run --port $PORT
