# -----------------------------------------------------------
# Jack Yang Huang
# Search Engine Project
# -----------------------------------------------------------

from pymongo import MongoClient, UpdateOne, ASCENDING, DESCENDING
from pymongo.errors import BulkWriteError
from pprint import pprint

DB_NAME = 'project3db'

class Storage:
    """
    This class is responsible for handling all database storage needs
    Using MongoDB and storing data locally.

    Dependencies:
        - MongoDB installed (Compass to look at the data through GUI)
        - pymongo for Python
    """

    def __init__(self):
        self.client = MongoClient("localhost", 27017)
        self.db = self.client[DB_NAME]

        # Collection for the terms
        self.collection_terms = self.db['test_terms_v6']

        # Collection for the bi-grams
        self.collection_bigrams = self.db['test_bigrams_v6']

        # Collection for documents
        self.collection_docs = self.db['test_docs_v6']


    def insert_scores(self, term, idf, count, scores):
        """
        This method inserts all the calculated scores to the MongoDB collection of Terms.
            - IDF for each term
            - TF for each posting
            - TF-IDF for each posting
        It uses unordered bulk insertion to optimize the speed of data insertion.
        """
        
        try:
            self.collection_terms.update_one(
                { "term" : term },
                { "$set" : { "idf" : idf, "postings_count" : count }}
            )
            
            operations = []
            for path_id, value in scores.items():
                operations.append( UpdateOne(
                    { "term" : term , "postings.path_id" : path_id},
                    { "$set" : { "postings.$.tf" : value.get("tf"),
                    "postings.$.tf_idf" : value.get("tf_idf") }}
                ))

            self.collection_terms.bulk_write(operations, ordered = False)
        except BulkWriteError as bwe:
            pprint(bwe.details)

    def insert_scores_bigrams(self, term: str, idf: float, count: int, scores: dict):
        """
        This method inserts all the calculated scores to the MongoDB collection of Bi-grams.
            - IDF for each term
            - TF for each posting
            - TF-IDF for each posting
        It uses unordered bulk insertion to optimize the speed of data insertion.
        """
        
        try:
            self.collection_bigrams.update_one(
                { "term" : term },
                { "$set" : { "idf" : idf, "postings_count" : count }}
            )

            operations = []
            for path_id, value in scores.items():
                operations.append( UpdateOne(
                    { "term" : term , "postings.path_id" : path_id},
                    { "$set" : { "postings.$.tf" : value.get("tf"),
                    "postings.$.tf_idf" : value.get("tf_idf") }}
                ))

            self.collection_bigrams.bulk_write(operations, ordered = False)
        except BulkWriteError as bwe:
            pprint(bwe.details)
        

    def insert_posting(self, id: str, posting: dict, weighted_freq: dict):
        """
        This method will insert all the postings of a page to the collection of Terms.
            - Adds the ID (path ID)
            - Adds the natural frequency of the term occurrences
            - Adds the weighted frequency of the term occurrences.
            - Adds an array containing the positional index of each of the term occurrences.
        It uses unordered bulk insertion to optimize the speed of data insertion.
        """

        try:
            # Creation of MongoDB index to speed-up insertion and querying.
            # If it already exists it will be ignored.
            self.collection_terms.create_index([ ("term", ASCENDING) ])

            operations = []
            for key, value in posting.items():
                operations.append( UpdateOne(
                    { "term" : key },
                    { "$push" : 
                        { "postings" :
                            { "path_id" : str(id),
                            "natural_freq" : value[0],
                            "positional_idx" : value[1],
                            "weighted_freq" : weighted_freq.get(key) }}},
                    upsert = True
                ))

            self.collection_terms.bulk_write(operations, ordered = False)
        except BulkWriteError as bwe:
            pprint(bwe.details)

    def insert_posting_bigram(self, id, posting: dict):
        """
        This method will insert all the postings of a page to the collection of Bi-grams.
            - Adds the ID (path ID)
            - Adds the weighted frequency of the term occurrences (title and body weights)
        It uses unordered bulk insertion to optimize the speed of data insertion.
        """

        try:
            # Creation of MongoDB index to speed-up insertion and querying.
            # If it already exists it will be ignored.
            self.collection_bigrams.create_index([ ("term", ASCENDING) ])

            operations = []
            for key, value in posting.items():
                operations.append( UpdateOne(
                    { "term" : key },
                    { "$push" : 
                        { "postings" :
                            { "path_id" : str(id),
                            "bigram_wt_freq" : value }}},
                    upsert = True
                ))

            self.collection_bigrams.bulk_write(operations, ordered = False)
        except BulkWriteError as bwe:
            pprint(bwe.details)


    def insert_documents(self, dict_path: dict):
        """
        This method will insert all the path ID's and their respective URLs to the
        collection of documents. This is to mirror the Bookeeping JSON file stored locally.
        Will be needed to store additional information that will be added such as page rank.
        It uses unordered bulk insertion to optimize the speed of data insertion.
        """

        try:
            # Creation of MongoDB index to speed-up insertion and querying.
            # If it already exists it will be ignored.
            self.collection_docs.create_index([ ("path_id", ASCENDING),
                                                 ("url", ASCENDING)])
            
            operations = []
            for path_id, url in dict_path.items():
                operations.append( UpdateOne(
                    { "path_id" : path_id },
                    { "$set" :
                        {
                            "url" : url
                        }
                    },
                    upsert = True
                ))

            self.collection_docs.bulk_write(operations, ordered = False)
        except BulkWriteError as bwe:
            pprint(bwe.details)


    def insert_pagerank(self, page_rank: dict):
        """
        This method will insert the page rank scores of each URL or path ID to the
        collection of documents.
        It uses unordered bulk insertion to optimize the speed of data insertion.
        """

        try:
            # Creation of MongoDB index to speed-up insertion and querying.
            # If it already exists it will be ignored.
            self.collection_docs.create_index([ ("url", ASCENDING) ])

            operations = []
            for url, rank in page_rank.items():
                operations.append( UpdateOne(
                    { "url" : url },
                    { "$set" : { "page_rank" : rank }}
                ))

            self.collection_docs.bulk_write(operations, ordered = False)
        except BulkWriteError as bwe:
            pprint(bwe.details)

    def insert_title_snippet(self, path: str, title: str, snippet: str):
        """
        This method inserts a the title and the snippet of each document or page
        to the collection of documents in MongoDB
        """
        
        # Creation of MongoDB index to speed-up insertion and querying.
        # If it already exists it will be ignored.
        self.collection_docs.create_index([ ("path_id", ASCENDING) ])

        self.collection_docs.update_one(
            { "path_id" : path },
            { "$set" : 
                { 
                    "title" : title,
                    "snippet" : snippet
                }
            }
        )

        

if __name__ == "__main__":
    s = Storage()

