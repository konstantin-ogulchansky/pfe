"""
Fit the degree distribution.
"""

import powerlaw as pl

from pfe.misc.log import timestamped, cx
from pfe.misc.plot import Plot, red, blue, crosses, circles, green
from pfe.parse import parse, publications_in
from pfe.tasks.hypothesis import degree_distribution
from pfe.tasks.statistics import Statistic


tex: bool = True
"""Whether to use TeX in plots."""

weighted: bool = True
"""Whether to plot the weighted degree distribution."""


def plot_dd(statistic: Statistic, fit: pl.Fit):
    """Plots the degree distribution."""

    global tex, weighted

    normalized = statistic.normalized()
    truncated = statistic.truncate(fit.xmin, fit.xmax)

    included = {x: y for x, y in normalized.items() if x in truncated}
    excluded = {x: y for x, y in normalized.items() if x not in truncated}

    plot = Plot(tex=tex)

    plot.x.label('Weighted ' * weighted + 'Degree $k$')
    plot.x.scale('log')
    plot.x.limit(10 ** -1, 10 ** 4)

    plot.y.label('$P' + '_w' * weighted + '(k)$')
    plot.y.scale('log')
    plot.y.limit(10 ** -6, 10 ** 0)

    plot.scatter(excluded, **crosses, label='Excluded Degrees')
    plot.scatter(included, **circles, label='Included Degrees')

    if fit.xmin is not None:
        dx = 0.75 if weighted else 2.25

        plot.x.line(fit.xmin)
        plot.text(fit.xmin - dx, 1.25 * 10**-4, f'$x_{{min}} = {fit.xmin:g}$', rotation=90)

    if fit.xmax is not None:
        dx = 0.75 if weighted else 2.25

        plot.x.line(fit.xmax)
        plot.text(fit.xmax - dx, 1.25 * 10**-4, f'$x_{{max}} = {fit.xmax:g}$', rotation=90)

    fit.plot_pdf(ax=plot.ax, original_data=True, color=red, label='Empirical PDF')

    plot.legend()
    plot.save(f'COMP' + '-w' * weighted + '-dd.eps')


def plot_pdf(statistic: Statistic, fit: pl.Fit):
    """Plots theoretical PDFs."""

    global tex, weighted

    truncated = statistic.truncate(fit.xmin, fit.xmax)

    plot = Plot(tex=tex)
    plot.scatter(truncated.normalized())

    plot.x.label('Weighted ' * weighted + 'Degree $k$')
    plot.x.scale('log')
    plot.x.limit(10 ** -1, 10 ** 4)

    plot.y.label('$P' + '_w' * weighted + '(k)$')
    plot.y.scale('log')
    plot.y.limit(10 ** -6, 10 ** 0)

    fit.plot_pdf(ax=plot.ax, color=red, label='Empirical')
    fit.power_law.plot_pdf(ax=plot.ax, color=blue, label='Power-Law')
    fit.truncated_power_law.plot_pdf(ax=plot.ax, color=green, label='Power-Law with Cut-Off')

    plot.legend(title='PDF')
    plot.save('COMP' + '-w' * weighted + '-pdf.eps')


def plot_cdf(statistic: Statistic, fit: pl.Fit):
    """Plots theoretical CDFs."""

    global tex, weighted

    truncated = statistic.truncate(fit.xmin, fit.xmax)

    plot = Plot(tex=tex)
    plot.scatter(truncated.cdf())

    plot.x.label('Weighted ' * weighted + 'Degree $k$')
    plot.x.scale('log')
    plot.x.limit(10 ** -1, 10 ** 4)

    plot.y.label('$F' + '_w' * weighted + '(k)$')
    plot.y.scale('log')

    fit.plot_cdf(ax=plot.ax, color=red, label='Empirical')
    fit.power_law.plot_cdf(ax=plot.ax, color=blue, label='Power-Law')
    fit.truncated_power_law.plot_cdf(ax=plot.ax, color=green, label='Power-Law with Cut-Off')

    # Unfortunately, for some reason this must be after `fit.plot_whatever`. :(
    plot.y.ticks([
        (10 ** -1, r'$10^{-1}$'),
        (10 ** 0,  r'$10^{ 0}$')
    ])

    plot.legend(title='CDF', location='lower right')
    plot.save('COMP' + '-w' * weighted + '-cdf.eps')


def plot_ccdf(statistic: Statistic, fit: pl.Fit):
    """Plots theoretical CCDFs."""

    global tex, weighted

    truncated = statistic.truncate(fit.xmin, fit.xmax)

    plot = Plot(tex=tex)
    plot.scatter(truncated.ccdf())

    plot.x.label('Weighted ' * weighted + 'Degree $k$')
    plot.x.scale('log')
    plot.x.limit(10 ** -1, 10 ** 4)

    plot.y.label('$\\overline{F}' + '_w' * weighted + '(k)$')
    plot.y.scale('log')

    fit.plot_ccdf(ax=plot.ax, color=red, label='Empirical')
    fit.power_law.plot_ccdf(ax=plot.ax, color=blue, label='Power-Law')
    fit.truncated_power_law.plot_ccdf(ax=plot.ax, color=green, label='Power-Law with Cut-Off')

    plot.legend(title='CCDF', location='lower left')
    plot.save('COMP' + '-w' * weighted + '-ccdf.eps')


if __name__ == '__main__':
    log = timestamped
    log('Starting...')

    # Construct a graph.
    graph = parse(publications_in('COMP', between=(1990, 2018), log=log))

    log(f'Read a graph with '
        f'{graph.number_of_nodes()} nodes and '
        f'{graph.number_of_edges()} edges.')

    # Compute the degree distribution.
    with cx(log, 'Computing the degree distribution...'):
        statistic = degree_distribution(graph, weighted)

    # Fit the hypothesis.
    with cx(log, 'Fitting the hypothesis...'):
        fit = pl.Fit(list(statistic.sequence()), discrete=True)

        log(f'Estimated power-law parameters:'
            f'    α: {fit.power_law.alpha}'
            f'    σ: {fit.power_law.sigma}'
            f'    x: {(fit.power_law.xmin, fit.power_law.xmax)}')
        log(f'Estimated power-law with cutoff parameters:'
            f'    α: {fit.truncated_power_law.alpha}'
            f'    λ: {fit.truncated_power_law.Lambda}'
            f'    x: {(fit.truncated_power_law.xmin, fit.truncated_power_law.xmax)}')

        if not fit.xmin == fit.power_law.xmin == fit.truncated_power_law.xmin:
            log('`xmin` differs.')
        if not fit.xmax == fit.power_law.xmax == fit.truncated_power_law.xmax:
            log('`xmax` differs.')

    # Compare distributions.
    with cx(log, 'Comparing distributions...'):
        comparison = {
            (a, b): fit.distribution_compare(a, b, normalized_ratio=True)
            for a in fit.supported_distributions
            for b in fit.supported_distributions
        }
        comparison = \
            '\n'.join(f'{a:>25}   {b:>25}   {comparison[a, b]}'
                      for a, b in comparison)

        with open('COMP' + '-w' * weighted + '-log-likelihood.txt', 'w') as file:
            file.write(comparison)

        log('\n' + comparison)

    # Plotting.
    with cx(log, 'Plotting data...'):
        plot_dd(statistic, fit)
    with cx(log, 'Plotting theoretical PDFs...'):
        plot_pdf(statistic, fit)
    with cx(log, 'Plotting theoretical CDFs...'):
        plot_cdf(statistic, fit)
    with cx(log, 'Plotting theoretical CCDfs...'):
        plot_ccdf(statistic, fit)
