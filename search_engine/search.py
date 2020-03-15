# -----------------------------------------------------------
# Jack Yang Huang
# Search Engine Project
# -----------------------------------------------------------

import json
import math
from pymongo import MongoClient
from pprint import pprint
from time import perf_counter
from preprocessing import Preprocessing
from query import Query
from collections import defaultdict

DB_NAME = 'project3db'
PR_MULTIPLIER = 20          # Page rank multiplier that will add the value to the final score
                            # (0 for no effect, 10 for low, 25 for medium and > 100 for high)

BIGRAM_MULTIPLIER = 0.5     # Bi-gram multiplier alpha that will determine how much weighting the
                            # bi-gram score has in comparison to the regular scoring (total sums up to 1)

RESULTS_DISPLAYED = 20      # Number of results that are returned

"""
This class is responsible for handling all user based searches and
retrieving the top ranked results from the Mongo DB database
"""
class Search:
    def __init__(self):
        # MongoDB initialization
        self.client = MongoClient("localhost", 27017)
        self.db = self.client[DB_NAME]

        # Initialization of other modules
        self.p = Preprocessing()
        self.q = Query()

        # Cached data
        self.cached_dict = defaultdict(dict)    # Dictionary containing all the possible terms

        self.cached_docs = self.q.get_docs()    # Dictionary containing all paths, mappings to URLs,
        self.load_dict()                        # pagerank, title, and snippet for each document
        
    """
    This method is responsible for getting all the results for the search terms
    by using MongoDB's aggregation pipelines where it will query the results using
    an OR statement.

    MongoDB Aggregation/Pipeline (From Query: get_doc_length_tf_idf):
    -   Finds documents that match with at least 1 of the terms and will sum the number
    of documents it matches into a new field. The number of documents where the term/s
    appears in is sorted in descending order because the more documents it appears in, the
    more relevant is the document/page for the search.
    -   After sorting by number of documents, the aggregation will sort by TF-IDF (or TF
    depending on which SMART notation is being used) in descending order.

    Takes into consideration the bi-grams by using the bi-gram ratio for weighting.
    Adds in the page rank scores to each of the final scores of the document as a tiebreaker.

    Using weighting scheme ltc.ltc
    """
    def retrieve_results(self, search: str) -> list:
        
        # Start the stopwatch to measure the time it takes to retrieve the result
        # It is used in the front-end to show the user how fast it was. 
        total_start = perf_counter()

        list_tokens = self.p.tokenize_span(search)
        word_freq = self.p.word_frequency(list_tokens)
        bigram_freq = self.p.bigram_freq(search)

        search_lemmatized = search.split(" ")      # The search words in lemmatized form

        # Nested dictionary
        dict_query = defaultdict(dict)
        
        # Calculates the TF, DF, TF-IDF for all the queried words
        for term, freq in word_freq.items():
            # Adding terms to a set (For styling purposes in the front-end)
            search_lemmatized.append(term)

            # Checks if weighted frequency is 0, because log(0) = 1
            tf = 0
            if freq[0] != 0:
                tf = 1 + math.log10(freq[0])
            dict_query[term]['tf'] = tf
            if self.cached_dict.get(term):
                dict_query[term]['tf_idf'] = tf * self.cached_dict.get(term).get('idf')

        # Calculate query length
        query_length = 0
        for term in dict_query.values():
            if term.get('tf_idf'):
                query_length += pow((term.get('tf_idf')), 2)
        query_length = math.sqrt(query_length)

        # Calculate the Normalized (Cosine Similarity)
        for term in dict_query.values():
            if term.get('tf_idf'):
                term['cosine_sim'] = term['tf_idf'] / query_length

        # Fetch the data from MongoDB by using the aggregation pipeline
        # Sorted by TF-IDF in descending order, includes doc length
        doc_length = self.q.get_doc_length_tf_idf(list(word_freq.keys()))
        # doc_length = self.q.get_doc_length_tf(list(word_freq.keys()))

        final_result = []
        
        # If the search query is just 1 word, it means that the cosine similarity for the document is not calculated,
        # because the result would always be 1. It is multiplied by the query's IDF (It says cosine similarity,
        # but the rest of the values like query_length and TF would always be 1 since it is only 1 word)
        if len(list_tokens) == 1:
            # Score calcualtion with TF-IDF of the document and IDF of the query
            for path in doc_length:
                final_result.append([path['_id'], (path['tf_idf']) ])

        # If the search is more than 1 word
        else:
            # Nested dictionary for storing the scores of each term
            # (key = term, value = {nested dict containing tf_idf, etc})
            term_doc_dict = defaultdict(dict)
            # Fetch scores from MongoDB inverted index postings for each term
            for term in word_freq:
                term_doc_dict[term] = self.q.get_term_postings(term)

            # Nested dictionary for the bi-gram version
            bigram_doc_dict = defaultdict(dict)
            for bigram in bigram_freq:
                bigram_doc_dict[bigram] = self.q.get_bigram_postings(bigram)

            # Score calculation for each of the documents it found the query terms
            for path in doc_length:
                score = 0
                proximity_score = 0
                merged_idx = []
                # Will loop through each of the search terms and calculate the product between
                # the cosine similarity of the query and the cosine similarity of the document
                for term, values in term_doc_dict.items():
                    if path.get('_id') in values:
                        cosine_query = dict_query.get(term).get('cosine_sim')
                        cosine_doc = values.get(path.get('_id')).get('tf_idf') / path.get('len')
                        score += cosine_query * cosine_doc

                        # Positional index proximity
                        # merged_idx.append(values.get(path.get('_id')).get('positional_idx'))

                # Score calculation for the bi-gram version (Only uses TF-IDF)
                for bigram, values in bigram_doc_dict.items():
                    if path.get('_id') in values:
                        # Add weighted bigram to final score
                        score = (score * (1 - BIGRAM_MULTIPLIER)) + (values.get(path.get('_id')).get('tf_idf') * BIGRAM_MULTIPLIER)
                    
                final_result.append([path['_id'], score])

        # Page rank adjustment/tiebreaker by using the PR Multiplier
        # Loops through all the pages in the results to add in the page rank score
        for i in range(len(final_result)):
            if 'page_rank' in self.cached_docs.get(final_result[i][0]):
                page_rank = self.cached_docs.get(final_result[i][0]).get('page_rank') * PR_MULTIPLIER
                final_result[i][1] += page_rank

        # Sort all the adjusted results again as page rank could have potentially changed the ranks
        sorted_results = sorted(final_result, key = lambda x: x[1], reverse = True)

        # Stops the stopwatch/timer for calculating the query speed. Rounds to 2 decimals. 
        total_stop = perf_counter()
        query_speed = round(total_stop-total_start, 2)
        print("Query timer in seconds: {}".format(query_speed)) 

        return (sorted_results, len(sorted_results), query_speed, search_lemmatized)

    """
    This method will construct the results in a way that can be read in JSON for the api.
    It will paginate the results by only returning 20 results at a time using the 'start'
    argument as the starting point of the next 20 results.
    Returns a list of dictionaries containing the url, title, and the snippet of the document/page.
    """
    def construct_results(self, results: list, start: int) -> 'List of dictionaries': 
        paginated_results = results[start:start+RESULTS_DISPLAYED]
        complete_result = []

        for page in paginated_results:
            complete_result.append({'url':self.cached_docs.get(page[0]).get('url'),
                                    'title':self.cached_docs.get(page[0]).get('title'),
                                    'snippet':self.cached_docs.get(page[0]).get('snippet')})
        
        return complete_result


    """
    This method will load the dictionary to memory and it will contain the terms with their
    respective IDF score and postings count. This is needed to calculate the length of the
    query and the document.
    """
    def load_dict(self):
        list_terms = self.q.get_dict_without_postings()
        for term in list_terms:
            self.cached_dict[term['term']]['idf'] = term['idf']
            self.cached_dict[term['term']]['postings_count'] = term['postings_count']



if __name__ == "__main__":
    search = Search()
    # print(search.retrieve_results('computer science'))

    pprint(search.construct_results(search.retrieve_results('computer science'), 10))
