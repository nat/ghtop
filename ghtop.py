#!/usr/bin/python

import time
import json
import sys
import shutil
from urllib2 import urlopen, Request

logfile = "log.txt"
url = "https://api.github.com/events"

def get_token():
    f = open("ghtoken.txt", "r")
    token = f.read()
    return token

def fetch_events():
    request = Request(url)
    request.add_header('Authorization', 'token %s' % get_token())
    response = urlopen(request)
    remaining_apis = int(response.headers['X-RateLimit-Remaining'])
    if remaining_apis < 1000:
        print "WARNING WARNING WARNING WARNING WARNING WARNING WARNING WARNING "
        print "Remaining calls: " + str(remaining_apis)
        print "WARNING WARNING WARNING WARNING WARNING WARNING WARNING WARNING "
    data = response.read()

    return json.loads(data)

def read_json_log(logfile):
    try:
        f = open(logfile, "r")
        data = f.read()
        f.close()
        return json.loads(data)
    except:
        return []

ansi_colors = [
    "\033[0;31m", # red
    "\033[0;32m", # green
    "\033[0;33m", # yellow
    "\033[0;34m", # blue
    "\033[0;35m", # purple
    "\033[0;36m", # cyan
    "\033[0;37m", # light gray
    "\033[1;30m", # dark gray
    "\033[1;31m", # light red
    "\033[1;32m", # light green
    "\033[1;33m", # light yellow
    "\033[1;34m", # light blue
    "\033[1;35m", # light purple
    "\033[1;36m", # light cyan
    "\033[1;37m" # light white
]

printed_event_ids = {}

def print_event(e):
    #print ansi_colors[hash(e["type"]) % len(ansi_colors)]

    #print e["type"]
    if e["id"] in printed_event_ids:
        return
    printed_event_ids[e["id"]] = 1

    login = e["actor"]["login"]
    repo = e["repo"]["name"][:15]

    if "bot" in login:
        return

    if e["type"] == "ReleaseEvent":
        tag = e["payload"]["release"]["tag_name"]
        print login + " released " + tag + " of " + repo
    elif e["type"] == "PublicEvent":
        return
    elif e["type"] == "ForkEvent":
        return
    elif e["type"] == "IssueEvent":
        return
    elif e["type"] == "IssueCommentEvent":
        issue = e["payload"]["issue"]
        print login + " commented on issue #" + str(issue["number"]) + " on repo " + repo[:22] + " (\"" +  issue["title"][:50] + "...\")"
#        print json.dumps(e, indent=2)
    elif e["type"] == "PushEvent":
        commits = e["payload"]["commits"]
        return
        sys.stdout.write(".")
        if len(commits) > 1:
            print login + " pushed " + str(len(commits)) + " commits to " + repo
        elif len(commits) > 0:
            print login + " pushed a commit to " + repo
    elif e["type"] == "CreateEvent":
        return
    elif e["type"] == "PullRequestEvent":
        print login + " " + e["payload"]["action"] + " a pull request on repo " + repo[:20] + " (\"" +  e["payload"]["pull_request"]["title"][:50] + "...\")"
        return
    elif e["type"] == "MemberEvent":
        return
       
def write_logs(events):
    f = open("tmp.log", "w")
    f.write(json.dumps(events, indent=2))
    f.close()
    shutil.move("tmp.log", logfile)

while True:
    events = fetch_events()
    log = read_json_log(logfile)
    combined = log + events
    write_logs(combined)
    for x in combined:
        print_event(x)
    time.sleep(1)
    