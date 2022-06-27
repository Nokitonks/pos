from square.client import Client
from flask import Flask,request,json

import os
import uuid


class Terminal(object):

    device_id = ""
    name = ""
    code = ""
    product_type = ""
    def __init__(self,device_id):
        self.device_id = device_id

class APIRequest(object):
    access_token = ""
    client = None
    def __init__(self,access_token):
        self.access_token = access_token
        self.client = Client(
        access_token=access_token,
        environment='sandbox')


class DeviceRequest(APIRequest):

    def __init__(self,access_token):
        super(DeviceRequest,self).__init__(access_token)
   
   #returns device code dictionary with idempotency_key
    def create_device_code(self,name,product_type,location_id):
        idem_key = str(uuid.uuid4().bytes)
        body = {
        "idempotency_key": idem_key,
        "device_code": {
            "name": name,
            "product_type": product_type,
            "location_id":location_id 
            }
        }
        result = self.client.devices.create_device_code(body)
        if result.is_success():
            return idem_key,result.body
        elif result.is_error():
            return idem_key,result.errors


class TerminalRequest(APIRequest):

    def __init__(self,access_token):
        super(TerminalRequest,self).__init__(access_token)

    #Creates terminal checkout request and returns idempotency_key assoc with req
    def create_checkout(self,amount,device_id,ref_id):
        idem_key = str(uuid.uuid4().bytes)
        body = {
                "idempotency_key": idem_key,
                "checkout":{
                    "amount_money": {
                        "amount": amount,
                        "currency": "USD"
                    },
                    "device_options":{
                        "device_id": device_id,
                        "tip_settings":{
                            "allow_tipping":True    
                        }
                    },
                    "app_fee_money":{
                        "amount" :0,
                        "currency": "USD"
                    },
                    "reference_id":ref_id
                }
            }
        print(body)
        result = self.client.terminal.create_terminal_checkout(body)
        if result.is_success():
            print(result.body)
            return idem_key
        elif result.is_error():
            print(result.errors)
            return ""


def main():
    app = Flask(__name__)
    app.run(host="0.0.0.0",port=5000,debug=True)

    @app.route('/')
    def hello():
        return 'Webhooks with Python'
 

if __name__ == "__main__":
    main()





