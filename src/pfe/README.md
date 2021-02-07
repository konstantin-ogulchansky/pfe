# PFE

This directory contains scripts for processing collaboration graphs.

## Parsing

`parse.py` defines methods that parse data on (clean) publications and construct 
a collaboration graph, based on the parsed data.
We use the `networkx` package to represent graphs.

The following example demonstrates how to extract publications from `data/clean` directory
and construct a corresponding collaboration graph.

```python
from pfe.parse import parse, all_publications, publications_in, publications_from

# Construct a collaboration graph based on publications 
# within all domains between the years 1990 and 2018.
graph = parse(all_publications(between=(1990, 2018)))

# Construct a collaboration graph based on publications 
# within the domains of computer science and physics 
# between the years 1990 and 2018.
graph = parse(publications_in('COMP', 'PHYS', between=(1990, 2018)))

# Construct a collaboration graph based on publications
# from file '/path/to/a.json'.
graph = parse(publications_from(['/path/to/a.json']))
```

The function `parse` simply accepts a list (or any iterable) of publications, represented as
dictionaries, and produces an instance of `networkx.Graph`.

Each node in the produced graph has the following attributes:
* `publications`, which represents the total number of publications that the corresponding
  author collaborated on.

Each edge in the produced graph has the following attributes:
* `collaborations`, which represents the total number of publications that the corresponding
  authors collaborated on;
* `weight`, which represents the "closeness" of the collaboration of two authors.

It is recommended to save large graphs into a file.

1. Build graph using function `parse` from `parse.py`;
2. Save built graph into file using `networkx.write_weighted_edgelist()`.

If you need to use a graph of `igraph` instance there are several ways to convert `networkx` graph.

* You can use `igraph` function `igraph.Graph.from_networkx(g)` where `g` – graph of instance of `networks`. However, if a graph is too large, it takes much time;
* Or you can run `rename.py` that can create a file containing the list of weighted edges, that `igraph` can use to build a graph.


For the last option, run `rename.py` from `preprocessing`. The graph can be created either from the file (if you have already created the graph and saved it into the file) or with function `parse`.

Three files will be created:

1. `nx_node_mapping.csv` – contains pairs `(author-id, i)`, `i` from `[1..n]`;
2. `nx_graph_relabeled_nodes.txt` – file containing the list of weighted edges for `networkx`;
3. `ig_graph_relabeled_nodes.net` – file containing the list of weighted edges for `igraph`.

To create graph of `igraph` instance from file we used `igraph.Graph.Read_Pajek(file)`. 

> `igraph` nodes have ids from `1` to `n`, while `networks` can use author ids as node ids. 
> Thus, author-ids need to be mapped into `[1..n]`.

## Tasks

The `tasks` directory contains scripts related to the tasks that had to be completed,
such as computing and fitting distributions (of the number of authors per publication, 
of the number of publications per author, etc.), clustering and others.

### Communities 

`communities.py` defines methods that run community detection algorithm (Louvain Method or Leiden Algorithm) on a given graph.

#### Louvain Method

```
louvain(graph: nx.Graph,  data: Path, log: Log)
```

- `graph` – an instance of `networkx.Graph`;
- `data` – output path for results;
- `log` – logger from `misc` `log.py`.

Resulting file has extension `json` and contains key-value pairs, where key is a community number and value – list of members.

Example:

```
{
  "0": ["1", "2", "3", ..],
  ...,
  "№ community": [list of `str`s (member ids as string)]
}
```

#### Leiden Algorithm 

```
leiden(graph: ig.Graph, data: Path, log: Log)
```
  
- `graph` – an instance of `igraph.Graph`. 
- `data` – output path for results.
- `log` – logger from `misc` `log.py`

Creates two `json` files. First, contains key-value pairs, where key is a community number and value – list of members.

Example:

```
{
  "0": [1, 2, 3, ..],
  ...,
  "№ community": [list of `int`s (member ids)]
}
```

Second file contains modularity of Leiden partition.

### Distributions

`distributions.py` defines methods for calculating different distributions, associated with the network,
such as `authors_per_publications`, `publications_per_authors`, `degree_distribution`, and others.

Please refer to `distributions.ipynb` for examples.

## Preprocessing

The `preprocessing` directory contains scripts that are related to preprocessing of data.

For example, `clean.py` can be used to clean the raw data from redundant fields,
thus significantly reducing JSON files in size.
This script can be used right away by simply running it.

## Miscellaneous

The `misc` directory contains auxiliary scripts, such as `log.py` or `errors.py`.

The most interesting script here is, probably, `log.py`. 
This file defines classes that allow printing [`Pretty`](misc/log/pretty.py) colored logs.
Consider the following example.

```python
from pfe.parse import parse, publications_in
from pfe.misc.log import Pretty

log = Pretty()
log.info('Starting.')

with log.scope.info('Reading a graph.'):
    graph = parse(publications_in('COMP', between=(1990, 2018), log=log))

log.info(f'Read a graph with '
         f'{graph.number_of_nodes()} nodes and '
         f'{graph.number_of_edges()} edges.')
```

The code above will output the following (excluding colours, of course).

```
2021-03-22 08:14:28.848894  INFO     Starting.
2021-03-22 08:14:28.848894  INFO   ╭ Reading a graph.
2021-03-22 08:14:28.849893  INFO   │     Reading "COMP-1990.json". [ 14.3%]
2021-03-22 08:14:28.887791  INFO   │     Reading "COMP-1991.json". [ 28.6%]
2021-03-22 08:14:28.917712  INFO   │     Reading "COMP-1992.json". [ 42.9%]
2021-03-22 08:14:28.954611  INFO   │     Reading "COMP-1993.json". [ 57.1%]
2021-03-22 08:14:28.998494  INFO   │     Reading "COMP-1994.json". [ 71.4%]
2021-03-22 08:14:29.050355  INFO   │     Reading "COMP-1995.json". [ 85.7%]
2021-03-22 08:14:29.129649  INFO   │     Reading "COMP-1996.json". [100.0%]
2021-03-22 08:14:29.223399  INFO   ╰ Done in 0.374505s.
2021-03-22 08:14:29.229382  INFO     Read a graph with 16961 nodes and 50343 edges.
```

Everything within `log.scope` will be indented.
Scopes can also contain other scopes, thus increasing the nesting level.

There is also a convenient [`Nothing`](misc/log/nothing.py) class, 
which ignores logs and does not print anything.
For example, one could pass `Nothing` instead of `Pretty` 
in order to silence all the logs that a certain function produces.
