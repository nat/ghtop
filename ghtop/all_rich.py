from rich import print as pr
from rich.align import *
from rich.bar import *
from rich.color import *
from rich.columns import *
from rich.console import *
from rich.emoji import *
from rich.highlighter import *
from rich.live import *
from rich.logging import *
from rich.markdown import *
from rich.markup import *
from rich.measure import *
from rich.padding import *
from rich.panel import *
from rich.pretty import *
from rich.progress_bar import *
from rich.progress import *
from rich.prompt import *
from rich.protocol import *
from rich.rule import *
from rich.segment import *
from rich.spinner import *
from rich.status import *
from rich.style import *
from rich.styled import *
from rich.syntax import *
from rich.table import *
from rich.text import *
from rich.theme import *
from rich.traceback import *
from fastcore.all import *

@delegates(Style)
def text(s, maxlen=None, **kwargs):
    "Create a styled `Text` object"
    if maxlen: s = truncstr(s, maxlen=maxlen)
    return Text(s, style=Style(**kwargs))

@delegates(Style)
def segment(s, maxlen=None, space=' ', **kwargs):
    "Create a styled `Segment` object"
    if maxlen: s = truncstr(s, maxlen=maxlen, space=space)
    return Segment(s, style=Style(**kwargs))

class Segments(list):
    def __init__(self, options): self.w = options.max_width
    
    @property
    def chars(self): return sum(o.cell_length for o in self)
    def txtlen(self, pct): return min((self.w-self.chars)*pct, 999)
    
    @delegates(segment)
    def add(self, x, maxlen=None, pct=None, **kwargs):
        if pct: maxlen = math.ceil(self.txtlen(pct))
        self.append(segment(x, maxlen=maxlen, **kwargs))

@delegates(Table)
def _grid(box=None, padding=0, collapse_padding=True, pad_edge=False, expand=False, show_header=False, show_edge=False, **kwargs):
    return Table(padding=padding, pad_edge=pad_edge, expand=expand, collapse_padding=collapse_padding,
                 box=box, show_header=show_header, show_edge=show_edge, **kwargs)

@delegates(_grid)
def grid(items, expand=True, no_wrap=True, **kwargs):
    g = _grid(expand=expand, **kwargs)
    for c in items[0]: g.add_column(no_wrap=no_wrap, justify='center')
    for i in items: g.add_row(*i)
    return g

Color = str_enum('Color', *ANSI_COLOR_NAMES)

class Deque(deque):
    def __rich__(self): return RenderGroup(*(filter(None, self)))

@delegates()
class FixedPanel(Panel, GetAttr):
    _default='renderable'
    def __init__(self, height, **kwargs):
        super().__init__(Deque([' ']*height, maxlen=height), **kwargs)

@delegates(Style)
def add(self, s:str, **kwargs):
    "Add styled `s` to panel"
    self.append(text(s, **kwargs))

