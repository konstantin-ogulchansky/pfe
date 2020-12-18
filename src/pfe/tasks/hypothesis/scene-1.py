"""
Fit the degree distribution.
"""

import powerlaw as pl

from pfe.misc.log import Log, Pretty, redirect_stderr_to, suppress_stderr
from pfe.misc.plot import Plot, crosses, circles
from pfe.misc.style import blue
from pfe.parse import parse, publications_in
from pfe.tasks.hypothesis import degree_distribution
from pfe.tasks.statistics import Statistic


weighted: bool = True
"""Whether to plot the weighted degree distribution."""

tex: bool = True
"""Whether to use TeX in plots."""

scale: float = 0.43
"""Scale of the figures."""


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

    fit.plot_pdf(ax=plot.ax, original_data=True, label='Empirical PDF')

    plot.legend()
    plot.resize(scale=scale)
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

    fit.plot_pdf(ax=plot.ax, label='Empirical')
    fit.power_law.plot_pdf(ax=plot.ax, label='Power-Law')
    fit.truncated_power_law.plot_pdf(ax=plot.ax, label='Power-Law with Cut-Off')

    plot.legend(location='lower left')
    plot.resize(scale=scale)
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

    fit.plot_cdf(ax=plot.ax, label='Empirical')
    fit.power_law.plot_cdf(ax=plot.ax, label='Power-Law')
    fit.truncated_power_law.plot_cdf(ax=plot.ax, label='Power-Law with Cut-Off')

    plot.legend(location='lower right')
    plot.resize(scale=scale)
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

    fit.plot_ccdf(ax=plot.ax, label='Empirical')
    fit.power_law.plot_ccdf(ax=plot.ax, label='Power-Law')
    fit.truncated_power_law.plot_ccdf(ax=plot.ax, label='Power-Law with Cut-Off')

    plot.legend(location='lower left')
    plot.resize(scale=scale)
    plot.save('COMP' + '-w' * weighted + '-ccdf.eps')


if __name__ == '__main__':
    log: Log = Pretty()
    log.info('Starting.')

    redirect_stderr_to(log.warn)

    with log.scope.info('Reading a graph.'):
        graph = parse(publications_in('COMP', between=(1990, 2018), log=log))

        log.info(f'Read a graph with '
                 f'{blue | graph.number_of_nodes()} nodes and '
                 f'{blue | graph.number_of_edges()} edges.')

    with log.scope.info('Computing the degree distribution.'):
        statistic = degree_distribution(graph, weighted)

    with log.scope.info('Fitting the hypothesis.'):
        fit = pl.Fit(list(statistic.sequence()), discrete=True)

        with log.scope.info('Estimating power-law parameters.'):
            log.info(f'α: {fit.power_law.alpha}')
            log.info(f'σ: {fit.power_law.sigma}')
            log.info(f'x: {[fit.power_law.xmin, fit.power_law.xmax]}')

        with log.scope.info('Estimating power-law with cutoff parameters.'):
            log.info(f'α: {fit.truncated_power_law.alpha}')
            log.info(f'λ: {fit.truncated_power_law.Lambda}')
            log.info(f'x: {[fit.truncated_power_law.xmin, fit.truncated_power_law.xmax]}')

        if not fit.xmin == fit.power_law.xmin == fit.truncated_power_law.xmin:
            log.warn('`xmin` differs.')
        if not fit.xmax == fit.power_law.xmax == fit.truncated_power_law.xmax:
            log.warn('`xmax` differs.')

    with log.scope.info('Comparing distributions.'), suppress_stderr():
        comparison = {}

        for a in fit.supported_distributions:
            for b in fit.supported_distributions:
                comparison[a, b] = fit.distribution_compare(a, b)

                log.info(f'{a:<23} {b:<23} {comparison[a, b]}')

        with open('COMP' + '-w' * weighted + '-log-likelihood.txt', 'w') as file:
            file.write('\n'.join(f'{a:<23} {b:<23} {comparison[a, b]}'
                                 for a, b in comparison))

    with log.scope.info('Plotting the degree distribution.'):
        plot_dd(statistic, fit)
    with log.scope.info('Plotting theoretical PDFs.'):
        plot_pdf(statistic, fit)
    with log.scope.info('Plotting theoretical CDFs.'):
        plot_cdf(statistic, fit)
    with log.scope.info('Plotting theoretical CCDfs.'):
        plot_ccdf(statistic, fit)
