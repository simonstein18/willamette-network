import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
import pandas as pd
from bs4 import BeautifulSoup
import requests
from csv import writer
from validators import url


dict = {}


def check_valid(href_link):
    # this function makes sure it's not checking hrefs that are nonsense, such as links to emails, telephones, or other errors encountered during testing
    # returns true if the link should be a node
    if href_link is None:
        return False
    if (not url(href_link)) and (not href_link.startswith('mailto')) and (not href_link.startswith('tel')) and (not href_link.startswith('#')) and ('newwebreport' not in href_link) and ('error' not in href_link) and ('(' not in href_link):
        return True
    return False


def modify_link(og_link, new_link):
    # Since some hrefs can be absolute(href="admissions/index.html") or relative(href="../index.html"), we need to account for them
    # This function takes in those special hrefs and turns them into whole links
    # Ex: 'admissions/index.html' might turn into 'https://willamette.edu/computing/programs/computer-science-ms/index.html'
    count = new_link.count('../')
    if count > 0:
        return (og_link.rsplit('/', count+1)[0] + '/') + new_link.replace('../', '')
    else:
        return (og_link.rsplit('/', 1)[0] + '/') + new_link


def get_roots(link):
    # this function takes in a link(aka a site) and adds hrefs that are in it to a dictionary
    page = requests.get(link)
    soup = BeautifulSoup(page.content, 'html.parser')
    if link not in dict:
        dict[link] = []
    for a_link in soup.find_all('a'):
        href_link = a_link.get('href')
        if check_valid(href_link):
            updated_link = modify_link(link, href_link)
            if (updated_link not in visited):
                visited.append(updated_link)
                dict[link].append(updated_link)
                queue.append(updated_link)


queue = []
visited = []

starting_url = "https://willamette.edu/computing/programs/computer-science-ms/index.html"

queue.append(starting_url)

max_iterations = 50  # Set the maximum number of iterations
iteration_count = 0

# Code that loops through all the sites
while len(queue) != 0 and iteration_count < max_iterations:
    link = queue.pop(0)
    get_roots(link)
    iteration_count += 1


# Turns the dictionary of sites into a list of connected nodes for graphing purposes
def dict_to_list(d):
    result = []
    for key, values in d.items():
        for value in values:
            result.append([key[33:], value[33:]])
    return result


# Graphing the list
G = nx.Graph()
G.add_edges_from(dict_to_list(dict))
#nx.draw(G, with_labels=True, node_color='r', font_size=4)
# plt.show()

# Community Detection
iterations = 5
for i in range(iterations):
    edge_betweenness = nx.edge_betweenness_centrality(G).items()
    edge_to_delete = sorted(edge_betweenness, key=lambda pair: -pair[1])[0][0]

    G.remove_edge(*edge_to_delete)

    nx.draw(G, with_labels=True, node_color='r', font_size=4)
    plt.title('Step %s\nEdge %s Deleted' % (i, edge_to_delete), fontsize=20)

    plt.show()
