# Matrices 

This directory contains scripts for creation and visualisation of matrices where value in cell `i,j` corresponds to the probability of community `i` to have common publication with community `j`.

## Generating necessary data

`generate_data.py` contains a single function `create_data()` that does all job. 


Required pregenerated data:
- file of a graph in Pajek format
- node mapping that corresponds to that graph


The most important is to specify:
- the path, where the file of a graph is located (`data` variable, Pajek format `*.net`)
- the path, where all generated data will be placed (`new_data` variable)

Data that will be produced:
- `leiden_communities.json`
- `leiden_modularity.json`
- `leiden_author-community.json`
- `node_list.txt`
- `mapping.txt` (author_id : node_id)
- `stats_largest_cluster.json` (the most impotrant one)


## Creating Pandas matrices

`matrix.py` contains multiple finctions for creating and manipulatind matrices. 

- `matrix()` creates Numpy matrix using `stats_largest_cluster.json` data. 

*Returns*: symetric matrix where values in cell `i, j` and `j, i` correspond to the number of publications between community `i` and community `j`. Diagonal is zeros.

(Note: publications where only 2 communities have contributed are considered)

Example: Creates a matrix of number of publications with all communities. Then matrix is converted to DataFrame. (must have as all following functions work with DataFrame) 
```

n_communities = number_of_communities()
m = matrix()
m = pd.DataFrame(m, [str(i) for i in range(n_communities)], [str(i) for i in range(n_communities)])

```

- `fill_diagonal(martix)` fills diagonal (`i, j`, where `i`=`j`) with the number of publications that belong only to a single community `i`. 

*Returns*: DataFrame matrix with filled diagonal.


- `prob_matrix(martix)` devides each value in a row `i` by the sum of all values in this row.

*Returns*: DataFrame matrix with modified values.

- `add_row_with_community_size()` adds a column with the number that corresponds to the size of the community.

- `exclude_columns(martix, columns)`

- `keep_columns(martix, columns)`

## Plotting 

`plot_heatmap.py` contains `plot_matrix` function that creates an image with heatmap.

- `plot_matrix(matrix, file_name, title='', subtitle='', prob=False, exclude_columns=False)`
    - `matrix` DataFrame matrix
    - `file_name` the name under which the image will be created
    - `title`, `subtitle` optional, captures that will be written on the image
    - `prob` flag that indicates the format of the content of the matrix. when `True` `fmt=".4f"`, otherwise ` fmt="d"`
    - `exclude_columns` indicates that there are special columns in the matrix which values should be excluded from heatmap. For example if there is column with community sizes we don't want it to affect the colors of each value of the matrix. 
