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
        self.device_code = device_id

class APIRequest(object):
    access_token = ""
    client = None
    def __init__(self,access_token):
        self.access_token = access_token
        self.client = Client(
        access_token=access_token,
        environment='production')


class DeviceRequest(APIRequest):

    def __init__(self,access_token):
        super().__init__(access_token)
   
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

    terminal = None
    def __init__(self,access_token,terminal):
        super().init(access_token)
        self.terminal = terminal

    #Creates terminal checkout request and returns idempotency_key assoc with req
    def create_checkout(amount):
        idem_key = str(uuid.uuid4().bytes)
        body = {
                "idempotency_key": idem_key,
                "checkout":{
                    "amount_money": {
                        "amount": amount,
                        "currency": "USD"
                        },
                    "device_options":{
                        "device_id": self.terminal.device_id,
                        "skip_receipt_screen": False,
                        "tip_settings": {},
                        "show_itemized_cart": False
                        },
                    "app_free_money":{}
                    }
                }
        result = self.client.terminal.create_terminal_checkout(body)
        if result.is_success():
            print(result.body)
            return idem_key
        elif result_is_error():
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





