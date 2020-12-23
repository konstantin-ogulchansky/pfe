"""
Test the hypothesis.
"""

import math

import powerlaw as pl
import scipy.stats as st
import numpy as np

from pfe.misc.log import Log, Pretty, redirect_stderr_to
from pfe.misc.log.misc import itemize
from pfe.misc.plot import Plot
from pfe.misc.style import blue, underlined, bold
from pfe.parse import parse, publications_in
from pfe.tasks.hypothesis import degree_distribution, histogram


if __name__ == '__main__':
    np.set_printoptions(suppress=True)

    log: Log = Pretty()
    log.info('Starting.')

    redirect_stderr_to(log.warn)

    with log.scope.info('Reading a graph.'):
        graph = parse(publications_in('COMP', between=(1990, 2018), log=log))

        log.info(f'Read a graph with '
                 f'{blue | graph.number_of_nodes()} nodes and '
                 f'{blue | graph.number_of_edges()} edges.')

    with log.scope.info('Computing the degree distribution.'):
        statistic = degree_distribution(graph, weighted=True)

    with log.scope.info('Fitting the hypothesis.'):
        fit = pl.Fit(statistic.as_list(), discrete=True)

        x_min = int(fit.xmin or min(statistic.keys()))
        x_max = int(fit.xmax or max(statistic.keys()))

        truncated = statistic.truncate(x_min, x_max)

        x = list(range(x_min, x_max + 1))

        cdf = dict(zip(x, fit.truncated_power_law.cdf(x)))
        pdf = dict(zip(x, fit.truncated_power_law.pdf(x)))

        assert abs(1 - sum(pdf.values())) <= 1e-3, '`sum p_i` must equal 1.'

    with log.scope.info('Plotting PDF.'):
        plot = Plot(title='PDF')
        plot.scatter(truncated.normalized())
        plot.scatter(pdf, color='red')

        fit.truncated_power_law.plot_pdf(ax=plot.ax)

        plot.show()

    with log.scope.info('Plotting CDF.'):
        plot = Plot(title='CDF')
        plot.scatter(cdf, color='red')

        fit.truncated_power_law.plot_cdf(ax=plot.ax)

        plot.show()

    with log.scope.info('Computing the χ² statistic.'):
        n = truncated.total()

        obs = {x: truncated[x] for x in sorted(truncated)}
        exp = {x: n * pdf[x]   for x in sorted(pdf)}

        log.info(itemize(bold | 'Observed:', obs))
        log.info(itemize(bold | 'Expected:', exp))

        # These bins give pretty good results.
        # These bins were calculated with brute force.
        bins = [2, 64, 69, 226, 482]
        bin_obs = histogram(obs, bins)
        bin_exp = histogram(exp, bins)

        chi = st.chisquare(bin_obs, bin_exp, ddof=1)

        log.info(itemize(f'Special binning case.',
                         f'Bins: {list(bins)}',
                         f'Obs.: {bin_obs}',
                         f'Exp.: {bin_exp}',
                         f'χ²: {blue | tuple(chi)}'))

        def clear(obs, exp):
            i = 0
            while i < len(obs):
                if obs[i] == 0 and exp[i] == 0:
                    del obs[i]
                    del exp[i]
                else:
                    i += 1

        for amount in range(2, 50):
            lin_bins = np.linspace(x_min, x_max, amount)
            lin_obs = histogram(obs, lin_bins)
            lin_exp = histogram(exp, lin_bins)

            log_bins = np.logspace(math.log(x_min, 10), math.log(x_max, 10), amount)
            log_obs = histogram(obs, log_bins)
            log_exp = histogram(exp, log_bins)

            clear(lin_obs, lin_exp)
            clear(log_obs, log_exp)

            lin_chi = st.chisquare(lin_obs, lin_exp, ddof=1)
            log_chi = st.chisquare(log_obs, log_exp, ddof=1)

            log.info(itemize(f'{amount} bins ({underlined | "lin"}).',
                             f'Bins: {list(lin_bins)}',
                             f'Obs.: {lin_obs}',
                             f'Exp.: {lin_exp}',
                             f'χ²: {blue | tuple(lin_chi)}'))

            log.info(itemize(f'{amount} bins ({underlined | "log"}).',
                             f'Bins: {list(log_bins)}',
                             f'Obs.: {log_obs}',
                             f'Exp.: {log_exp}',
                             f'χ²: {blue | tuple(log_chi)}'))
