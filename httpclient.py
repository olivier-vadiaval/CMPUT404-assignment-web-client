#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
import time
# you may use urllib to encode data appropriately
from urllib.parse import urlparse, quote, unquote

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        return None

    def get_headers(self,data):
        return None

    def get_body(self, data):
        return None
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
                
    def close(self):
        self.socket.close()

    def request_template(self, extra_headers={}):
        now = time.strftime("%a, %d %b %Y %H:%M:%S %p %Z", time.gmtime())

        request_str = "{method} {path} HTTP/{http_ver}\r\n"
        request_str += "Host: {host}\r\n"
        request_str += "Date: {now}\r\n"
        request_str += "Accept: {accept}\r\n"
        request_str += "User-Agent: {client_name}\r\n"
        request_str += "Connection: close\r\n"
        for header_name, header in extra_headers.items():
            request_str += f"{header_name}: {header}\r\n"

        request_str += "\r\n"
        return request_str

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        code = 500
        body = ""
        parsed_url = urlparse(url)
        if args is not None:
            query_str = ""
            for key, value in args.items():
                query_str += f"{quote(key)}={quote(value)}"

            if len(parsed_url.query) == 0:
                query_str = "?" + query_str
                    
        req = self.request_template()

        req.format(
            method="GET",
            path=parsed_url.path,
            http_ver="1.1",
            host=parsed_url.netloc,
            accept="*/*",
            client_name="Mozilla 5.0",
        )

        # send request
        # read response and print

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
