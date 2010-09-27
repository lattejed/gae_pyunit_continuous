#!/usr/bin/env python
#
# Copyright 2010 Matthew Smith.
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
DIR_PATH = '/usr/local/google_appengine'

import os, sys
import imp, unittest, time

# Set up our path similar to dev_appserver.py
EXTRA_PATHS = [
  DIR_PATH,
  os.path.join(DIR_PATH, 'lib', 'antlr3'),
  os.path.join(DIR_PATH, 'lib', 'django'),
  os.path.join(DIR_PATH, 'lib', 'ipaddr'),
  os.path.join(DIR_PATH, 'lib', 'webob'),
  os.path.join(DIR_PATH, 'lib', 'yaml', 'lib'),
  os.path.join(os.path.dirname(__file__)),
]
sys.path = EXTRA_PATHS + sys.path

# Import AE's api stubs
from google.appengine.api import apiproxy_stub_map
from google.appengine.api import datastore_file_stub
from google.appengine.api import mail_stub
from google.appengine.api import urlfetch_stub
from google.appengine.api import user_service_stub

# Set up our dummy environment
APP_ID = 'test_app'
AUTH_DOMAIN = 'gmail.com'
LOGGED_IN_USER = 't...@example.com'  # set to '' for no logged in user

os.environ['AUTH_DOMAIN'] = AUTH_DOMAIN
os.environ['USER_EMAIL'] = LOGGED_IN_USER
os.environ['APPLICATION_ID'] = APP_ID

apiproxy_stub_map.apiproxy = apiproxy_stub_map.APIProxyStubMap()
stub = datastore_file_stub.DatastoreFileStub(APP_ID, '/dev/null', '/dev/null')
apiproxy_stub_map.apiproxy.RegisterStub('datastore_v3', stub)
apiproxy_stub_map.apiproxy.RegisterStub('user', user_service_stub.UserServiceStub())
apiproxy_stub_map.apiproxy.RegisterStub('urlfetch', urlfetch_stub.URLFetchServiceStub())
apiproxy_stub_map.apiproxy.RegisterStub('mail', mail_stub.MailServiceStub())

# Watch the file given at the command line 
if __name__ == '__main__':
    old_mtime = 0
    while True:
        if len(sys.argv) == 1:
            print 'Usage: python this_file.py your_module.py'
            sys.exit()
        else:
            test = sys.argv[1].split('.')[0]
            # Load here so we can use imp.reload later
            test_mod = __import__(test)
            # TODO: update this to handle Win
            mtime = os.stat(sys.argv[1]).st_mtime
            if mtime != old_mtime:
                try:
                    old_mtime = mtime
                    # unittest loads as module is already loaded
                    # so needs to be manually reloaded each time
                    imp.reload(test_mod)
                    suite = unittest.TestSuite()
                    suite.addTests(unittest.TestLoader().loadTestsFromName(test))
                    unittest.TextTestRunner().run(suite)
                # Show any exceptions
                except Exception as e:
                    print str(type(e)), e
            time.sleep(1)
