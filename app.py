#!flask/bin/python



__author__     = 'Zach Dischner'                      
__credits__    = ["NA"]
__license__    = "NA"
__version__    = "0.0.1"
__maintainer__ = "Zach Dischner"
__email__      = "zach.dischner@gmail.com"
__status__     = "Dev"
__doc__        ="""
Asset RESTful API coding challenge for PlanetLabs.

https://gist.github.com/bcavagnolo/14a869f0e9df6f37d203cc832ec1125d

"""

##############################################################################
#                               Imports
#----------*----------*----------*----------*----------*----------*----------*
from flask import Flask, abort, jsonify, request, g
from flask_httpauth import HTTPBasicAuth
from collections import OrderedDict
import json
import sys
import traceback

##############################################################################
#                              Data Management
#----------*----------*----------*----------*----------*----------*----------*
# Asset "database", just a list of asset dictionaries. Not super efficient for searching
# but that is okay for this demo
assets = [
    {
        'name': 'test1',
        'type': 'satellite',
        'class': 'dove'
    },
    {
        'name': 'test2',
        'type': 'antenna',
        'class': 'dish'
    },
]

def reset_asset_db():
    """Trivial"""
    global assets
    assets = []
    Asset.NAMES = []

class Asset(dict):
    """Super simple base class to form Asset objects. 

    Basic dictionary with a few constrained attributes, this class is 
    what would eventually be replaced by a proper database abstraction
    layer
    """
    ## List of asset names already created, helps verify uniqueness
    NAMES = []

    ## Some Requirement Placeholders
    VALID_CLASSES = {
        "satellite": ["dove", "rapideye"],
        "antenna": ["dish", "yagi"]
        }

    REQUIRED = ["asset_name", "asset_type", "asset_class"]

    def __repr__(self):
        return json.dumps(self, indent=2)

    @classmethod
    def validate(cls, asset_name, asset_type, asset_class, **details):
        if asset_name in cls.NAMES:
            msg = f"PROBREM! Asset asset_named '{asset_name}' already exists!"
            # abort(400)
            return (False, msg)
        ## Regex the asset_name

        if asset_type not in cls.VALID_CLASSES:
            msg = f"Specified type '{asset_type}' is not recognized. Must be one of: {cls.VALID_CLASSES.keys()}"
            return (False, msg)

        if asset_class not in cls.VALID_CLASSES[asset_type]:
            msg = f"Specified asset class '{asset_class}' is not allowable for asset type '{asset_type}'. Allowed classes: {cls.VALID_CLASSES[asset_type]}"
            return (False, msg)

        if len(details) > 0:
            print("Have details!")
        return (True, "Asset specifications are valid")


    def __init__(self, asset_name, asset_type, asset_class, **details):

        self.NAMES.append(asset_name)

        ## Assign Asset specs
        self["name"] = asset_name
        self["type"] = asset_type
        self["class"] = asset_class

        ## Add details
        self.update(details)

##############################################################################
#                              Backend Utilities
# ----------*----------*----------*----------*----------*----------*----------*
def add_single_asset(asset_name, asset_type, asset_class, **details):
    passfail, msg =  Asset.validate(asset_name, asset_type, asset_class)
    if not passfail:
        msg = f"Unable to add new asset: {msg}"
    else:
        asset = Asset(asset_name, asset_type, asset_class, **details)
        assets.append(asset)
        msg = f"Successfully added Asset to datastore {asset}"
    return passfail, msg


##############################################################################
#                                API Application
#----------*----------*----------*----------*----------*----------*----------*
app = Flask(__name__)

#--------------------------------Authentication-------------------------------
auth = HTTPBasicAuth()

@auth.get_password
def get_password(username):
    g.current_user = username
    print(f"Username is '{username}'")
    if username == 'admin':
        return ''
    if username == "sudo":
        return "rm/*"
    return None


@auth.error_handler
def unauthorized(msg=None):
     message = {'status':401, 'Message': 'Unauthorized access', "detail": msg}
     resp = jsonify(message)
     resp.status_code = 401
     return resp

#--------------------------------Error Handlers-------------------------------
@app.errorhandler(404)
def not_found(error=None):
    message = {'status': 404, 'message':'Not Found: ' + request.url, "detail": error}
    resp = jsonify(message)
    resp.status_code = 404
    return resp

@app.errorhandler(400)
def malformed(error=None):
    message = {'status': 400, 'message':'Malformed Argument: ' + request.url, "detail":str(error)}
    resp = jsonify(message)
    resp.status_code = 400
    return resp

@app.errorhandler(500)
def internal_error(error=None):
    message = {'status': 500, 'message':'Problem occurred processing ' + request.url, "detail": error}
    resp = jsonify(message)
    resp.status_code = 500
    return resp


#----------------------------------Endpoints--------------------------------

@app.route('/')
def index():
    message = {'message':"Welcome to the PlanetLabs Asset Store API!"} 
    return jsonify(message)

@app.route('/api/v1.0/assets', methods=['GET'])
@app.route('/api/v1.0/assets/', methods=['GET'])
def get_tasks():
    return jsonify({'assets': assets})

## Delete is admin only for testing
@app.route('/api/v1.0/assets', methods=['DELETE'])
@app.route('/api/v1.0/assets/', methods=['DELETE'])
@auth.login_required
def drop_tasks():
    print(f"User: {g.current_user}")
    if g.current_user != "sudo":
        return unauthorized(msg="Only a super user can delete the database")
    reset_asset_db()
    return jsonify({'assets': assets})

@app.route('/api/v1.0/assets/<asset_name>', methods=["POST", "GET"])
@auth.login_required
def single_task(asset_name):

    ## Add a single asset to the database
    if request.method == "POST":
        print("Post data: ", str(request.get_json()))
        asset_specs = request.get_json()
        asset_specs.update({"asset_name":asset_name})
        print("Decoded")
        if False in [key in asset_specs for key in Asset.REQUIRED]:
            return malformed(f"Must provide all required Asset specifications to create a new Asset: {Asset.REQUIRED}. Missing: {set(Asset.REQUIRED) - (asset_specs.keys())}")
        passfail, msg = add_single_asset(asset_specs["asset_name"], asset_specs["asset_type"], asset_specs["asset_class"])
        if passfail:
            return json.dumps(msg)
        return malformed(msg)

    if request.method == "GET":
        try:
            asset = next(a for a in assets if a['name'] == asset_name)
            return json.dumps(asset)
        except StopIteration:
            return not_found(f"Asset named {asset_name} doesn't exist")


if __name__ == '__main__':
    app.run(debug=True)














