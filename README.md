Zach Dischner
=================================================

**April 13 2017**

**PlanetLabs Coding Challenge - RESTful web service**

## Setup

### Python
Anaconda's Python distribution is recommended for getting started. Easiest way to get started is to install and create a new Python 3.6 environment 
from the included `environment.yml` file. http://conda.pydata.org/docs/using/envs.html.

```
$ conda env create -f environment.yml
```

Otherwise, if you don't have Anaconda, a working Python 3.6+ environment with a few ancilarly modules is all you need. 
Consult `environment.yml` for a list of all modules and install however you're most comfortable.

### Clone

```
git clone git@github.com:ZachDischner/smartypy.git
```

### Start the Application
Step 1 is to startup the flask API server in a session. The app datatabase is all in-memory using native Python data structures, so no need to 
install or start a true database service. *Note* that this means that as soon as you kill the app process, the data stored for that session is 
lost. 

Just start the app:

```
python app.py
```

### Tests
Simple test cases are provided in test.py. It is a good resource for how to form requests and access the API. Consult at will

Once the server is running, you may run the following to confirm that all base test cases are passing.

```
pytest test.py
```

## Using the App 
Once started, the API can be accessed at your local URL and port: `http://127.0.0.1:5000`. 

Provided examples utilize the python `requests` library. Same results can be achieved with plain old `curl` or other similar libraries. 

**Specify Assets** with a `json` dictionary submitted in the request with `asset_type` and `asset_class` specified. For Antennas, you may also specify 
`asset_details`, which is a dictionary of information supplied about the antenna asset. Consult the prompt for allowable detail information.

```json
{
  "asset_type":"satellite", 
  "asset_class":"dove"
}
```

**Example Using Curl** instead of python's `request` library 

```bash
curl -u admin: -H "Content-Type: application/json" -X POST -d '{"asset_type":"satellite", "asset_class":"dove"}' http://127.0.0.1:5000/api/v1.0/assets/newasset
```

#### Getting Assets
GET all assets at URL: `http://127.0.0.1:5000/api/v1.0/`

GET specific asset named `assetname` at URL: `http://127.0.0.1:5000/api/v1.0/assetname`

**Filter** assets by including either the `asset_type` or `asset_class` that you want results limited to in the request JSON. Example:

```python
requests.get(f'{API_URL}/assets/',
                        headers={'Content-Type': 'application/json'},
                        json={"asset_type":"antenna"})
```

#### Adding Assets
Adding assets requires that the requestor be the `admin` user. Include that username and a blank password in the POST's `auth` info, along with 
asset JSON specifications in order to create a new Asset. 
 
 ```python
requests.post(f'{API_URL}/assets/asset-name',
                             headers={'Content-Type': 'application/json'},
                             json={"asset_type":"satellite", "asset_class":"dove"},
                             auth=("admin", ""))
```

**Antenna** type assets also allow you to specify `asset_details` as well, again included in submitted JSON data.

```python
requests.post(f'{API_URL}/assets/antenna-name',
                             headers={'Content-Type': 'application/json'},
                             json={"asset_type": "antenna", "asset_class": "dish",
                                   "asset_details":{
                                        "diameter": 200.043,
                                        "randome": True }
                                   },
                             auth=("admin", ""))
```


