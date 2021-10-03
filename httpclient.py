#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, https://github.com/treedust and Olivier Vadiavaloo
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

    def __str__(self):
        res_str = f"Status Code: {self.code}\r\n"
        res_str += self.body
        return res_str

class HTTPClient(object):

    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        start_line = data.split("\r\n")[0]
        try:
            split_start_line = start_line.split()
            return int(split_start_line[1])
        except:
            return -1

    def get_headers(self,data):
        headers = ""
        try:
            for line in data.split("\r\n"):
                if len(line) == 0:
                    return headers
                headers += line + "\r\n"
        except:
            return -1

    def get_body(self, data):
        try:
            splitted_data = data.split("\r\n")
        except:
            return -1

        for i in range(len(splitted_data)):
            if len(splitted_data[i]) == 0:
                return "\r\n".join(splitted_data[i+1:])
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
                
    def close(self):
        self.socket.close()

    def request_template(self, extra_headers={}):
        now = time.strftime("%a, %d %b %Y %H:%M:%S %p %Z", time.gmtime())

        request_str = "{method} {path} HTTP/{http_ver}\r\n"
        request_str += "Host: {host}\r\n"
        request_str += f"Date: {now}\r\n"
        request_str += "Accept: {accept}\r\n"
        request_str += "User-Agent: {client_name}\r\n"
        request_str += "Connection: close\r\n"
        for header_name, header in extra_headers.items():
            request_str += f"{header_name}: {header}\r\n"

        request_str += "\r\n"
        request_str += "{body}"
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

    def get_path(self, parsed_url_path):
        if parsed_url_path == "":
            return "/"
        else:
            return parsed_url_path

    def get_host_port(self, netloc):
        host_port = netloc.split(":")
        host = host_port[0]
        port = 80
        if len(host_port) == 2:
            port = int(host_port[1])

        return host, port

    def send_req(self, req, host, port):
        self.connect(host, port)

        # send request
        self.sendall(req)

        # read response and print
        res = self.recvall(self.socket)
        code = self.get_code(res)
        headers = self.get_headers(res)
        body = self.get_body(res)

        return code, headers, body

    def GET(self, url, args=None):
        code = 500
        body = ""
        parsed_url = urlparse(url)
        query_str = ""
        if args is not None:
            for key, value in args.items():
                query_str += f"{quote(key)}={quote(value)}"

            if len(parsed_url.query) == 0:
                query_str = "?" + query_str
                    
        req = self.request_template()

        req = req.format(
            method="GET",
            path=self.get_path(parsed_url.path) + query_str,
            http_ver="1.1",
            host=parsed_url.netloc,
            accept="*/*",
            client_name="Mozilla 5.0",
            body=""
        )

        # DEBUG: Print req
        # print(req)

        host, port = self.get_host_port(parsed_url.netloc)
        code, headers, body = self.send_req(req, host, port)
        
        # DEBUG: Print response headers
        # print("Response headers:\n\n" + headers)

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""

        parsed_url = urlparse(url)
        query_str = parsed_url.query
        if args is not None:
            if len(query_str) > 0:
                query_str += "&"
            
            count = 1
            for key, value in args.items():
                query_str += f"{key}={quote(value)}"
                if count < len(args):
                    query_str += "&"
                count += 1

        extra_headers = {
            "Content-Type" : "application/x-www-form-encoded",
            "Content-Length" : len(query_str)
        }
        req = self.request_template(extra_headers)

        req = req.format(
            method="POST",
            path=self.get_path(parsed_url.path),
            http_ver="1.1",
            host=parsed_url.netloc,
            accept="*/*",
            client_name="Mozilla 5.0",
            body=query_str
        )

        host, port = self.get_host_port(parsed_url.netloc)
        code, headers, body = self.send_req(req, host, port)

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
