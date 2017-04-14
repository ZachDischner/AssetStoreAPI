#!flask/bin/python

__author__     = 'Zach Dischner'                      
__credits__    = ["NA"]
__license__    = "NA"
__version__    = "0.0.1"
__maintainer__ = "Zach Dischner"
__email__      = "zach.dischner@gmail.com"
__status__     = "Dev"
__doc__        ="""
Basic testing script. Definitely not full coverage, but it tests the main cases. 

Also serves as a nice template for creating requests!

"""

import sys
import json
import requests
import random
from flask_httpauth import HTTPBasicAuth
auth=HTTPBasicAuth()

API_URL = "http://127.0.0.1:5000/api/v1.0"

def is_running(f, *args, **kwargs):
    def wrapped():
        try:
            requests.get(API_URL)
            return f(*args, **kwargs)
        except requests.ConnectionError:
            assert 0==1, f"{API_URL} is not reachable!"
    return wrapped

@is_running
def test_dropall(user="sudo", password="rm/*"):
    resp = requests.delete(f'{API_URL}/assets/',headers={'Content-Type': 'application/json'}, auth=(user,password) )
    assert resp.ok, f"Problem! {resp.json()}"
    return resp

@is_running
def test_getall():
    resp = requests.get(f'{API_URL}/assets/',headers={'Content-Type': 'application/json'})
    assert resp.ok, f"Problem! {resp.json()}"
    return resp

@is_running
def test_add_assets(num=10, user="admin", password=""):
    for num in range(num):
        # Add a few satellites

        resp = requests.post(f'{API_URL}/assets/sc-test-{num}',
                             headers={'Content-Type': 'application/json'},
                             json={"asset_type":"satellite", "asset_class":"dove"},
                             auth=(user, password))
        assert resp.ok, f"Problem! {resp.json()}"

        ## Now add some antennas with extra details!
        resp = requests.post(f'{API_URL}/assets/ant-test-{num}',
                             headers={'Content-Type': 'application/json'},
                             json={"asset_type": "antenna", "asset_class": "dish",
                                   "asset_details":{
                                        "diameter": random.random()*100,
                                        "randome": random.randint(0,1) }
                                   },
                             auth=(user, password))
        assert resp.ok, f"Problem! {resp.json()}"
    return resp

@is_running
def test_bad_credentials():
    resp = requests.post(f'{API_URL}/assets/sc-test-foo',
                         headers={'Content-Type': 'application/json'},
                         json={"asset_type": "satellite", "asset_class": "dove"},
                         auth=("foo_user", "foo_password"))
    assert resp.status_code == 401, f"User with wrong credentials was allowed to POST an asset! {resp.json()}"
    return resp

@is_running
def test_filtered():
    resp = requests.get(f'{API_URL}/assets/',
                        headers={'Content-Type': 'application/json'},
                        json={"asset_type":"antenna"})
    assert resp.ok, f"Problem! {resp.json()}"
    assets = resp.json()['assets']
    assert False not in ["antenna"==asset['type'] for asset in assets], f"Filtering assets for just antennas didn't work! Returned assets: {assets}"

    resp = requests.get(f'{API_URL}/assets/',
                        headers={'Content-Type': 'application/json'},
                        json={"asset_class": "dove"})
    assert resp.ok, f"Problem! {resp.json()}"
    assets = resp.json()['assets']
    assert False not in ["dove" == asset['class'] for asset in assets], f"Filtering assets for just dove types didn't work! Returned assets: {assets}"

    return resp

def main():
    print("Running all test cases for the Asset API")
    if is_running() is False:
        print(f"{API_URL} not reachable, cannot run Asset API tests")
        return -1

    ## Prelim checks - reachable and empty asset datastore
    print("Getting existing Assets")
    resp = test_getall()
    print(f"All Assets: {json.dumps(resp.json(),indent=2)}")

    print("\n\nResetting asset store database")
    resp = test_dropall()
    print(f"Response after dropping: {resp.json()}")

    print("\n\nGetting all assets")
    resp = test_getall()
    assert(len(resp.json()['assets']) == 0), f"Assets exist after being dumped! {resp.json()}"
    print(f"All Assets: {json.dumps(resp.json(),indent=2)}")


    ## Add some Assets
    print("\n\nAdding some assets")
    resp = test_add_assets()
    print(f"Response from adding the last asset : {json.dumps(resp.json(),indent=2)}")

    ## Test bad credentials
    print("\n\nTesting a user with bad credentials")
    resp = test_bad_credentials()
    print(f"Response from trying to add bad credentials : {json.dumps(resp.json(),indent=2)}")

    ## Test filtering query
    print("\n\nTesting out asset filtering query")
    resp = test_filtered()()
    print(f"Response from filtering on 'dove' type assets {json.dumps(resp.json(),indent=2)}")
    return 0

if __name__ == "__main__":
    print("Running all test cases for AssetStore app")
    ret = main()
    sys.exit(ret)