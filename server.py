#  coding: utf-8 
import socketserver
import os
from enum import Enum

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
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
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    class ContentType(Enum):
        HTML = 1
        CSS = 2
        UNKNOWN = 3

    def setup(self):
        self.default_file_path = "www"

    def handle(self):
        self.data = self.request.recv(1024).decode().strip()
        # print ("Got a request of: %s\n" % self.data)

        if "GET" in self.data:
            response = self.handle_get()
        else:
            response = self.build_response("Method Not Allowed", status_code=405)

        self.request.sendall(response.encode())

    def handle_get(self):
        path_requested = self.data.split()[1]
        path = self.obtain_requested_file_path(path_requested)
        content_type = self.get_content_type(path)
        # print("Path:", path, "\r\n")

        if content_type != MyWebServer.ContentType.UNKNOWN:
            try:
                with open(path, "r") as f:
                    content = f.read()
                return self.build_response(content, content_type=content_type)
            except FileNotFoundError:
                return self.build_response("Not Found", status_code=404)
        else:
            # path requested could be a directory as it does not end with "/"
            if os.path.isdir(path):
                # redirect user
                return self.build_response("Not Found", status_code=301, redirect_path=f'{path_requested}/')
            else:
                return self.build_response("Not Found", status_code=404)


    def build_response(self, content, content_type=ContentType.UNKNOWN, status_code=200, redirect_path="/"):
        if status_code == 200:
            status = "200 OK"
        elif status_code == 301:
            status = "301 MOVED"
        elif status_code == 404:
            status = "404 NOT FOUND"
        elif status_code == 405:
            status = "405 METHOD NOT ALLOWED"
        else:
            status = f'{status_code} UNKNOWN STATUS'
        response = f'HTTP/1.1 {status}\n'

        if status_code == 301:
            response += f'Location: {redirect_path}\n'
            return response

        if content_type == MyWebServer.ContentType.HTML:
            response += "Content-Type: text/html; charset=utf-8\n"
        elif content_type == MyWebServer.ContentType.CSS:
            response += "Content-Type: text/css; charset=utf-8\n"

        response += f'\n{content}'
        return response
    
    def get_sanitized_path(self, path_requested):
        return path_requested.strip("/").strip("../")

    def obtain_requested_file_path(self, path_requested):
        if path_requested.endswith("/"):
            return os.path.join(self.default_file_path, self.get_sanitized_path(path_requested), "index.html")
        else:
            return os.path.join(self.default_file_path, self.get_sanitized_path(path_requested))

    def get_content_type(self, path):
        if path.endswith(".html"):
            return MyWebServer.ContentType.HTML
        elif path.endswith(".css"):
            return MyWebServer.ContentType.CSS
        return MyWebServer.ContentType.UNKNOWN


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)  # makes an instance of MyWebServer for each new tcp connection

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
