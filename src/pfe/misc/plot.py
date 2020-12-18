"""
A soft wrapper around `matplotlib` that unifies styling
and provides a slightly better API for plotting.
"""

from typing import Any, Iterable, Tuple, Optional, Union

import matplotlib.pyplot as plt

from pfe.tasks.statistics import Statistic


class Plot:
    """A plot. :)"""

    def __init__(self,
                 ax: Optional[plt.Axes] = None,
                 title: Optional[str] = None,
                 tex: bool = False,
                 grid: bool = True):
        """Initialises the plot.

        :param ax: an instance of `Axes` to plot on.
        :param title: a title of the plot.
        :param tex: whether to use TeX and the 'Computer Modern' font;
                    if enabled, plotting may be time consuming.
        :param grid: whether to draw a grid.
        """

        if tex:
            # Must be before `plt.gca()`.
            plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman']})
            plt.rc('text', usetex=True)

        self.ax: plt.Axes = ax or plt.gca()
        self.fig: plt.Figure = self.ax.figure

        if title is not None:
            self.ax.set_title(title)
        if grid:
            self.ax.set_axisbelow(True)
            self.ax.grid(linestyle='--')

        # self.ax.set_color_cycle([
        #     '#ff3f3f',  # Red.
        #     '#3f3fff',  # Blue.
        #     '#3fff3f',  # Green.
        # ])

    @property
    def x(self) -> 'XAxis':
        """Returns the `x` axis."""
        return XAxis(self.ax)

    @property
    def y(self) -> 'YAxis':
        """Returns the `y` axis."""
        return YAxis(self.ax)

    def scatter(self, data: Union[dict[float, float], Statistic], **kwargs: Any):
        """Scatters points that are specified in `data`.

        :param data: a dictionary that maps `x` to `y`.
        """

        items = list(data.items())
        x = [x for x, _ in items]
        y = [y for _, y in items]

        # Set the default style.
        if 'marker' not in kwargs:
            kwargs = circles | kwargs

        self.ax.scatter(x, y, **kwargs)

    def draw(self, data: Union[dict[float, float], Statistic], **kwargs: Any):
        """Draws a line through (sorted) points that are specified in `data`.

        :param data: a dictionary that maps `x` to `y`.
        """

        items = list(sorted(data.items()))
        x = [x for x, _ in items]
        y = [y for _, y in items]

        # Set the default style.
        kwargs.setdefault('color', 'black')
        kwargs.setdefault('linewidth', 0.75)

        self.ax.plot(x, y, **kwargs)

    def text(self, x: float, y: float, label: str, **kwargs: Any):
        """An alias for `text`."""
        self.ax.text(x, y, label, **kwargs)

    def legend(self, *, location: Optional[str] = None, **kwargs: Any):
        """Adds the legend."""

        # Set the default style.
        kwargs.setdefault('shadow', True)
        kwargs.setdefault('fancybox', True)
        kwargs.setdefault('edgecolor', 'black')
        kwargs.setdefault('prop', {'size': 8})

        if location is not None:
            kwargs['loc'] = location

        legend = self.ax.legend(**kwargs)

        frame = legend.get_frame()
        frame.set_linewidth(0.5)

        title = legend.get_title()
        title.set_fontsize(10)

    def show(self):
        """Shows the plot."""
        self.fig.show()

    def resize(self,
               width: Optional[float] = None,
               height: Optional[float] = None,
               scale: float = 1):
        """Resizes the figure.

        :param width: the width of the figure in inches.
        :param height: the height of the figure in inches.
        :param scale: the scaling factor to multiply
                      the width and the height with.
        """

        if width is None:
            width = self.fig.get_figwidth()
        if height is None:
            height = self.fig.get_figheight()

        self.fig.set_size_inches(width * scale, height * scale)
        self.fig.tight_layout()

    def save(self, path: str, dpi: Optional[int] = None, and_show: bool = True):
        """Saves the plot (and probably shows it too).

        :param path: the path to a file to save the plot to.
        :param dpi: the resolution of the figure in DPI (dots per inch).
        :param and_show: whether to show the plot after saving;
                         very convenient with PyCharm's scientific mode.
        """

        if dpi is not None:
            self.fig.savefig(path, dpi=dpi)
        else:
            self.fig.savefig(path)

        if and_show:
            self.show()


class XAxis:
    """Represents the abscissa (the `x` axis)."""

    __slots__ = ('ax',)

    def __init__(self, ax: plt.Axes):
        self.ax = ax

    def limit(self, *args: Any, **kwargs: Any):
        """An alias for `set_xlim`."""
        self.ax.set_xlim(*args, **kwargs)

    def scale(self, *args: Any, **kwargs: Any):
        """An alias for `set_xscale`."""
        self.ax.set_xscale(*args, **kwargs)

    def label(self, *args: Any, **kwargs: Any):
        """An alias for `set_xlabel`."""
        self.ax.set_xlabel(*args, **kwargs)

    def ticks(self, values: Iterable[Tuple[float, str]]):
        """Updates ticks via `set_xticks` and `set_xticklabels`.

        :param values: a collection of pairs `(tick, label)`.
        """

        self.ax.set_xticks([x for x, _ in values])
        self.ax.set_xticklabels([y for _, y in values])

    def line(self, x: float, **kwargs: Any):
        """An alias for `axvline`."""

        # Set the default style.
        kwargs.setdefault('linestyle', 'dashed')
        kwargs.setdefault('color', 'black')
        kwargs.setdefault('linewidth', 0.75)

        self.ax.axvline(x, **kwargs)


class YAxis:
    """Represents the ordinate (the `y` axis)."""

    __slots__ = ('ax',)

    def __init__(self, ax: plt.Axes):
        self.ax = ax

    def limit(self, *args: Any, **kwargs: Any):
        """An alias for `set_ylim`."""
        self.ax.set_ylim(*args, **kwargs)

    def scale(self, *args: Any, **kwargs: Any):
        """An alias for `set_yscale`."""
        self.ax.set_yscale(*args, **kwargs)

    def label(self, *args: Any, **kwargs: Any):
        """An alias for `set_ylabel`."""
        self.ax.set_ylabel(*args, **kwargs)

    def ticks(self, values: Iterable[Tuple[float, str]]):
        """Updates ticks via `set_yticks` and `set_yticklabels`.

        :param values: a collection of pairs `(tick, label)`.
        """

        self.ax.set_yticks([x for x, _ in values])
        self.ax.set_yticklabels([y for _, y in values])

    def line(self, y: float, **kwargs: Any):
        """An alias for `axhline`."""

        # Set the default style.
        kwargs.setdefault('linestyle', 'dashed')
        kwargs.setdefault('color', 'black')
        kwargs.setdefault('linewidth', 0.75)

        self.ax.axhline(y, **kwargs)


# A set of pretty markers.
markers = [
    crosses := dict(s=25, color='black', marker='x'),
    circles := dict(s=25, facecolors='none', edgecolors='black'),
]
