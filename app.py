from flask import Flask, jsonify
from flask.logging import create_logger
from werkzeug.exceptions import HTTPException
import logging


app = Flask(__name__)

app.config["DEBUG"] = True

#Logging and tracing
LOG = create_logger(app)
LOG.setLevel(logging.INFO)


try:
    from controller.ECMRangersController import *
except Exception as e:
    print(e)

#Handling globle exceptions
@app.errorhandler(Exception)
def handle_error(e):
    print("-----Error -----",app)
    code = 500
    if isinstance(e, HTTPException):
        code = e.code
    return jsonify(error=str(e)), code

#Application running

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)