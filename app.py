from flask import Flask
from flask.logging import create_logger
import logging


app = Flask(__name__)

app.config["DEBUG"] = True

#Logging and tracing
LOG = create_logger(app)
LOG.setLevel(logging.INFO)

#Handling globle exceptions
@app.errorhandler(Exception)
def handle_error(e):
    code = 500
    if isinstance(e, HTTPException):
        code = e.code
    return jsonify(error=str(e)), code

stores = [   {
        "name": "My Store",
        "items": [
            {
                "name": "Chair",
                "price": 15.99
            }
        ]
    }
]


# REST services
@app.get("/store")
def get_stores():
    return {"stores": stores}






#Application running

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)