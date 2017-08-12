#!/usr/bin/env python
__author_name__ = 'Ahmed Sajid'
__author_email__ = 'ahmed4343@hotmail.com'
__author__ = '{0} <{1}>'.format(__author_name__, __author_email__)
__version__ = '1.0'

import json
import sys, getopt
import csv
import json
import tempfile
import requests

def main(argv):
    input_file = ''
    global openam_url 
    try:
        opts, args = getopt.getopt(argv,"hi:u:p:l:")
    except getopt.GetoptError:
        print 'mybank_users.py -i <path to inputfile> -u <admin username> -p <admin password> -l <URL To OPENAM>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'mybank_users.py -i <path to inputfile> -u <admin username> -p <admin password> -l <URL To OPENAM>'
            sys.exit()
        elif opt in ("-i"):
            input_file = arg
        elif opt in ("-u"):
            adm_user = arg
        elif opt in ("-p"):
            adm_pass = arg
        elif opt in ("-l"):
            openam_url = arg

    get_session(adm_user,adm_pass) 
    read_csv(input_file)

#Remove empty fields in dictionary
def clean_empty(d):
    if not isinstance(d, (dict, list)):
        return d
    if isinstance(d, list):
        return [v for v in (clean_empty(v) for v in d) if v]
    return {k: v for k, v in ((k, clean_empty(v)) for k, v in d.items()) if v}

#Get Session ID
def get_session(adm_user,adm_pass):
    global session_id 
    url = openam_url + "/json/authenticate"
    headers = {'Content-Type': 'application/json','X-OpenAM-Username': adm_user,'X-OpenAM-Password': adm_pass}
    r = requests.post(url,data={},headers=headers)
    if r.status_code == 200:
        session_id = json.loads(r._content)['tokenId']
    elif r.status_code == 401:
        print "Unauthorized. Check username or password"
        sys.exit()
    else:
        print "Couldn't get session ID, return code: ",r.status_code
        sys.exit()
        
#Search User
def search_user(userdata):
    url = openam_url + "/json/users/" + userdata["username"]
    headers = {'Content-Type': 'application/json','iplanetDirectoryPro': session_id}
    r = requests.get(url,headers=headers)
    return r.status_code

#Create User
def create_user(userdata):
    url = openam_url + "/json/users/?_action=create"
    headers = {'Content-Type': 'application/json','iplanetDirectoryPro': session_id}
    r = requests.post(url,headers=headers,data=json.dumps(userdata))
    return r.status_code

#Update User
def update_user(userdata):
    url = openam_url + "/json/users/" + userdata["username"]
    headers = {'Content-Type': 'application/json','iplanetDirectoryPro': session_id}
    r = requests.put(url,headers=headers,data=json.dumps(userdata))
    return r.status_code

#Read CSV File
def read_csv(file):
    data = {}
    json_list = []
    utf8_file = tempfile.NamedTemporaryFile()
    source = open(file)
    target = open(utf8_file.name,"w")
    target.write(unicode(source.read(), "latin1").encode("utf-8"))
    target.close()
    with open(utf8_file.name) as csvfile:
        reader = csv.DictReader(csvfile)
        #title = reader.fieldnames
        for row in reader:

            json_row = json.loads(json.dumps(clean_empty(row)))
            
            # search user
            search_return_code = search_user(json_row)

            if search_return_code == 200:

                update_return_code = update_user(json_row)

                if update_return_code == 200:
                    print "Successfully Updated user: " + json_row["username"]
                else:
                    print "Couldn't update" + json_row["username"] + ". return code: ",update_return_code

            elif search_return_code == 404:

                create_return_code = create_user(json_row)

                if create_return_code == 201:
                    print "Successfully Created user: " + json_row["username"]
                else:
                    print "Couldn't create" + json_row["username"] + ". return code: ",create_return_code

            else:
                #update_user(row)
                print "Couldn't perform search. return code: ",search_return_code
                sys.exit()

if __name__ == "__main__":
   if sys.argv[1:]:
      main(sys.argv[1:])    
   else:
      print 'Usage: mybank_users.py -i <path to inputfile> -u <admin username> -p <admin password> -l <URL To OPENAM>'