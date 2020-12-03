"""
Fit the degree distribution.
"""

import powerlaw as pl

from pfe.misc.collections import truncate
from pfe.misc.log import timestamped
from pfe.misc.plot import Plot, red, blue, crosses, circles, green
from pfe.parse import parse, publications_in
from pfe.tasks.hypothesis import degree_distribution


if __name__ == '__main__':
    log = timestamped
    log('Starting...')

    weighted = False

    # Construct a graph.
    graph = parse(publications_in('COMP', between=(1990, 2018), log=log))

    log(f'Read a graph with '
        f'{graph.number_of_nodes()} nodes and '
        f'{graph.number_of_edges()} edges.')

    # Compute the degree distribution.
    original = degree_distribution(graph, weighted)
    original_normalized = original.normalized()

    # Fit the hypothesis.
    fit = pl.Fit(list(original.sequence()), discrete=True)

    log(f'Estimated power-law parameters:'
        f'    α: {fit.power_law.alpha}'
        f'    σ: {fit.power_law.sigma}'
        f'    x: {(fit.power_law.xmin, fit.power_law.xmax)}')
    log(f'Estimated power-law with cutoff parameters:'
        f'    α: {fit.truncated_power_law.alpha}'
        f'    λ: {fit.truncated_power_law.Lambda}'
        f'    x: {(fit.truncated_power_law.xmin, fit.truncated_power_law.xmax)}')

    # Compare distributions.
    log('Comparing distributions...')

    comparison = {
        (a, b): fit.distribution_compare(a, b, normalized_ratio=True)
        for a in fit.supported_distributions
        for b in fit.supported_distributions
    }
    comparison = \
        '\n' + \
        '\n'.join(f'{a:>25}   {b:>25}   {comparison[a, b]}'
                  for a, b in comparison)

    with open('COMP' + '-w' * weighted + '-log-likelihood.txt', 'w') as file:
        file.write(comparison)

    log(comparison)

    # Compute the truncated degree distribution
    # (i.e., without points out of `(x_min, x_max)` range).
    if fit.power_law.xmin != fit.truncated_power_law.xmin:
        log('`x_min` differs for power-law and power-law with cutoff.')
    if fit.power_law.xmax != fit.truncated_power_law.xmax:
        log('`x_max` differs for power-law and power-law with cutoff.')

    x_min = max(filter(None, [fit.power_law.xmin, fit.truncated_power_law.xmin]), default=None)
    x_max = min(filter(None, [fit.power_law.xmax, fit.truncated_power_law.xmax]), default=None)

    truncated = original.truncate(x_min, x_max)
    truncated_normalized = truncated.normalized()

    # Plot the data.
    log('Plotting the data...')

    included = truncate(original_normalized, x_min, x_max)
    excluded = {x: y for x, y in original_normalized.items() if x not in included}

    plot = Plot(tex=True, log=log)

    plot.x.label('Weighted ' * weighted + 'Degree $k$')
    plot.x.scale('log')
    plot.x.limit(10 ** -1, 10 ** 4)

    plot.y.label('$P' + '_w' * weighted + '(k)$')
    plot.y.scale('log')
    plot.y.limit(10 ** -6, 10 ** 0)

    plot.scatter(excluded, crosses, label='Excluded Points')
    plot.scatter(included, circles, label='Included Points')

    if x_min is not None:
        plot.x.line(x_min, label=f'$x_{{min}} = {x_min}$')
    if x_max is not None:
        plot.x.line(x_max, label=f'$x_{{max}} = {x_max}$')

    fit.plot_pdf(ax=plot.ax, original_data=True, color=red, linestyle='--', label='Empirical PDF')

    plot.legend()
    plot.save(f'COMP' + '-w' * weighted + '-degrees.eps')

    # Plot estimated theoretical PDFs.
    log('Plotting theoretical PDFs...')

    plot = Plot(tex=True, log=log)
    plot.scatter(truncated_normalized)

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

    # Plot estimated theoretical CDFs.
    log('Plotting theoretical CDFs...')

    plot = Plot(tex=True, log=log)
    plot.scatter(truncated.cdf())

    plot.x.label('Weighted ' * weighted + 'Degree $k$')
    plot.x.scale('log')
    plot.x.limit(10 ** -1, 10 ** 4)

    plot.y.label('$F' + 'w_' * weighted + '(k)$')
    plot.y.scale('log')

    fit.plot_cdf(ax=plot.ax, color=red, label='Empirical')
    fit.power_law.plot_cdf(ax=plot.ax, color=blue, label='Power-Law')
    fit.truncated_power_law.plot_cdf(ax=plot.ax, color=green, label='Power-Law with Cut-Off')

    plot.legend(title='CDF', location='lower right')
    plot.save('COMP' + '-w' * weighted + '-cdf.eps')

    # Plot estimated theoretical CCDFs.
    log('Plotting theoretical CCDFs...')

    plot = Plot(tex=True, log=log)
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
