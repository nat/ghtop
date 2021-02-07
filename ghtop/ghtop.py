

__all__ = ['get_sparklines', 'ETYPES', 'term', 'tdim', 'limit_cb', 'pct_comp', 'tail_events', 'watch_users',
           'quad_logs', 'simple', 'main']


import sys, signal, shutil, os, json
# from dashing import *
from collections import defaultdict
from warnings import warn
from itertools import islice
from fastcore.utils import *
from fastcore.foundation import *
from fastcore.script import *
from ghapi.all import *
from .richext import *
from .all_rich import (Console, Color, FixedPanel, box, Segments, Live,
                            grid, ConsoleOptions, Progress, BarColumn, Spinner, Table)



ETYPES=PushEvent,PullRequestEvent,IssuesEvent,ReleaseEvent

def get_sparklines():
    s1 = ESpark('Push', 'magenta', [PushEvent], mx=30)
    s2 = ESpark('PR', 'yellow', [PullRequestEvent, PullRequestReviewCommentEvent, PullRequestReviewEvent], mx=8)
    s3 = ESpark('Issues', 'green', [IssueCommentEvent,IssuesEvent], mx=6)
    s4 = ESpark('Releases', 'blue', [ReleaseEvent], mx=0.4)
    s5 = ESpark('All Events', 'orange', mx=45)

    return Stats([s1,s2,s3,s4,s5], store=5, span=5, spn_lbl='5/s', show_freq=True)


term = Console()

tdim = L(os.popen('stty size', 'r').read().split())
if not tdim: theight,twidth = 15,15
else: theight,twidth = tdim.map(lambda x: max(int(x)-4, 15))


def _exit(msg):
    print(msg, file=sys.stderr)
    sys.exit()


def limit_cb(rem,quota):
    "Callback to warn user when close to using up hourly quota"
    w='WARNING '*7
    if rem < 1000: print(f"{w}\nRemaining calls: {rem} out of {quota}\n{w}", file=sys.stderr)


def pct_comp(api): return int(((5000-int(api.limit_rem)) / 5000) * 100)


def tail_events(evt, api):
    "Print events from `fetch_events` along with a counter of push events"
    p = FixedPanel(theight, box=box.HORIZONTALS, title='ghtop')
    s = get_sparklines()
    g = grid([[s], [p]])
    with Live(g):
        for e in evt:
            s.add_events(e)
            s.update_prog(pct_comp(api))
            p.append(e)
            g = grid([[s], [p]])


def _user_grid():
    g = Table.grid(expand=True)
    g.add_column(justify="left")
    for i in range(4): g.add_column(justify="center")
    g.add_row("", "", "", "", "")
    g.add_row("User", "Events", "PRs", "Issues", "Pushes")
    return g


def watch_users(evts, api):
    "Print a table of the users with the most events"
    users,users_events = defaultdict(int),defaultdict(lambda: defaultdict(int))

    with Live() as live:
        s = get_sparklines()
        while True:
            for x in islice(evts, 10):
                users[x.actor.login] += 1
                users_events[x.actor.login][x.type] += 1
                s.add_events(x)

            ig = _user_grid()
            sorted_users = sorted(users.items(), key=lambda o: (o[1],o[0]), reverse=True)
            for u in sorted_users[:theight]:
                data = (*u, *itemgetter('PullRequestEvent','IssuesEvent','PushEvent')(users_events[u[0]]))
                ig.add_row(*L(data).map(str))

            s.update_prog(pct_comp(api))
            g = grid([[s], [ig]])
            live.update(g)


def _panelDict2Grid(pd):
    ispush,ispr,isiss,isrel = pd.values()
    return grid([[ispush,ispr],[isiss,isrel]], width=twidth)


def quad_logs(evts, api):
    "Print 4 panels, showing most recent issues, commits, PRs, and releases"
    pd = {o:FixedPanel(height=(theight//2)-1,
                       width=(twidth//2)-1,
                       box=box.HORIZONTALS,
                       title=camel2words(remove_suffix(o.__name__,'Event'))) for o in ETYPES}
    p = _panelDict2Grid(pd)
    s = get_sparklines()
    g = grid([[s], [p]])
    with Live(g):
        for e in evts:
            s.add_events(e)
            s.update_prog(pct_comp(api))
            typ = type(e)
            if typ in pd: pd[typ].append(e)
            p = _panelDict2Grid(pd)
            g = grid([[s], [p]])


def simple(evts, api):
    for ev in evts: print(f"{ev.actor.login} {ev.type} {ev.repo.name}")


def _get_token():
    path = Path.home()/".ghtop_token"
    if path.is_file():
        try: return path.read_text().strip()
        except: _exit("Error reading token")
    else: token = github_auth_device()
    path.write_text(token)
    return token


def _signal_handler(sig, frame):
    if sig != signal.SIGINT: return
    term.clear()
    sys.exit(0)

_funcs = dict(tail=tail_events, quad=quad_logs, users=watch_users, simple=simple)
_filts = str_enum('_filts', 'users', 'repo', 'org')
_OpModes = str_enum('_OpModes', *_funcs)

@call_parse
def main(mode:         Param("Operation mode to run", _OpModes),
         include_bots: Param("Include bots (there's a lot of them!)", store_true)=False,
         types:        Param("Comma-separated types of event to include (e.g PushEvent)", str)='',
         pause:        Param("Number of seconds to pause between requests to the GitHub api", float)=0.4,
         filt:         Param("Filtering method", _filts)=None,
         filtval:      Param("Value to filter by (for `repo` use format `owner/repo`)", str)=None):
    signal.signal(signal.SIGINT, _signal_handler)
    types = types.split(',') if types else None
    if filt and not filtval: _exit("Must pass `filter_value` if passing `filter_type`")
    if filtval and not filt: _exit("Must pass `filter_type` if passing `filter_value`")
    kwargs = {filt:filtval} if filt else {}
    api = GhApi(limit_cb=limit_cb, token=_get_token())
    evts = api.fetch_events(types=types, incl_bot=include_bots, pause=float(pause), **kwargs)
    _funcs[mode](evts, api)