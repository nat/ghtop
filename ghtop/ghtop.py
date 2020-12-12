__all__ = ['term', 'logfile', 'github_auth_device', 'limit_cb', 'api', 'fetch_events', 'Events', 'seen', 'print_event', 'tail_events', 'batch_events', 'watch_users', 'quad_logs', 'simple', 'main']

import time, sys, signal, shutil, os, json, enlighten, emoji, blessed
from dashing import *
from collections import defaultdict
from itertools import islice

from fastcore.utils import *
from fastcore.foundation import *
from fastcore.script import *
from ghapi.core import *

term = Terminal()
logfile = Path("log.txt")

def github_auth_device(wb='', n_polls=9999):
    "Authenticate with GitHub, polling up to `n_polls` times to wait for completion"
    auth = GhDeviceAuth()
    print(f"First copy your one-time code: {term.yellow}{auth.user_code}{term.normal}")
    print(f"Then visit {auth.verification_uri} in your browser, and paste the code when prompted.")
    if not wb: wb = input("Shall we try to open the link for you? [y/n] ")
    if wb[0].lower()=='y': auth.open_browser()

    print("Waiting for authorization...", end='')
    token = auth.wait(lambda: print('.', end=''), n_polls=n_polls)
    if not token: return print('Authentication not complete!')
    print("Authenticated with GitHub")
    return token

def _exit(msg):
    print(msg, file=sys.stderr)
    sys.exit()

def limit_cb(rem,quota):
    "Callback to warn user when close to using up hourly quota"
    w='WARNING '*7
    if rem < 1000: print(f"{w}\nRemaining calls: {rem} out of {quota}\n{w}", file=sys.stderr)

def _get_api():
    path = Path.home()/".ghtop_token"
    if path.is_file():
        try: token = path.read_text().strip()
        except: _exit("Error reading token")
    else: token = github_auth_device()
    path.write_text(token)
    return GhApi(limit_cb=limit_cb, token=token)

api = _get_api()

def fetch_events(types=None):
    "Generate an infinite stream of events optionally filtered to `types`"
    while True:
        yield from (o for o in api.activity.list_public_events() if not types or o.type in types)
        time.sleep(0.2)

Events = dict(
    IssuesEvent_closed=('⭐', 'closed', noop),
    IssuesEvent_opened=('📫', 'opened', noop),
    IssueCommentEvent=('💬', 'commented on', term.white),
    PullRequestEvent_opened=('✨', 'opened a pull request', term.yellow),
    PullRequestEvent_closed=('✔', 'closed a pull request', term.green),
)

seen = set()

def _to_log(e):
    login,repo,pay = e.actor.login,e.repo.name,e.payload
    typ = e.type + (f'_{pay.action}' if e.type in ('PullRequestEvent','IssuesEvent') else '')
    emoji,msg,color = Events.get(typ, [0]*3)
    if emoji:
        xtra = '' if e.type == "PullRequestEvent" else f' issue # {pay.issue.number}'
        d = try_attrs(pay, "pull_request", "issue")
        return color(f'{emoji} {login} {msg}{xtra} on repo {repo[:20]} ("{d.title[:50]}...")')
    elif e.type == "ReleaseEvent": return f'🚀 {login} released {e.payload.release.tag_name} of {repo}'

def print_event(e, commits_counter):
    if e.id in seen: return
    seen.add(e.id)
    login = e.actor.login
    if "bot" in login or "b0t" in login: return  # Don't print bot activity (there is a lot!)

    res = _to_log(e)
    if res: print(res)
    elif e.type == "PushEvent": [commits_counter.update() for c in e.payload.commits]
    elif e.type == "SecurityAdvisoryEvent": print(term.blink("SECURITY ADVISORY"))

def tail_events():
    "Print events from `fetch_events` along with a counter of push events"
    manager = enlighten.get_manager()
    commits = manager.counter(desc='Commits', unit='commits', color='green')
    for ev in fetch_events(): print_event(ev, commits)

def batch_events(size, types=None):
    "Generate an infinite stream of batches of events of `size` optionally filtered to `types`"
    while True: yield islice(fetch_events(types=types), size)

def _pr_row(*its): print(f"{its[0]: <30} {its[1]: <6} {its[2]: <5} {its[3]: <6} {its[4]: <7}")
def watch_users():
    "Print a table of the users with the most events"
    users,users_events = defaultdict(int),defaultdict(lambda: defaultdict(int))
    for xs in batch_events(10):
        for x in xs:
            users[x.actor.login] += 1
            users_events[x.actor.login][x.type] += 1

        print(term.clear())
        _pr_row("User", "Events", "PRs", "Issues", "Pushes")
        sorted_users = sorted(users.items(), key=lambda o: (o[1],o[0]), reverse=True)
        for u in sorted_users[:20]:
            _pr_row(*u, *itemgetter('PullRequestEvent','IssuesEvent','PushEvent')(users_events[u[0]]))

def _push_to_log(e): return f"{e.actor.login} pushed {len(e.payload.commits)} commits to repo {e.repo.name}"
def _logwin(title,color): return Log(title=title,border_color=2,color=color)

def quad_logs():
    "Print 4 panels, showing most recent issues, commits, PRs, and releases"
    term.enter_fullscreen()
    ui = HSplit(VSplit(_logwin('Issues',        color=7), _logwin('Commits' , color=3)),
                VSplit(_logwin('Pull Requests', color=4), _logwin('Releases', color=5)))

    issues,commits,prs,releases = all_items = ui.items[0].items+ui.items[1].items
    for o in all_items: o.append(" ")

    d = dict(PushEvent=commits, IssuesEvent=issues, IssueCommentEvent=issues, PullRequestEvent=prs, ReleaseEvent=releases)
    for xs in batch_events(10, types=d):
        for x in xs:
            f = [_to_log,_push_to_log][x.type == 'PushEvent']
            d[x.type].append(f(x)[:95])
        ui.display()

def simple():
    for ev in fetch_events(): print(f"{ev.actor.login} {ev.type} {ev.repo.name}")

def _signal_handler(sig, frame):
    if sig != signal.SIGINT: return
    print(term.exit_fullscreen(),term.clear(),term.normal)
    sys.exit(0)

_funcs = dict(tail=tail_events, quad=quad_logs, users=watch_users, simple=simple)
_OpModes = str_enum('_OpModes', *_funcs)

@call_parse
def main(mode: Param("Operation mode to run", _OpModes)):
    signal.signal(signal.SIGINT, _signal_handler)
    _funcs[mode]()

