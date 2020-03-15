# -----------------------------------------------------------
# Jack Yang Huang
# Search Engine Project
# -----------------------------------------------------------

import networkx as nx
from storage import Storage
from urllib.request import urljoin
from bs4 import BeautifulSoup
import json
import re
from lxml import html
from pprint import pprint

# Regex that will match if a URL contains a protocol
regex_protocol = re.compile(r'https?://')

"""
Gets the file paths and url's to each document from the json file.
Starting point to iterate through the entire corpus.
"""
def read_json() -> 'Dict: {path : url}':

    try:
        with open("WEBPAGES_RAW/bookkeeping.json", "r", encoding="utf-8") as file:
            data = json.load(file)
            return data

    except IOError:
        print("Json file not found in the directory.")

"""
This method will create a dictionary of URLs as key, and a list of URLs it points towards
as value.
It will not add URLs that are external to the current corpus of URLs or Path IDs.
"""
def outgoing_links(dict_corpus: dict) -> dict:

    dict_outgoing = {}
    raw = ""
    count = 0

    try:
        # Loops through each document or page
        for path, url in dict_corpus.items():
        
            with open("WEBPAGES_RAW/{}".format(path), "r", encoding="utf-8") as html_file:
                raw = html_file.read()

            soup_lxml = BeautifulSoup(raw, 'lxml')
            
            # List of outgoing links
            list_links = []

            for link in soup_lxml.find_all('a', href=True):
                
                # If a URL starts with a protocol, it removes it by using regex.
                temp_link = link['href']
                if temp_link.startswith('http'):
                    temp_link = re.sub(regex_protocol, '', temp_link)
                else:
                    temp_link = urljoin(url, temp_link)

                # Checks if the URL links to the set of URLs of the corpus.
                # Only adds if it is True, else it means it links to an external page.
                if not temp_link == url and temp_link in dict_corpus.values():
                    list_links.append(temp_link)

                # print(list_links)

            dict_outgoing[url] = list_links
            count += 1
            print("Count: {} ... Progress: {}%".format(
                count, round(count/len(dict_corpus) * 100, 2)))

    except IOError:
        print("HTML file not found in the directory.")

    return dict_outgoing


if __name__ == "__main__":
    s = Storage()
    dict_path = read_json()
    outgoing = outgoing_links(dict_path)
    G = nx.DiGraph(outgoing)
    page_rank = nx.pagerank(G, alpha = 0.9)
    s.insert_pagerank(page_rank)

    # print("Page Rank: {}".format())


    

