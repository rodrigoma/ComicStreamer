# coding=utf-8

"""
ComicStreamer bonjour thread class
"""

"""
Copyright 2012-2014  Anthony Beville

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

	http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import threading
import select
import sys
import pybonjour
import logging

class BonjourThread(threading.Thread):
    def __init__(self, port):
        super(BonjourThread, self).__init__()
        self.name    = "ComicStreamer"
        self.regtype = "_http._tcp"
        self.port    = port
        self.daemon = True
         
    def register_callback(self, sdRef, flags, errorCode, name, regtype, domain):
        if errorCode == pybonjour.kDNSServiceErr_NoError:
            logging.info("Registered bonjour server: {0}:{1}:(port {2})".format(name,regtype,self.port))
        
    def run(self):
        sdRef = pybonjour.DNSServiceRegister(name = self.name,
                                             regtype = self.regtype,
                                             port = self.port,
                                             callBack = self.register_callback)
        try:
            try:
                while True:
                    ready = select.select([sdRef], [], [])
                    if sdRef in ready[0]:
                        pybonjour.DNSServiceProcessResult(sdRef)
            except KeyboardInterrupt:
                pass
        finally:
            sdRef.close()


#-------------------------------------------------
