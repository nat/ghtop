#!/usr/bin/python
 
import urllib
import json

endpoint = 'https://api.github.com/events'

f = urllib.urlopen(endpoint)
data = f.readline()  

parsed = json.loads(data)

for x in parsed:
    if x["type"] == "PushEvent":
        repo = x["repo"]["name"]
        # print(json.dumps(x, indent=2, sort_keys=True))
        for c in x["payload"]["commits"]:
            print repo[:19].ljust(20) + '\t' + c["message"][:60]
