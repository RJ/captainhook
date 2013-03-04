#!/usr/bin/env python
import sys
import json
import getpass
import requests

hook = {
    "name": "irc",
    "active": True,
    "events": [
        "push"
    ],
    "config": {
        "branch_regexes": "",
        "nick": "github",
        "password": "",
        "long_url": "1",
        "room": "#captainhook",
        "server": "irc.example.com",
        "port": "6667"
    }
}

username = raw_input('Enter github username:')
password = getpass.getpass("Enter github.com password for '%s':" % (username,))
org = raw_input('Enter github org:')
server = raw_input("Enter irc server hostname:")
room = raw_input("Enter #channel::key or #channel:")

hook['config']['server'] = server
hook['config']['room'] = room

auth = requests.auth.HTTPBasicAuth(username, password)

doall = False
r = requests.get('https://api.github.com/orgs/%s/repos' % (org,), auth=auth)
if r.ok:
    j = json.loads(r.text or r.content)
    for org in j:
        name = org['name']
        hurl = org['hooks_url']
        print name
        ## Prompt
        if not doall:
            inp = raw_input("Add hook for %s? [Y/n/a/q] " % (name,))
            if inp == "q":
                sys.exit(0)
            if inp == "a":
                doall = True
            else:
                if not (inp == "" or inp == "y" or inp == "Y"):
                    continue
        ## Get all existing hooks
        hs = requests.get(hurl, auth=auth)
        if not r.ok:
            print " Failed: ", name
            continue
        hj = json.loads(hs.text or hs.content)
        ## Look for existing hook that matches this one
        found = False
        for h in hj:
            if h['name'] != hook['name']:
                continue
            if h['config']['room'] == hook['config']['room'] and h['config']['server'] == hook['config']['server'] and h['active']:
                found = True
                break
        ## Setup hook, if matching one not found
        if not found:
            headers = {'Content-type': 'application/json'}
            k = requests.post(hurl, auth=auth, data=json.dumps(hook), headers=headers)
            if k.ok:
                print " Set hook for ", name
            else:
                print " Failed to set hook for ", name
        else:
            print " Hook already exists for ", name
