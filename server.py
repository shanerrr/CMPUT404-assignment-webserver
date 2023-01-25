#  coding: utf-8
import socketserver
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos, Shane Goonasekera
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

    httpMethod = ''
    route = ''
    protocol = ''
    fileContent = ''
    statusCode = ''
    mimeType = ''
    locationHeader = ''

    def handle(self):
        self.data = self.request.recv(1024).strip().decode('utf-8')

        # get the stuff from the request
        self.httpMethod, self.route, self.protocol = self.data.splitlines()[
            0].split()

        print("Got a request of: %s\n" % self.data)

        # ignore all other http methods other than GET and send 405
        if (self.httpMethod != 'GET'):
            self.statusCode = '405 Method Not Allowed'

        else:
            # if index route / just spit out index.html page otherwise use folder structure to get other pages
            fileRoute = 'www' + self.route + \
                'index.html' if self.route[-1] == '/' else 'www' + self.route

            try:
                # check it valid file or folder and send correct status code
                pathToFile = os.getcwd() + "/www" + os.path.abspath(self.route)
                print(pathToFile)
                if (not os.path.isdir(pathToFile) and not os.path.isfile(pathToFile)):
                    self.statusCode = "404 Page Not Found"
                else:
                    self.statusCode = "200 OK"
                    self.fileContent = open(fileRoute, 'r').read()

                # grab the mime type
                self.mimeType = self._defineMimeType(fileRoute)

            except:
                if self.route[-1] != '/':
                    self.statusCode = '301 Moved Permanently'
                    self.locationHeader = 'Location: ' + self.route + '/' + '\n'
                else:
                    self.statusCode = '404 Page Not Found'

        # create response
        response = self._createResponse()

        # send the response
        self.request.sendall(bytearray(response, 'utf-8'))

    # helper function to define mimeType
    # assuming only two types being sent (.html, and .css)
    def _defineMimeType(self, fileRoute):
        if fileRoute.endswith('.html'):
            return 'Content-Type: text/html'
        elif fileRoute.endswith('.css'):
            return 'Content-Type: text/css'
        return ''

    # helper function to build response
    def _createResponse(self):
        return self.protocol + ' ' + self.statusCode + '\n' + \
            self.locationHeader + self.mimeType + '\n\n' + self.fileContent + '\n'


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
