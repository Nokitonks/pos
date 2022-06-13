from flask import Flask,request,json
import ssl

# python 3 compatible only
from http.server import BaseHTTPRequestHandler, HTTPServer
import base64
import hmac
import json

# The URL where event notifications are sent.
NOTIFICATION_URL = 'https://344d-47-144-184-29.ngrok.io'

# The event notification subscription signature key (sigKey) defined in dev portal for app.
SIG_KEY = b'-ZEXjlo1SziIT0sZ9-iTxA';

# A generic request handler to get the raw bytes of the request body.
# Different frameworks may provide the raw request body in other ways.
class MainHandler(BaseHTTPRequestHandler):
    result = None
    def do_POST(self):
        length = int(self.headers.get('content-length', 0))
        body = self.rfile.read(length)
        square_signature = self.headers.get('x-square-signature')
        event_is_from_square = self.is_from_square(SIG_KEY, NOTIFICATION_URL, square_signature, body)
        if event_is_from_square:
            self.send_response(200)
            self.server.result = body
            self.end_headers()
        else:
            self.send_response(400)
            self.end_headers()

        self.end_headers()

    # Method to generate signature from url and body and compare to square signature.
    def is_from_square(self, sig_key, notification_url, square_signature, body):
      # convert url to bytes
      url_request_bytes = notification_url.encode('utf-8') + body

      # create hmac signature
      hmac_code = hmac.new(sig_key, msg=None, digestmod='sha1')
      hmac_code.update(url_request_bytes)
      hash = hmac_code.digest()

      # compare to square signature from header
      return base64.b64encode(hash) == square_signature.encode('utf-8')
# Simple server for local testing. Run the server with python3 and send the following curl from a separate terminal:
# curl -vX POST localhost:8000 -d '{"hello":"world"}' -H "X-Square-Signature: KiPKaeNj311k3uhWDUbESP1QTRM="

def wait_for_webhook_event():
    server_address = ('0.0.0.0', 5000)
    httpd = HTTPServer(server_address, MainHandler)
    httpd.result = None
    httpd.handle_request()
    return httpd.result

