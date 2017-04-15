#!flask/bin/python

__author__     = 'Zach Dischner'                      
__credits__    = ["NA"]
__license__    = "NA"
__version__    = "0.0.1"
__maintainer__ = "Zach Dischner"
__email__      = "zach.dischner@gmail.com"
__status__     = "Dev"
__doc__        ="""
Asset Store RESTful API coding challenge for PlanetLabs.

https://gist.github.com/bcavagnolo/14a869f0e9df6f37d203cc832ec1125d

Run with:
    >> python app.py

"""

##############################################################################
#                               Imports
#----------*----------*----------*----------*----------*----------*----------*
from flask import Flask, jsonify, request, g
from flask_httpauth import HTTPBasicAuth
import json
import re

##############################################################################
#                              Data Management
#----------*----------*----------*----------*----------*----------*----------*
# Asset "database", just a list of asset dictionaries. Not super efficient for searching
# but that is okay for this demo
assets = []

def reset_asset_db():
    """Trivial"""
    global assets
    assets = []

class Asset(dict):
    """Super simple base class to form Asset objects. 

    Basic dictionary with a few constrained attributes, this class is 
    what would eventually be replaced by a proper database abstraction
    layer.
    
    It would be cool and not too difficult to make this work like SQLAlchemy and keep 
    the data store internal to this class... for another time.
    """
    ## Some Requirement Placeholders
    VALID_CLASSES = {
        "satellite": ["dove", "rapideye"],
        "antenna": ["dish", "yagi"]
        }

    REQUIRED = ["asset_name", "asset_type", "asset_class"]

    ## Pretty print representation just because
    def __repr__(self):
        return json.dumps(self, indent=2)

    @classmethod
    def validate(cls, asset_name, asset_type, asset_class, **details):
        """Validate the formation criteria for a new Asset according to project
        specs https://gist.github.com/bcavagnolo/14a869f0e9df6f37d203cc832ec1125d
        
        
        See __init__ method for argument specs
        
        Returns:
            status: Boolean indicator, are the asset formation args/kwargs valid?
            msg:    String describing success/failure
        
        Examples:
            >>>Asset.validate("test1","satellite","dove")[0]
            True
            
            >>>Asset.validate("test1","Bad","dove")[0]
            False
            
            >>>Asset.validate("test1","satellite","DOVE")[0]
            False
        """

        ## Check to make sure asset name is unique
        if asset_name in [asset["name"] for asset in assets]:
            msg = f"Integrity Error! Asset asset_named '{asset_name}' already exists!"
            return (False, msg)

        ## Check for allowable names
        if not re.findall('^[a-zA-Z0-9][a-zA-Z0-9\-\_]{3,64}$', asset_name):
            msg = f"Asset name constraints violated! Check name constraints and try again: {asset_name}"
            return (False, msg)

        ## Make sure specified type is allowed
        if asset_type not in cls.VALID_CLASSES:
            msg = f"Specified type '{asset_type}' is not recognized. Must be one of: {cls.VALID_CLASSES.keys()}"
            return (False, msg)

        ## Make sure specified type of class is allowed
        if asset_class not in cls.VALID_CLASSES[asset_type]:
            msg = f"Specified asset class '{asset_class}' is not allowable for asset type '{asset_type}'. Allowed classes: {cls.VALID_CLASSES[asset_type]}"
            return (False, msg)

        ## Verify that asset details conform to rules
        if len(details) > 0:
            # 1. Only antennas can have details
            if asset_type != "antenna":
                return (False, "Only antennas are allowed to have details")
            # 2. Antenna classes have specific constraints too
            if asset_class == "dish":
                if (len(details) > 2) or ("diameter" not in details) or ("randome" not in details):
                    return (False, f"Antenna->dish details must have a 'diameter' and 'randome' keyword. No more.  Provided {details.keys()}")
                try:
                    float(details["diameter"])
                    bool(details["randome"])
                except:
                    return (False, f"Dish details could not be converted into a float 'diameter' and boolean 'radome'. Provided {details}")
            elif asset_class == "yagi":
                if (len(details) > 1) or ("gain" not in details):
                    return (False, f"Antenna->yagi details must have a 'gain' keyword. No more.  Provided {details.keys()}")
                try:
                    float(details["gain"])
                except:
                    return (False, f"Dish details could not be converted into a float 'gain'. Provided {details}")

        return (True, "Asset specifications are valid")


    def __init__(self, asset_name, asset_type, asset_class, validate=True, **details):
        """Create a new asset instance
        
        Args:
            asset_name: String name of the new asset you want to create
            asset_type: String Type of the asset 
            asset_class: String Class of the asset type
    
        
        Kwargs:
            validate: Boolean to see if you want to validate input info prior to creation
            details: Dictionary Details corresponding to the asset
        """
        if validate:
            status, msg = self.validate(asset_name, asset_type, asset_class, **details)
            if not status:
                print(f"Invalid Asset criteria provided: {msg}")
                return

        ## Assign Asset specs
        self["name"] = asset_name
        self["type"] = asset_type
        self["class"] = asset_class

        ## Add details
        if len(details) > 0:
            self["details"] = details

##############################################################################
#                              Backend Utilities
# ----------*----------*----------*----------*----------*----------*----------*
def add_single_asset(asset_name, asset_type, asset_class, details=None):
    """Simple function to create a new Asset() and add it to the database if valid
    
    See Asset.__init__ for argument details

    Return
        passfail: (Bool) Was the addition successful?
        msg: Details about how it passed/failed
    """
    if details is None:
        details = {}
    passfail, msg =  Asset.validate(asset_name, asset_type, asset_class, **details)
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
    # Simple username password verifier
    g.current_user = username
    if username == 'admin':
        return ''
    if username == "sudo":
        return "rm/*"
    return None

#--------------------------------Error Handlers-------------------------------
@auth.error_handler
def unauthorized(msg=None):
     message = {'status':401, 'Message': 'Unauthorized access', "detail": str(msg)}
     resp = jsonify(message)
     resp.status_code = 401
     return resp

@app.errorhandler(404)
def not_found(error=None):
    message = {'status': 404, 'message':'Not Found: ' + request.url, "detail": str(error)}
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
    message = {'status': 500, 'message':'Problem occurred processing ' + request.url, "detail": str(error)}
    resp = jsonify(message)
    resp.status_code = 500
    return resp


#----------------------------------Endpoints--------------------------------

## Homepage
@app.route('/')
@app.route('/api/v1.0')
@app.route('/api/v1.0/')
def index():
    message = {'message':"Welcome to the PlanetLabs Asset Store API!",
               'ex -get all assets': "/api/v1.0/assets",
              'ex -get named asset': "/api/v1.0/assets/assetname"}
    return jsonify(message)

## All Assets
@app.route('/api/v1.0/assets', methods=['GET'])
@app.route('/api/v1.0/assets/', methods=['GET'])
def get_tasks():
    ## Check for filtering requirements
    if request.data:
        filters = request.get_json()
        if filters:
            if "asset_type" in filters:
                return jsonify({'assets': list(filter(lambda asset: asset['type']==filters["asset_type"], assets))})
            if "asset_class" in filters:
                return jsonify({'assets': list(filter(lambda asset: asset['class']==filters["asset_class"], assets))})

    ## No filters, return everything!
    return jsonify({'assets': assets})

## Delete is admin only for testing
@app.route('/api/v1.0/assets', methods=['DELETE'])
@app.route('/api/v1.0/assets/', methods=['DELETE'])
@auth.login_required
def drop_tasks():
    if g.current_user != "sudo":
        return unauthorized(msg="Only a super user can delete the database")
    reset_asset_db()
    return jsonify({'assets': assets})

## Single Asset Creation/Retrieval
@app.route('/api/v1.0/assets/<asset_name>', methods=["POST", "GET"])
@auth.login_required
def single_task(asset_name):

    ## Add a single asset to the database
    if request.method == "POST":
        asset_specs = request.get_json()
        asset_specs.update({"asset_name":asset_name})
        if False in [key in asset_specs for key in Asset.REQUIRED]:
            return malformed(f"Must provide all required Asset specifications to create a new Asset: {Asset.REQUIRED}. Missing: {set(Asset.REQUIRED) - (asset_specs.keys())}")
        passfail, msg = add_single_asset(asset_specs["asset_name"], asset_specs["asset_type"], asset_specs["asset_class"], asset_specs.get("asset_details"))
        if passfail:
            return json.dumps(msg)
        return malformed(msg)

    if request.method == "GET":
        try:
            ## Efficient so we don't have to look through whole list most of the time. Neat!
            asset = next(a for a in assets if a['name'] == asset_name)
            return json.dumps(asset)
        except StopIteration:
            return not_found(f"Asset named {asset_name} doesn't exist")


if __name__ == '__main__':
    app.run(debug=True)














