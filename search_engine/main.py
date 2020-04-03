# -----------------------------------------------------------
# Jack Yang Huang
# Search Engine Project
# -----------------------------------------------------------

import sys
import string
import json
import logging
import time
import math
from time import perf_counter
from pymongo import MongoClient
from pprint import pprint
from preprocessing import Preprocessing
from query import Query
from storage import Storage
logger = logging.getLogger(__name__)

SNIPPET_MAX = 350 # The maximum number of characters for the snippet
TITLE_MAX = 60 # The maximum number of characters for the title
WEIGHT_TITLE = 6 # Weight for title token frequency
WEIGHT_H1H2 = 3 # Weight for h1h2 token frequency
WEIGHT_H3H6 = 2 # Weight for h3h6 token frequency
WEIGHT_STRONG = 1 # Weight for strong token frequency
WEIGHT_ANCHOR = 1 # Weight for anchor token frequency

paths_list = []
dict_path = {}


def read_json() -> 'List: file paths':
    """
    Gets the file paths to each document from the json file.
    Starting point to iterate through the entire corpus.
    """

    global paths_list
    global dict_path

    try:
        with open("WEBPAGES_RAW/bookkeeping.json", "r", encoding="utf-8") as file:
            dict_path = json.load(file)
            
        for item in dict_path:
            paths_list.append(item)

    except IOError:
        print("Json file not found in the directory.")
    
    # Sorts the listing as the json data is not correctly ordered
    paths_list = sorted(paths_list, key=lambda d: tuple(map(int, d.split('/'))))
    


def preprocess_all(p: Preprocessing(), s: Storage()):
    """
    This method retrieves all the content, proprocess them, and insert the
    relevant data to the database.
    """

    corpus_count = 0

    # Loops through the entire list of paths (corpus)
    while corpus_count < len(paths_list):
        path = paths_list[corpus_count]

        # Fetches the content doing HTML validation, fixing broken tags, and organizing the
        # text into different categories as seen in the Preprocessing module.
        content = p.fetch_content(path)
        title = content.get('title')
        body = content.get('body')
        paragraph = content.get('paragraph')

        # Insert title and snippet to document collection in MongoDB
        if title is None and body is not None and paragraph is not None:
            s.insert_title_snippet(path,
                            ' '.join(body.encode("ascii", errors="ignore").decode().split())[:TITLE_MAX],
                            ' '.join(paragraph.encode("ascii", errors="ignore").decode().split())[:SNIPPET_MAX])
        elif title is not None and paragraph is not None:
            s.insert_title_snippet(path,
                            ' '.join(title.encode("ascii", errors="ignore").decode().split())[:TITLE_MAX],
                            ' '.join(paragraph.encode("ascii", errors="ignore").decode().split())[:SNIPPET_MAX])
        elif title is not None and paragraph is None and body is not None:
            s.insert_title_snippet(path,
                            ' '.join(title.encode("ascii", errors="ignore").decode().split())[:TITLE_MAX],
                            ' '.join(body.encode("ascii", errors="ignore").decode().split())[:SNIPPET_MAX])
        elif title is not None and paragraph is None and body is None:
            s.insert_title_snippet(path,
                            ' '.join(title.encode("ascii", errors="ignore").decode().split())[:TITLE_MAX],'')                    


        # Tokenization and Lemmatization with word frequency
        title_tokens = p.tokenize_span(title)
        title_freq = p.word_frequency(title_tokens)
        body_tokens = p.tokenize_span(body)
        body_freq = p.word_frequency(body_tokens)
      
        # Fix the title positional index offset
        if title_tokens:
            title_offset = len(title_tokens[-1][0]) + title_tokens[-1][1]
        
            for value in body_freq.values():
                for pos in value[1]:
                    pos += title_offset

        # Weighted frequency
        h1h2_freq = p.word_frequency(p.tokenize(content.get('h1h2')))
        h3h6_freq = p.word_frequency(p.tokenize(content.get('h3h6')))
        strong_freq = p.word_frequency(p.tokenize(content.get('strong')))
        anchor_freq = p.word_frequency(p.tokenize(content.get('anchor')))

        # Weighting the diffrent types of text
        weighted_freq = {}

        for key, value in title_freq.items():
            if key not in weighted_freq:
                weighted_freq[key] = value[0]
            else:
                weighted_freq[key] += value[0] * WEIGHT_TITLE

        for key, value in body_freq.items():
            if key not in weighted_freq:
                weighted_freq[key] = value[0]
            else:
                weighted_freq[key] += value[0]

        for key, value in h1h2_freq.items():
            if key not in weighted_freq:
                weighted_freq[key] = value * WEIGHT_H1H2
            else:
                weighted_freq[key] += value * WEIGHT_H1H2

        for key, value in h3h6_freq.items():
            if key not in weighted_freq:
                weighted_freq[key] = value * WEIGHT_H3H6
            else:
                weighted_freq[key] += value * WEIGHT_H3H6

        for key, value in strong_freq.items():
            if key not in weighted_freq:
                weighted_freq[key] = value * WEIGHT_STRONG
            else:
                weighted_freq[key] += value * WEIGHT_STRONG

        for key, value in anchor_freq.items():
            if key not in weighted_freq:
                weighted_freq[key] = value * WEIGHT_ANCHOR
            else:
                weighted_freq[key] += value * WEIGHT_ANCHOR

        natural_freq = p.word_frequency(title_tokens + body_tokens)
        
        # Bi-grams / Bi-words
        title_bigram = p.bigram_freq(content.get('title'))
        body_bigram = p.bigram_freq(content.get('body'))
        
        # Weighting the title in the bigram, merge with body
        for key in title_bigram:
            if key in body_bigram:
                body_bigram[key] += WEIGHT_TITLE
            else:
                body_bigram[key] = WEIGHT_TITLE

        # Inserting inverted index data to MongoDB
        if natural_freq and weighted_freq:
            s.insert_posting(path, natural_freq, weighted_freq)

        # Inserting bigram to separate index collection
        if body_bigram:
            s.insert_posting_bigram(path, body_bigram)

        corpus_count = corpus_count + 1
        logger.info("Processed Path {} ... Fetched: {} ... Percentage: {}%".format(
            path, corpus_count, round((corpus_count/len(paths_list)) * 100 , 2)))



def calculate_scores(s: Storage(), q: Query()):
    """
    This method calculates all the terms scoring for the TF, IDF, and TF-IDF.
    Additionally, it will insert all the scores to the MongoDB collection of terms.
    """

    list_terms = q.get_all_terms()
    dict_postings_count = q.postings_count()
    count_unique_paths = q.doc_count()
    counter = 0

    # Calculate Term Frequency and IDF for all terms and insert to the DB
    for term in list_terms:
        # Retrieve the weighted frequencies from the database
        list_weighted_freq = q.get_weighted_freq(term)
        # Calculate Inverted Document Frequency for all terms and insert IDF to database
        idf = math.log10( count_unique_paths / dict_postings_count.get(term))

        scores = {}
        for path_dict in list_weighted_freq:
            # Checks if weighted frequency is 0, because log(0) = 1
            tf = 0
            if path_dict.get("weighted_freq") != 0:
                tf = 1 + math.log10( path_dict.get("weighted_freq") )
            scores[path_dict.get("path_id")] = { "tf" : tf, "tf_idf" : (tf * idf) }
        
        s.insert_scores(term, idf, dict_postings_count.get(term), scores)
        counter = counter + 1
        logger.info("Processed Term {} ... Fetched: {} ... Percentage: {}%".format(
        term, counter, round((counter/len(list_terms)) * 100 , 2)))



def calculate_scores_bigrams(s: Storage(), q: Query()):
    """
    This method calculates all the bi-grams scoring for the TF, IDF, and TF-IDF.
    Additionally, it will insert all the scores to the MongoDB collection of bi-grams.
    """    

    # Calculate Term Frequency and IDF for all bigrams and insert to the DB
    list_bigrams = q.get_all_bigrams()
    dict_postings_bigrams_count = q.postings_bigrams_count()
    count_unique_paths_bigrams = q.bigram_doc_count()
    counter = 0

    for term in list_bigrams:
        # Retrieve the weighted frequencies from the database
        list_bigram_freq = q.get_bigram_freq(term)
        # Calculate Inverted Document Frequency for all bigrams and insert IDF to database
        idf = math.log10(count_unique_paths_bigrams / dict_postings_bigrams_count.get(term))
        
        scores = {}
        for path_dict in list_bigram_freq:
            # Checks if weighted frequency is 0, because log(0) = 1
            tf = 0
            if path_dict.get("bigram_wt_freq") != 0:
                tf = 1 + math.log10( path_dict.get("bigram_wt_freq"))
            scores[path_dict.get("path_id")] = { "tf" : tf, "tf_idf" : (tf * idf) }

        s.insert_scores_bigrams(term, idf, dict_postings_bigrams_count.get(term), scores)
        counter = counter + 1       
        logger.info("Processed Bi-gram {} ... Fetched: {} ... Percentage: {}%".format(
        term, counter, round((counter/len(list_bigrams)) * 100 , 2)))


def create_database_docs(s: Storage(), q: Query()):
    """
    This method will insert all the documents/pages (With Path ID and respective URLs)
    to the MongoDB collection of documents.
    """

    s.insert_documents(dict_path)
    

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s (%(name)s) %(levelname)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',
                        level=logging.INFO)
    read_json()

    p = Preprocessing()
    s = Storage()
    q = Query()

    # Correct order to create inverted index and calculate all scores
    create_database_docs(s, q)
    preprocess_all(p, s)
    calculate_scores(s, q)
    calculate_scores_bigrams(s, q)
    # Finally calculate the page rank by running the pagerank.py module
