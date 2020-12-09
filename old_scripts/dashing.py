# -*- coding: utf-8 -*-
#

from collections import deque, namedtuple

from blessed import Terminal

try:
    unichr
except NameError:
    unichr = chr

# "graphic" elements

border_bl = u'└'
border_br = u'┘'
border_tl = u'┌'
border_tr = u'┐'
border_h = u'─'
border_v = u'│'
hbar_elements = (u"▏", u"▎", u"▍", u"▌", u"▋", u"▊", u"▉")
vbar_elements = (u"▁", u"▂", u"▃", u"▄", u"▅", u"▆", u"▇", u"█")
braille_left = (0x01, 0x02, 0x04, 0x40, 0)
braille_right = (0x08, 0x10, 0x20, 0x80, 0)
braille_r_left = (0x04, 0x02, 0x01)
braille_r_right = (0x20, 0x10, 0x08)

TBox = namedtuple('TBox', 't x y w h')


class Tile(object):
    def __init__(self, title=None, border_color=None, color=0):
        self.title = title
        self.color = color
        self.border_color = border_color

    def _display(self, tbox, parent):
        """Render current tile
        """
        raise NotImplementedError

    def _draw_borders(self, tbox):
        # top border
        print(tbox.t.color(self.border_color) + tbox.t.move(tbox.x, tbox.y) +
              border_tl + border_h * (tbox.w - 2) + border_tr)
        # left and right
        for dx in range(1, tbox.h - 1):
            print(tbox.t.move(tbox.x + dx, tbox.y) + border_v)
            print(tbox.t.move(tbox.x + dx, tbox.y + tbox.w - 1) + border_v)
        # bottom
        print(tbox.t.move(tbox.x + tbox.h - 1, tbox.y) + border_bl +
              border_h * (tbox.w - 2) + border_br)

    def _draw_borders_and_title(self, tbox):
        """Draw borders and title as needed and returns
        inset (x, y, width, height)
        """
        if self.border_color is not None:
            self._draw_borders(tbox)
        if self.title:
            fill_all_width = (self.border_color is None)
            self._draw_title(tbox, fill_all_width)

        if self.border_color is not None:
            return TBox(tbox.t, tbox.x + 1, tbox.y + 1, tbox.w - 2, tbox.h - 2)

        elif self.title is not None:
            return TBox(tbox.t, tbox.x + 1, tbox.y, tbox.w - 1, tbox.h - 1)

        return TBox(tbox.t, tbox.x, tbox.y, tbox.w, tbox.h)

    def _fill_area(self, tbox, char, *a, **kw):  # FIXME
        """Fill area with a character
        """
        # for dx in range(0, height):
        #    print(tbox.t.move(x + dx, tbox.y) + char * width)
        pass

    def display(self):
        """Render current tile and its items. Recurse into nested splits
        if any.
        """
        try:
            t = self._terminal
        except AttributeError:
            t = self._terminal = Terminal()
            tbox = TBox(t, 0, 0, t.width, t.height - 1)
            self._fill_area(tbox.t, 0, 0, t.width, t.height - 1, 'f')  # FIXME

        tbox = TBox(t, 0, 0, t.width, t.height - 1)
        self._display(tbox, None)
        # park cursor in a safe place and reset color
        print(t.move(t.height - 3, 0) + t.color(0))

    def _draw_title(self, tbox, fill_all_width):
        if not self.title:
            return
        margin = int((tbox.w - len(self.title)) / 20)
        col = '' if self.border_color is None else \
            tbox.t.color(self.border_color)
        if fill_all_width:
            title = ' ' * margin + self.title + \
                ' ' * (tbox.w - margin - len(self.title))
            print(tbox.t.move(tbox.x, tbox.y) + col + title)
        else:
            title = ' ' * margin + self.title + ' ' * margin
            print(tbox.t.move(tbox.x, tbox.y + margin) + col + title)


class Split(Tile):
    def __init__(self, *items, **kw):
        super(Split, self).__init__(**kw)
        self.items = items

    def _display(self, tbox, parent):
        """Render current tile and its items. Recurse into nested splits
        """
        tbox = self._draw_borders_and_title(tbox)

        if not self.items:
            # empty split
            self._fill_area(tbox, ' ')
            return

        if isinstance(self, VSplit):
            item_height = tbox.h // len(self.items)
            item_width = tbox.w
        else:
            item_height = tbox.h
            item_width = tbox.w // len(self.items)

        x = tbox.x
        y = tbox.y
        for i in self.items:
            i._display(TBox(tbox.t, x, y, item_width, item_height),
                       self)
            if isinstance(self, VSplit):
                x += item_height
            else:
                y += item_width

        # Fill leftover area
        if isinstance(self, VSplit):
            leftover_x = tbox.h - x + 1
            if leftover_x > 0:
                self._fill_area(TBox(tbox.t, x, y, tbox.w, leftover_x), ' ')
        else:
            leftover_y = tbox.w - y + 1
            if leftover_y > 0:
                self._fill_area(TBox(tbox.t, x, y, leftover_y, tbox.h), ' ')


class VSplit(Split):
    pass


class HSplit(Split):
    pass


class Text(Tile):
    def __init__(self, text, color=0, *args, **kw):
        super(Text, self).__init__(**kw)
        self.text = text
        self.color = color

    def _display(self, tbox, parent):
        tbox = self._draw_borders_and_title(tbox)
        for dx, line in enumerate(self.text.splitlines()):
            print(tbox.t.color(self.color) + tbox.t.move(tbox.x + dx, tbox.y) +
                  line + ' ' * (tbox.w - len(line)))
        dx += 1
        while dx < tbox.h:
            print(tbox.t.move(tbox.x + dx, tbox.y) + ' ' * tbox.w)
            dx += 1


class Log(Tile):
    def __init__(self, *args, **kw):
        self.logs = deque(maxlen=50)
        super(Log, self).__init__(**kw)

    def _display(self, tbox, parent):
        tbox = self._draw_borders_and_title(tbox)
        n_logs = len(self.logs)
        log_range = min(n_logs, tbox.h)
        start = n_logs - log_range
        print(tbox.t.color(self.color))
        for i in range(0, log_range):
            line = self.logs[start + i]
            print(tbox.t.move(tbox.x + i, tbox.y) + line +
                  ' ' * (tbox.w - len(line)))

        if i < tbox.h:
            for i2 in range(i + 1, tbox.h):
                print(tbox.t.move(tbox.x + i2, tbox.y) + ' ' * tbox.w)

    def append(self, msg):
        self.logs.append(msg)


class HGauge(Tile):
    def __init__(self, label=None, val=100, color=2, **kw):
        kw['color'] = color
        super(HGauge, self).__init__(**kw)
        self.value = val
        self.label = label

    def _display(self, tbox, parent):
        tbox = self._draw_borders_and_title(tbox)
        if self.label:
            wi = (tbox.w - len(self.label) - 3) * self.value / 100
            v_center = int((tbox.h) * 0.5)
        else:
            wi = tbox.w * self.value / 100.0
        index = int((wi - int(wi)) * 7)
        bar = hbar_elements[-1] * int(wi) + hbar_elements[index]
        print(tbox.t.color(self.color) + tbox.t.move(tbox.x, tbox.y + 1))
        if self.label:
            pad = tbox.w - 1 - len(self.label) - len(bar)
        else:
            pad = tbox.w - len(bar)
        bar += hbar_elements[0] * pad
        # draw bar
        for dx in range(0, tbox.h):
            m = tbox.t.move(tbox.x + dx, tbox.y)
            if self.label:
                if dx == v_center:
                    # draw label
                    print(m + self.label + ' ' + bar)
                else:
                    print(m + ' ' * len(self.label) + ' ' + bar)
            else:
                print(m + bar)


class VGauge(Tile):
    def __init__(self, val=100, color=2, **kw):
        kw['color'] = color
        super(VGauge, self).__init__(**kw)
        self.value = val

    def _display(self, tbox, parent):
        """Render current tile
        """
        tbox = self._draw_borders_and_title(tbox)
        nh = tbox.h * (self.value / 100.5)
        print(tbox.t.move(tbox.x, tbox.y) + tbox.t.color(self.color))
        for dx in range(tbox.h):
            m = tbox.t.move(tbox.x + tbox.h - dx - 1, tbox.y)
            if dx < int(nh):
                bar = vbar_elements[-1] * tbox.w
            elif dx == int(nh):
                index = int((nh - int(nh)) * 8)
                bar = vbar_elements[index] * tbox.w
            else:
                bar = ' ' * tbox.w

            print(m + bar)


class ColorRangeVGauge(Tile):
    """Vertical gauge with color map.
    E.g.: green gauge for values below 50, red otherwise:
    colormap=((50, 2), (100, 1))
    """
    def __init__(self, val=100, colormap=(), **kw):
        self.colormap = colormap
        super(ColorRangeVGauge, self).__init__(**kw)
        self.value = val

    def _display(self, tbox, parent):
        tbox = self._draw_borders_and_title(tbox)
        nh = tbox.h * (self.value / 100.5)
        filled_element = vbar_elements[-1]
        for thresh, col in self.colormap:
            if thresh > self.value:
                break
        print(tbox.t.move(tbox.x, tbox.y) + tbox.t.color(col))
        for dx in range(tbox.h):
            m = tbox.t.move(tbox.x + tbox.h - dx - 1, tbox.y)
            if dx < int(nh):
                bar = filled_element * tbox.w
            elif dx == int(nh):
                index = int((nh - int(nh)) * 8)
                bar = vbar_elements[index] * tbox.w
            else:
                bar = ' ' * tbox.w

            print(m + bar)


class VChart(Tile):
    """Vertical chart. Values must be between 0 and 100 and can be float.
    """
    def __init__(self, val=100, *args, **kw):
        super(VChart, self).__init__(**kw)
        self.value = val
        self.datapoints = deque(maxlen=50)

    def append(self, dp):
        self.datapoints.append(dp)

    def _display(self, tbox, parent):
        tbox = self._draw_borders_and_title(tbox)
        filled_element = hbar_elements[-1]
        scale = tbox.w / 100.0
        print(tbox.t.color(self.color))
        for dx in range(tbox.h):
            index = 50 - (tbox.h) + dx
            try:
                dp = self.datapoints[index] * scale
                index = int((dp - int(dp)) * 8)
                bar = filled_element * int(dp) + hbar_elements[index]
                assert len(bar) <= tbox.w, dp
                bar += ' ' * (tbox.w - len(bar))
            except IndexError:
                bar = ' ' * tbox.w
            print(tbox.t.move(tbox.x + dx, tbox.y) + bar)


class HChart(Tile):
    """Horizontal chart, filled
    """
    def __init__(self, val=100, *args, **kw):
        super(HChart, self).__init__(**kw)
        self.value = val
        self.datapoints = deque(maxlen=500)

    def append(self, dp):
        self.datapoints.append(dp)

    def _display(self, tbox, parent):
        tbox = self._draw_borders_and_title(tbox)
        print(tbox.t.color(self.color))
        for dx in range(tbox.h):
            bar = ''
            for dy in range(tbox.w):
                dp_index = - tbox.w + dy
                try:
                    dp = self.datapoints[dp_index]
                    q = (1 - dp / 100) * tbox.h
                    if dx == int(q):
                        index = int((int(q) - q) * 8 - 1)
                        bar += vbar_elements[index]
                    elif dx < int(q):
                        bar += ' '
                    else:
                        bar += vbar_elements[-1]

                except IndexError:
                    bar += ' '

            # assert len(bar) == tbox.w
            print(tbox.t.move(tbox.x + dx, tbox.y) + bar)


class HBrailleChart(Tile):
    def __init__(self, val=100, *args, **kw):
        super(HBrailleChart, self).__init__(**kw)
        self.value = val
        self.datapoints = deque(maxlen=500)

    def append(self, dp):
        self.datapoints.append(dp)

    def _generate_braille(self, l, r):
        v = 0x28 * 256 + (braille_left[l] + braille_right[r])
        return unichr(v)

    def _display(self, tbox, parent):
        tbox = self._draw_borders_and_title(tbox)
        print(tbox.t.color(self.color))
        for dx in range(tbox.h):
            bar = ''
            for dy in range(tbox.w):
                dp_index = (dy - tbox.w) * 2
                try:
                    dp1 = self.datapoints[dp_index]
                    dp2 = self.datapoints[dp_index + 1]
                except IndexError:
                    # no data (yet)
                    bar += ' '
                    continue

                q1 = (1 - dp1 / 100) * tbox.h
                q2 = (1 - dp2 / 100) * tbox.h
                if dx == int(q1):
                    index1 = int((q1 - int(q1)) * 4)
                    if dx == int(q2):  # both datapoints in the same rune
                        index2 = int((q2 - int(q2)) * 4)
                    else:
                        index2 = -1  # no dot
                    bar += self._generate_braille(index1, index2)
                elif dx == int(q2):
                    # the right dot only is in the current rune
                    index2 = int((q2 - int(q2)) * 4)
                    bar += self._generate_braille(-1, index2)
                else:
                    bar += ' '

            print(tbox.t.move(tbox.x + dx, tbox.y) + bar)


class HBrailleFilledChart(Tile):
    def __init__(self, val=100, *args, **kw):
        super(HBrailleFilledChart, self).__init__(**kw)
        self.value = val
        self.datapoints = deque(maxlen=500)

    def append(self, dp):
        self.datapoints.append(dp)

    def _generate_braille(self, lmax, rmax):
        v = 0x28 * 256
        for l in range(lmax):
            v += braille_r_left[l]
        for r in range(rmax):
            v += braille_r_right[r]
        return unichr(v)

    def _display(self, tbox, parent):
        tbox = self._draw_borders_and_title(tbox)
        print(tbox.t.color(self.color))
        for dx in range(tbox.h):
            bar = ''
            for dy in range(tbox.w):
                dp_index = (dy - tbox.w) * 2
                try:
                    dp1 = self.datapoints[dp_index]
                    dp2 = self.datapoints[dp_index + 1]
                except IndexError:
                    # no data (yet)
                    bar += ' '
                    continue

                q1 = (1 - dp1 / 100.0) * tbox.h
                q2 = (1 - dp2 / 100.0) * tbox.h
                if dx == int(q1):
                    index1 = 3 - int((q1 - int(q1)) * 4)
                elif dx > q1:
                    index1 = 3
                else:
                    index1 = 0
                if dx == int(q2):
                    index2 = 3 - int((q2 - int(q2)) * 4)
                elif dx > q2:
                    index2 = 3
                else:
                    index2 = 0
                bar += self._generate_braille(index1, index2)

            print(tbox.t.move(tbox.x + dx, tbox.y) + bar)
