import json
from collections import Counter
import matplotlib.pyplot as plt
from pfe.misc.log import Pretty, Log
import numpy as np


log: Log = Pretty()

with open('../../../data/graph/ig/leiden_communities.json', 'r') as file:
    data = json.load(file)

n_members = []
for c in data.items():
    n_members.append(len(c[1]))

total_authors = sum(n_members)

print('Total number of authors: ', total_authors)

count_sizes = dict(Counter(n_members))  # Dictionary 'community size': total number of members in such communities


def percent_of(k, n):
    return round(k*n * 100 / total_authors, 6)


count_percentage = {k: percent_of(v, k) for k, v in count_sizes.items()}

print('Number of unique sizes: ', len(count_sizes))
print('Max community size: ', max(count_percentage.keys()))
print('Max %: ', max(count_percentage.values()))

list = [(k, v) for k, v in count_percentage.items()]
list.sort(reverse=True)

print('Size: %')
for k, v in list:
    print(f'{k} : {v}%')


fig1, ax1 = plt.subplots()
ax1.pie([y for x, y in list], labels=[x for x, y in list], autopct='%1.01f%%',
        shadow=True, startangle=90)
ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

#
# plt.rcdefaults()
# fig, ax = plt.subplots()
#
# # Example data
# people = count_percentage.keys()
# y_pos = np.arange(len(people))
# performance = count_percentage.values()
#
# ax.barh(y_pos, performance, align='center')
# ax.set_yticks(y_pos)
# ax.set_yticklabels(people)
plt.show()
