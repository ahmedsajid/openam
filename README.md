# openam
OpenAM related scripts

### Requirements

* Python 2.7 (hopefully works with Python 3.x as well)

### add_users.py

Python script which loops through CSV file and creates users in OpenAM using OpenAM Restful API.

#### Usage
e.g,
```
./add_users.py -i CSVFILE -u ADMINUSER -p ADMINPASS -l OPENAMURL
```
