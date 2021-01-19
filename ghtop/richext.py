

__all__ = ['console', 'EProg', 'ESpark', 'SpkMap', 'Stats', 'colors', 'colors2']


import time,random
from collections import defaultdict
from typing import List
from collections import deque, OrderedDict, namedtuple
from .all_rich import (Console, Color, FixedPanel, box, Segments, Live,
                            grid, ConsoleOptions, Progress, BarColumn, Spinner)
from ghapi.event import *
from fastcore.all import *
console = Console()



class EProg:
    "Progress bar with a heading `hdg`."
    def __init__(self, hdg='Quota', width=10):
        self.prog = Progress(BarColumn(bar_width=width), "[progress.percentage]{task.percentage:>3.0f}%")
        self.task = self.prog.add_task("",total=100, visible=False)
        store_attr()
    def update(self, completed): self.prog.update(self.task, completed=completed)
    def __rich_console__(self, console: Console, options: ConsoleOptions):
        self.prog.update(self.task, visible=True)
        yield grid([["Quota"], [self.prog.get_renderable()]], width=self.width+2, expand=False)



class ESpark(EventTimer):
    "An `EventTimer` that displays a sparkline with a heading `nm`."
    def __init__(self, nm:str, color:str, ghevts=None, store=5, span=.2, mn=0, mx=None, stacked=True, show_freq=False):
        super().__init__(store=store, span=span)
        self.ghevts=L(ghevts)
        store_attr('nm,color,store,span,mn,mx,stacked,show_freq')

    def _spark(self):
        data = L(list(self.hist)+[self.freq] if self.show_freq else self.hist)
        num = f'{self.freq:.1f}' if self.freq < 10 else f'{self.freq:.0f}'
        return f"[{self.color}]{num} {sparkline(data, mn=self.mn, mx=self.mx)}[/]"

    def upd_hist(self, store, span): super().__init__(store=store, span=span)

    def _nm(self): return f"[{self.color}] {self.nm}[/]"

    def __rich_console__(self, console: Console, options: ConsoleOptions):
        yield grid([[self._nm()], [self._spark()]]) if self.stacked else f'{self._nm()}  {self._spark()}'

    def add_events(self, evts):
        evts = L([evts]) if isinstance(evts, dict) else L(evts)
        if self.ghevts: evts.map(lambda e: self.add(1) if type(e) in L(self.ghevts) else noop)
        else: self.add(len(evts))

    __repr__ = basic_repr('nm,color,ghevts,store,span,stacked,show_freq,ylim')


class SpkMap:
    "A Group of `ESpark` instances."
    def __init__(self, spks:List[ESpark]): store_attr()

    @property
    def evcounts(self): return dict([(s.nm, s.events) for s in self.spks])

    def update_params(self, store:int=None, span:float=None, stacked:bool=None, show_freq:bool=None):
        for s in self.spks:
            s.upd_hist(store=ifnone(store,s.store), span=ifnone(span,s.span))
            s.stacked = ifnone(stacked,s.stacked)
            s.show_freq = ifnone(show_freq,s.show_freq)

    def add_events(self, evts:GhEvent):
        "Update `SpkMap` sparkline historgrams with events."
        evts = L([evts]) if isinstance(evts, dict) else L(evts)
        for s in self.spks: s.add_events(evts)

    def __rich_console__(self, console: Console, options: ConsoleOptions): yield grid([self.spks])
    __repr__ = basic_repr('spks')




class Stats(SpkMap):
    "Renders a group of `ESpark` along with a spinner and progress bar that are dynamically sized."
    def __init__(self, spks:List[ESpark], store=None, span=None, stacked=None, show_freq=None, max_width=console.width-5, spin:str='earth', spn_lbl="/min"):
        super().__init__(spks)
        self.update_params(store=store, span=span, stacked=stacked, show_freq=show_freq)
        store_attr()
        self.spn = Spinner(spin)
        self.slen = len(spks) * max(15, store*2)
        self.plen = max(store, 10) # max(max_width-self.slen-15, 15)
        self.progbar = EProg(width=self.plen)

    def get_spk(self): return grid([self.spks], width=min(console.width-15, self.slen), expand=False)

    def get_spinner(self): return grid([[self.spn], [self.spn_lbl]])

    def update_prog(self, pct_complete:int=None): self.progbar.update(pct_complete) if pct_complete else noop()

    def __rich_console__(self, console: Console, options: ConsoleOptions):
        yield grid([[self.get_spinner(), self.get_spk(), grid([[self.progbar]], width=self.plen+5) ]], width=self.max_width)



@patch
def __rich_console__(self:GhEvent, console, options):
    res = Segments(options)
    kw = {'color': colors[self.type]}
    res.add(f'{self.emoji}  ')
    res.add(self.actor.login, pct=0.25, bold=True, **kw)
    res.add(self.description, pct=0.5, **kw)
    res.add(self.repo.name, pct=0.5 if self.text else 1, space = ': ' if self.text else '', italic=True, **kw)
    if self.text:
        clean_text = self.text.replace('\n', ' ').replace('\n', ' ')
        res.add (f'"{clean_text}"', pct=1, space='', **kw)
    res.add('\n')
    return res


colors = dict(
    PushEvent=None, CreateEvent=Color.red, IssueCommentEvent=Color.green, WatchEvent=Color.yellow,
    PullRequestEvent=Color.blue, PullRequestReviewEvent=Color.magenta, PullRequestReviewCommentEvent=Color.cyan,
    DeleteEvent=Color.bright_red, ForkEvent=Color.bright_green, IssuesEvent=Color.bright_magenta,
    ReleaseEvent=Color.bright_blue, MemberEvent=Color.bright_yellow, CommitCommentEvent=Color.bright_cyan,
    GollumEvent=Color.white, PublicEvent=Color.turquoise4)

colors2 = dict(
    PushEvent=None, CreateEvent=Color.dodger_blue1, IssueCommentEvent=Color.tan, WatchEvent=Color.steel_blue1,
    PullRequestEvent=Color.deep_pink1, PullRequestReviewEvent=Color.slate_blue1, PullRequestReviewCommentEvent=Color.tan,
    DeleteEvent=Color.light_pink1, ForkEvent=Color.orange1, IssuesEvent=Color.medium_violet_red,
    ReleaseEvent=Color.green1, MemberEvent=Color.orchid1, CommitCommentEvent=Color.tan,
    GollumEvent=Color.sea_green1, PublicEvent=Color.magenta2)