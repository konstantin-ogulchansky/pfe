"""
...
"""

import matplotlib.pyplot as plt

from pfe.misc.log import nothing


class XAxis:
    """..."""

    def __init__(self, ax):
        self.ax = ax

    def limit(self, *args, **kwargs):
        self.ax.set_xlim(*args, **kwargs)

    def scale(self, *args, **kwargs):
        self.ax.set_xscale(*args, **kwargs)

    def label(self, *args, **kwargs):
        self.ax.set_xlabel(*args, **kwargs)

    def ticks(self, values):
        self.ax.set_xticks([x for x, _ in values])
        self.ax.set_xticklabels([y for _, y in values])

    def line(self, x):
        self.ax.axvline(x, linestyle='dashed', color='black', linewidth=0.75)


class YAxis:
    """..."""

    def __init__(self, ax):
        self.ax = ax

    def limit(self, *args, **kwargs):
        self.ax.set_ylim(*args, **kwargs)

    def scale(self, *args, **kwargs):
        self.ax.set_yscale(*args, **kwargs)

    def label(self, *args, **kwargs):
        self.ax.set_ylabel(*args, **kwargs)

    def ticks(self, values):
        self.ax.set_yticks([x for x, _ in values])
        self.ax.set_yticklabels([y for _, y in values])

    def line(self, y, label=None):
        self.ax.axhline(y, linestyle='dashed', color='black', linewidth=0.75)

        if label is not None:
            self.ax.text(0.005, y, label)  # TODO: Fix magic values.


class Plot:
    """..."""

    def __init__(self, ax=None, tex=False, title=None, log=nothing):
        # Must be before `plt.gca()`.
        if tex:
            plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman']})
            plt.rc('text', usetex=True)

        self.ax = ax or plt.gca()

        self.ax.set_title(title)
        self.ax.set_axisbelow(True)
        self.ax.grid(linestyle='--')

        self.log = log

    @property
    def x(self):
        return XAxis(self.ax)

    @property
    def y(self):
        return YAxis(self.ax)

    def scatter(self, dictionary, style=None, label=None):
        """..."""

        items = list(dictionary.items())

        x = [x for x, _ in items]
        y = [y for _, y in items]

        self.ax.scatter(x, y, **(style or circles), label=label)

    def draw(self, dictionary, style=None, label=None):
        """..."""

        if style is None:
            style = {'color': 'black', 'linewidth': 0.75}

        items = list(sorted(dictionary.items()))

        x = [x for x, _ in items]
        y = [y for _, y in items]

        self.ax.plot(x, y, **style, label=label)

    def text(self, x, y, label, rotation=0):
        self.ax.text(x, y, label, rotation=rotation)

    def legend(self, *, title=None, location=None):
        """..."""

        legend = self.ax.legend(shadow=True, title=title, edgecolor='black', loc=location)

        frame = legend.get_frame()
        frame.set_linewidth(0.5)

    def show(self):
        """..."""

        self.log('Showing the figure...')
        plt.show()

    def save(self, name, and_show=True):
        """..."""

        self.log(f'Saving the figure `{name}`...')
        plt.savefig(name)

        if and_show:
            self.show()


colors = [
    red   := '#ff3f3f',
    blue  := '#3f3fff',
    green := '#3fff3f',
]

styles = [
    crosses := dict(s=25, color='black', marker='x'),
    circles := dict(s=25, facecolors='none', edgecolors='black'),
]
