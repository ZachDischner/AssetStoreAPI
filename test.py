#!flask/bin/python

__author__     = 'Zach Dischner'                      
__credits__    = ["NA"]
__license__    = "NA"
__version__    = "0.0.1"
__maintainer__ = "Zach Dischner"
__email__      = "zach.dischner@gmail.com"
__status__     = "Dev"
__doc__        ="""
Basic testing script. Definitely not full coverage, but it tests isolated cases

"""

import pytest
import app
import sys
import json
import requests
from flask_httpauth import HTTPBasicAuth
auth=HTTPBasicAuth()

API_URL = "http://127.0.0.1:5000/api/v1.0"

def test_dropall(user="sudo", password="rm/*"):
    resp = requests.delete(f'{API_URL}/assets/',headers={'Content-Type': 'application/json'}, auth=(user,password) )
    assert resp.ok, f"Problem! {resp.json()}"
    return resp

def test_getall():
    resp = requests.get(f'{API_URL}/assets/',headers={'Content-Type': 'application/json'})
    assert resp.ok, f"Problem! {resp.json()}"
    return resp

def test_add_assets(num=3, user="admin", password=""):
    for num in range(num):
        resp = requests.post(f'{API_URL}/assets/sc-test-{num}',
                             headers={'Content-Type': 'application/json'},
                             json={"asset_type":"satellite", "asset_class":"dove"},
                             auth=(user, password))
        assert resp.ok, f"Problem! {resp.json()}"

        resp = requests.post(f'{API_URL}/assets/ant-test-{num}',
                             headers={'Content-Type': 'application/json'},
                             json={"asset_type": "antenna", "asset_class": "dish"},
                             auth=(user, password))
        assert resp.ok, f"Problem! {resp.json()}"
    return resp


def main():

    ## Prelim checks - reachable and empty asset datastore
    print("Making sure service is reachable and taking requests")
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


    return 0

if __name__ == "__main__":
    print("Running all test cases for AssetStore app")
    ret = main()
    sys.exit(ret)