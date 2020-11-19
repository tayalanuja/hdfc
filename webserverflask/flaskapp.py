from flask import Flask

app = Flask(__name__)

# from .views import *
from .interface_bs_ss import *

def runapp():
    # app.debug=True
    app.run(host='0.0.0.0', port=5005,threaded=True)

