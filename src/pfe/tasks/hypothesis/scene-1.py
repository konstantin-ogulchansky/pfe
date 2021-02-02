"""
Fit the degree distribution.
"""

import powerlaw as pl

from pfe.misc.log import Log, Pretty, redirect_stderr_to, suppress_stderr
from pfe.misc.plot import Plots, crosses, circles
from pfe.misc.style import blue
from pfe.parse import parse, publications_in
from pfe.tasks.distributions import Distribution, degree_distribution


weighted: bool = False
"""Whether to plot the weighted degree distribution."""

tex: bool = True
"""Whether to use TeX in plots."""


def plot_pdf(statistic: Distribution, fit: pl.Fit):
    """Plots theoretical PDFs."""

    global tex, weighted

    normalized = statistic.pdf()
    truncated = statistic.truncate(fit.xmin, fit.xmax)

    plots = Plots(rows=2, cols=1, tex=tex)

    # The top subplot.
    top = plots[0, 0]

    included = {x: y for x, y in normalized.items() if x in truncated}
    excluded = {x: y for x, y in normalized.items() if x not in truncated}

    top.scatter(excluded, **crosses, label='Excluded Degrees')
    top.scatter(included, **circles, label='Included Degrees')

    top.x.scale('log')
    top.x.limit(10 ** 0, 10 ** 4)

    top.y.label('$P' + '_w' * weighted + '(k)$')
    top.y.scale('log')
    top.y.limit(10 ** -6, 10 ** 0)

    if fit.xmin is not None:
        dx = 0.75 if weighted else 2.25

        top.x.line(fit.xmin)
        top.text(fit.xmin - dx, 1.5 * 10**-4, f'$k_{{\\mathrm{{min}}}} = {fit.xmin:g}$', rotation=90)

    fit.plot_pdf(ax=top.ax, original_data=True, label='Empirical PDF')

    top.legend(location='lower left')

    # The bottom subplot.
    bottom = plots[1, 0]
    bottom.scatter(truncated.pdf())

    bottom.x.label('Weighted ' * weighted + 'Degree $k$')
    bottom.x.scale('log')
    bottom.x.limit(10 ** 0, 10 ** 4)

    bottom.y.label('$P' + '_w' * weighted + '(k)$')
    bottom.y.scale('log')
    bottom.y.limit(10 ** -6, 10 ** 0)

    fit.plot_pdf(ax=bottom.ax, label='Empirical')
    fit.power_law.plot_pdf(ax=bottom.ax, label='Power-Law')
    fit.truncated_power_law.plot_pdf(ax=bottom.ax, label='Power-Law with Cutoff')

    bottom.legend(location='lower left')

    # Saving the plot.
    plots.save('COMP' + '-w' * weighted + '-pdf.eps')


def plot_cdf(statistic: Distribution, fit: pl.Fit):
    """Plots theoretical CDFs."""

    global tex, weighted

    truncated = statistic.truncate(fit.xmin, fit.xmax)

    plots = Plots(rows=2, cols=1, tex=tex)

    # The top subplot.
    top = plots[0, 0]
    top.scatter(truncated.cdf())

    top.x.scale('log')
    top.x.limit(10 ** 0, 10 ** 4)

    top.y.label('$F' + '_w' * weighted + '(k)$')
    top.y.scale('log')

    fit.plot_cdf(ax=top.ax, label='Empirical')
    fit.power_law.plot_cdf(ax=top.ax, label='Power-Law')
    fit.truncated_power_law.plot_cdf(ax=top.ax, label='Power-Law with Cutoff')

    top.legend(location='lower right')

    # The bottom subplot.
    bottom = plots[1, 0]
    bottom.scatter(truncated.ccdf())

    bottom.x.label('Weighted ' * weighted + 'Degree $k$')
    bottom.x.scale('log')
    bottom.x.limit(10 ** 0, 10 ** 4)

    bottom.y.label('$\\bar{F}' + '_w' * weighted + '(k)$')
    bottom.y.scale('log')

    fit.plot_ccdf(ax=bottom.ax, label='Empirical')
    fit.power_law.plot_ccdf(ax=bottom.ax, label='Power-Law')
    fit.truncated_power_law.plot_ccdf(ax=bottom.ax, label='Power-Law with Cutoff')

    bottom.legend(location='lower left')

    # Saving the plot.
    plots.save('COMP' + '-w' * weighted + '-cdf.eps')


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
        fit = pl.Fit(statistic.as_list(), discrete=True)

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

    with log.scope.info('Plotting theoretical PDFs.'):
        plot_pdf(statistic, fit)
    with log.scope.info('Plotting theoretical CDFs.'):
        plot_cdf(statistic, fit)
