#!/usr/bin/env python3

import time, datetime, pytz, sys, signal, shutil, os, json, urllib.request
import enlighten, emoji, blessed, requests, webbrowser
from dashing import *
from urllib.parse import parse_qs

term = blessed.Terminal()

logfile = "log.txt"
url = "https://api.github.com/events"

def github_auth_device():
    client_id ='a945f87ad537bfddb109'

    # Kick off the headless device auth flow on github.com
    url = 'https://github.com/login/device/code'
    response = requests.post(url, data = {'client_id': client_id, 'scope': ''})
    params = parse_qs(response.text)

    YELLOW = '\033[93m'
    END = '\033[0m'
    print ("First copy your one-time code: "  + YELLOW + params['user_code'][0] + END)

    time.sleep(1)
    input("Then, press Enter to open %s in a browser..." % (params['verification_uri'][0]))
    webbrowser.open(params['verification_uri'][0])

    print ("Waiting for authorization...", end='')

    # Poll for the user to finish the auth flow
    interval = int(params['interval'][0]) + 1
    while True:
        time.sleep(interval)
        print('.', end='')
        poll_response = requests.post('https://github.com/login/oauth/access_token',
            data = {'client_id': client_id,
                    'device_code': params['device_code'],
                    'grant_type': 'urn:ietf:params:oauth:grant-type:device_code'})
        poll_params = parse_qs(poll_response.text)
        if 'error' in poll_params:
            continue
        if 'access_token' in poll_params:
            print()
            access_token=poll_params['access_token'][0]
            print("Got access token: " + access_token)
            break

    print("Authenticated with GitHub!")
    return access_token

def get_token():

    token_path = os.path.expanduser("~/.ghtop_token")

    if os.path.isfile(token_path):
        try:
            f = open(token_path, "r")
            token = f.read().rstrip()
            f.close()
            return token
        except:
            print("Error reading token", file=sys.stderr)
            sys.exit()

    token = github_auth_device()
    f = open(token_path, "w")
    f.write(token)
    f.close()

    return token

token = get_token()

def fetch_events():
    response = requests.get(url, headers = {'Authorization': 'token ' + token})
    remaining_apis = int(response.headers['X-RateLimit-Remaining'])
    if remaining_apis < 1000:
        print("WARNING WARNING WARNING WARNING WARNING WARNING WARNING WARNING ")
        print("Remaining calls: " + str(remaining_apis))
        print("WARNING WARNING WARNING WARNING WARNING WARNING WARNING WARNING ")

    return json.loads(response.text)

def read_json_log(logfile):
    try:
        f = open(logfile, "r")
        data = f.read()
        f.close()
        return json.loads(data)
    except:
        return []

printed_event_ids = {}

def wait_for_event(created_at):
    ts = datetime.datetime.fromisoformat(created_at.replace('Z', ''))
    ts = pytz.utc.localize(ts)

    if wait_for_event.time_pointer == 0:
        wait_for_event.time_pointer = ts
    else:
        delta = ts - wait_for_event.time_pointer
        if delta.seconds > 0 and delta.seconds < 3:
            time.sleep(delta.seconds)
        wait_for_event.time_pointer = ts

wait_for_event.time_pointer = 0

def print_event(e, commits_counter):

    #wait_for_event(e['created_at'])

    if e["id"] in printed_event_ids:
        return
    printed_event_ids[e["id"]] = 1

    login = e["actor"]["login"]
    repo = e["repo"]["name"]

    #print(e["type"], login, repo)

    # Don't print bot activity (there is a lot!)
    if "bot" in login:
        return

    if e["type"] == "ReleaseEvent":
        tag = e["payload"]["release"]["tag_name"]
        print(term.firebrick3(emoji.emojize(':rocket: ') + login + " released " + tag + " of " + repo))
    elif e["type"] == "PublicEvent":
        return
    elif e["type"] == "ForkEvent":
        return
    elif e["type"] == "IssuesEvent":
        action = e["payload"]["action"]
        issue = e["payload"]["issue"]

        if action == 'closed':
            print(emoji.emojize(':star:', use_aliases=True) + ' '  + login + ' closed issue #' + str(issue["number"]) + " on repo " + repo[:22] + " (\"" +  issue["title"][:50] + "...\")")
        elif action == 'opened':
            print(emoji.emojize(':closed_mailbox_with_raised_flag:', use_aliases=True) + ' '  + login + ' opened issue #' + str(issue["number"]) + " on repo " + repo[:22] + " (\"" +  issue["title"][:50] + "...\")")

    elif e["type"] == "IssueCommentEvent":
        issue = e["payload"]["issue"]
        print(term.white(emoji.emojize(':speech_balloon: ') + login + " commented on issue #" + str(issue["number"]) + " on repo " + repo[:22] + " (\"" +  issue["title"][:50] + "...\")"))
    elif e["type"] == "PushEvent":
        commits = e["payload"]["commits"]
        for c in commits:
            commits_counter.update()
    elif e["type"] == "CreateEvent":
        return
    elif e["type"] == "PullRequestEvent":
        action = e["payload"]["action"]
        pr_emoji = ''
        pr_color = None
        if action == "closed":
            pr_emoji = emoji.emojize(":white_heavy_check_mark:")
            pr_color = term.green
        else:
            pr_emoji = emoji.emojize(":sparkles:")
            pr_color = term.yellow
        print(pr_color(pr_emoji + ' ' + login + " " + e["payload"]["action"] + " a pull request on repo " + repo[:20] + " (\"" +  e["payload"]["pull_request"]["title"][:50] + "...\")"))
        return
    elif e["type"] == "MemberEvent":
        return
    elif e["type"] == "SecurityAdvisoryEvent":
        print(term.blink("SECURITY ADVISORY"))
        return

def write_logs(events):
    f = open("tmp.log", "w")
    f.write(json.dumps(events, indent=2))
    f.close()
    shutil.move("tmp.log", logfile)

def tail_events():
    manager = enlighten.get_manager()
    commits = manager.counter(desc='Commits', unit='commits', color='green')
    while True:
        events = fetch_events()
        log = read_json_log(logfile)
        combined = log + events

        combined = sorted(combined, key=lambda x: int(x["id"]))

        write_logs(combined)
        for x in combined:
            print_event(x, commits)
        time.sleep(0.2)

EVENT_EMOJI_MAPPING = {
    'CheckRunEvent': '::',
    'CheckSuiteEvent': '::',
    'CommitCommentEvent': '::',
    'ContentReferenceEvent': '::',
    'CreateEvent': ':new:',
    'DeleteEvent': ':x:',
    'DeployKeyEvent': '::',
    'DeploymentEvent': ':rocket:',
    'DeploymentStatusEvent': '::',
    'DownloadEvent': '::',
    'FollowEvent': '::',
    'ForkEvent': ':fork_and_knife:',
    'ForkApplyEvent': '::',
    'GitHubAppAuthorizationEvent': '::',
    'GistEvent': ':notepad:',
    'GollumEvent': '::',
    'InstallationEvent': '::',
    'InstallationRepositoriesEvent': '::',
    'IssueCommentEvent': ':speech_bubble:',
    'IssuesEvent': '::',
    'LabelEvent': ':label:',
    'MarketplacePurchaseEvent': '::',
    'MemberEvent': '::',
    'MembershipEvent': '::',
    'MetaEvent': '::',
    'MilestoneEvent': '::',
    'OrganizationEvent': '::',
    'OrgBlockEvent': '::',
    'PackageEvent': '::',
    'PageBuildEvent': '::',
    'ProjectCardEvent': '::',
    'ProjectColumnEvent': '::',
    'ProjectEvent': '::',
    'PublicEvent': '::',
    'PullRequestEvent': '::',
    'PullRequestReviewEvent': '::',
    'PullRequestReviewCommentEvent': '::',
    'PushEvent': ':fist:',
    'ReleaseEvent': ':rocket:',
    'RepositoryDispatchEvent': '::',
    'RepositoryEvent': '::',
    'RepositoryImportEvent': '::',
    'RepositoryVulnerabilityAlertEvent': '::',
    'SecurityAdvisoryEvent': '::',
    'SponsorshipEvent': '::',
    'StarEvent': ':star:',
    'StatusEvent': '::',
    'TeamEvent': '::',
    'TeamAddEvent': '::',
    'WatchEvent': ':eyes:' }

def event_to_emoji(e):
    if EVENT_EMOJI_MAPPING[e["type"]] == '::':
        return e["type"]
    return emoji.emojize(EVENT_EMOJI_MAPPING[e["type"]], use_aliases=True)

def watch_users():
    users = {}
    users_events = {}
    while True:
        events = fetch_events()
        for x in events:
            login = x["actor"]["login"]
            if login in users:
                users[login] += 1
            else:
                users[login] = 1
            if login not in users_events:
                users_events[login] = {}
            if x['type'] not in users_events[login]:
                users_events[login][x['type']] = 1
            else:
                users_events[login][x['type']] += 1

        print (term.clear())
        print ("User".ljust(30), "Events".ljust(6), "PRs".ljust(5), "Issues".ljust(6), "Pushes".ljust(7))

        sorted_users = sorted(users.items(), key = lambda kv: (kv[1], kv[0]), reverse=True)
        for i in range(20):
            u = sorted_users[i]
            ue = users_events[u[0]]
            print(u[0].ljust(30), str(u[1]).ljust(6),
                (str(ue['PullRequestEvent']) if 'PullRequestEvent' in ue else '').ljust(5),
                (str(ue['IssuesEvent']) if 'IssuesEvent' in ue else '').ljust(6),
                (str(ue['PushEvent']) if 'PushEvent' in ue else '').ljust(7))
        time.sleep(1)

def push_to_log(e):
    login = e["actor"]["login"]
    repo = e["repo"]["name"]

    return "%s pushed %d commits to repo %s" % (login, len(e["payload"]["commits"]), repo)

def issue_to_log(e):

    login = e["actor"]["login"]
    repo = e["repo"]["name"]

    if e["type"] == "IssuesEvent":
        action = e["payload"]["action"]
        issue = e["payload"]["issue"]

        if action == 'closed':
            return emoji.emojize(':star:', use_aliases=True) + ' '  + login + ' closed issue #' + str(issue["number"]) + " on repo " + repo[:22] + " (\"" +  issue["title"][:50] + "...\")"
        elif action == 'opened':
            return emoji.emojize(':closed_mailbox_with_raised_flag:', use_aliases=True) + ' '  + login + ' opened issue #' + str(issue["number"]) + " on repo " + repo[:22] + " (\"" +  issue["title"][:50] + "...\")"

    elif e["type"] == "IssueCommentEvent":
        issue = e["payload"]["issue"]
        return emoji.emojize(':speech_balloon: ') + login + " commented on issue #" + str(issue["number"]) + " on repo " + repo[:22] + " (\"" +  issue["title"][:50] + "...\")"

def pr_to_log(e):
    login = e["actor"]["login"]
    repo = e["repo"]["name"]

    action = e["payload"]["action"]
    pr_emoji = ''
    pr_color = None
    if action == "closed":
        pr_emoji = emoji.emojize(":white_heavy_check_mark:")
    else:
        pr_emoji = emoji.emojize(":sparkles:")
    return pr_emoji + ' ' + login + " " + e["payload"]["action"] + " a pull request on repo " + repo[:20] + " (\"" +  e["payload"]["pull_request"]["title"][:50] + "...\")"

def release_to_log(e):
    login = e["actor"]["login"]
    repo = e["repo"]["name"]

    tag = e["payload"]["release"]["tag_name"]
    return emoji.emojize(':rocket: ') + login + " released " + tag + " of " + repo

def str_clean(s):
    return s[:95]

def signal_handler(sig, frame):
    if sig != signal.SIGINT:
        return
    term=Terminal()
    print(term.exit_fullscreen())
    print(term.clear())
    print(term.normal)
    sys.exit(0)

def quad_logs():
    term = Terminal()
    term.enter_fullscreen()

    ui = HSplit(
            VSplit(
                Log(title='Issues', border_color = 2, color=7),
                Log(title='Commits', border_color = 2, color=3)
            ),
            VSplit(
                Log(title='Pull Requests', border_color = 2, color=4),
                Log(title='Releases', border_color = 2, color=5)
            ),
        )

    issues = ui.items[0].items[0]
    commits = ui.items[0].items[1]
    prs = ui.items[1].items[0]
    releases = ui.items[1].items[1]

    issues.append(" ")
    commits.append(" ")
    prs.append(" ")
    releases.append(" ")

    while True:
        events = fetch_events()

        for x in events:
            t = x["type"]
            if t == 'PushEvent':
                commits.append(str_clean(push_to_log(x)))
            elif t == 'IssuesEvent' or t == 'IssueCommentEvent':
                issues.append(str_clean(issue_to_log(x)))
            elif t == 'PullRequestEvent':
                prs.append(str_clean(pr_to_log(x)))
            elif t == 'ReleaseEvent':
                releases.append(str_clean(release_to_log(x)))

        ui.display()
        time.sleep(0.1)

def simple():
    while True:
        events = fetch_events()
        for x in events:
            print("%s %s %s" % (x["actor"]["login"], x["type"], x["repo"]["name"]))

if len(sys.argv) < 2:
    print("Usage: ghtop <tail|quad|users|simple>")
    sys.exit(1)

signal.signal(signal.SIGINT, signal_handler)

if sys.argv[1] == 'tail':
    tail_events()
elif sys.argv[1] == 'quad':
    quad_logs()
elif sys.argv[1] == 'users':
    watch_users()
elif sys.argv[1] == 'simple':
    simple()
