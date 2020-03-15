# -----------------------------------------------------------
# Jack Yang Huang
# Search Engine Project
# -----------------------------------------------------------

from pymongo import MongoClient
from pprint import pprint
import json
from collections import defaultdict

DB_NAME = 'project3db'

"""
This class is responsible for handling all query needs from the user and the preprocessing.
"""
class Query:
    def __init__(self):
        self.client = MongoClient("localhost", 27017)
        self.db = self.client[DB_NAME]
        self.dict_paths = []
        
        try:
            with open("WEBPAGES_RAW/bookkeeping.json", "r", encoding="utf-8") as file:
                self.dict_paths = json.load(file)
                
        except IOError:
            print("Json file not found in the directory.")

        # Collection for the terms
        self.collection_terms = self.db['test_terms_v6']

        # Collection for the bi-grams
        self.collection_bigrams = self.db['test_bigrams_v6']

        # Collection for documents
        self.collection_docs = self.db['test_docs_v6']

    """
    This method uses an aggregation pipeline to get the number of documents
    related to the term (Size of postings array)
    """
    def postings_count(self):

        pipeline = [
            {
                '$project': {
                    '_id': 0, 
                    'term': '$term', 
                    'count': {
                        '$size': '$postings'
                    }
                }
            }
        ]
        result = defaultdict()
        for d in list(self.collection_terms.aggregate(pipeline)):
            result[d.get('term')] = d.get('count')

        return result


    """
    This method uses an aggregation pipeline to get the number of documents
    related to the bi-grams (Size of postings array for bi-grams)
    """
    def postings_bigrams_count(self):
        
        pipeline = [
            {
                '$project': {
                    '_id': 0, 
                    'term': '$term', 
                    'count': {
                        '$size': '$postings'
                    }
                }
            }
        ]
        result = defaultdict()
        for d in list(self.collection_bigrams.aggregate(pipeline)):
            result[d.get('term')] = d.get('count')

        return result


    """
    This method uses an aggregation pipeline to get a list of terms without
    the content of each posting. Used if none of the posting information is needed.
    """
    def get_dict_without_postings(self):
        pipeline = [
            {
                '$project': {
                    '_id': 0, 
                    'postings': 0
                }
            }
        ]
        return list(self.collection_terms.aggregate(pipeline))


    """
    This method uses an aggregation pipeline to get all the terms in the entire
    collection and returns them sorted alphabetically in ascending order in a list
    """
    def get_all_terms(self):
        pipeline = [
            {
                '$project': {
                    '_id': 0, 
                    'postings': 0
                }
            }, {
                '$sort': {
                    'term': 1
                }
            }
        ]
        return [d['term'] for d in list(self.collection_terms.aggregate(pipeline))]


    """
    This method uses an aggregation pipeline to get all the bi-grams in the entire
    collection and returns them sorted alphabetically in ascending order in a list
    """
    def get_all_bigrams(self):
        pipeline = [
            {
                '$project': {
                    '_id': 0, 
                    'postings': 0
                }
            }, {
                '$sort': {
                    'term': 1
                }
            }
        ]
        return [d['term'] for d in list(self.collection_bigrams.aggregate(pipeline, allowDiskUse = True))]


    """
    This method gets the total number of terms in the collection of terms.
    """
    def term_count(self):
        return self.collection_terms.count()


    """
    This metod gets the number of unique paths (URLs) in the collection of terms.
    """
    def doc_count(self):
        return len(self.collection_terms.distinct('postings.path_id'))


    """
    This metod gets the number of unique paths (URLs) in the collection of bi-grams.
    """
    def bigram_doc_count(self):
        return len(self.collection_bigrams.distinct('postings.path_id'))


    """
    This method uses an aggregation pipeline to get all the frequency of a term,
    which is sorted in descending order.
    Limit is the number of results that the user would like.

    This was used for Milestone 1.
    """
    def find_term_freq_desc(self, term: str, limit: int):
        pipeline = [
            {
                '$match': {
                    'term': term
                }
            }, {
                '$unwind': {
                    'path': '$postings'
                }
            }, {
                '$project': {
                    '_id': 0, 
                    'path_id': '$postings.path_id', 
                    'natural_freq': '$postings.natural_freq', 
                    #'positional_idx': '$postings.positional_idx',
                }
            }, {
                '$sort': {
                    'natural_freq': -1
                }
            }, {
                '$limit': limit
            }
        ]

        return list(self.collection_terms.aggregate(pipeline))


    """
    This method uses an aggregation pipeline to get all the postings (and it's content) of a term.
    
    This was used for Milestone 1.
    """
    def get_term(self, term: str):
        pipeline = [
            {
                '$match': {
                    'term': term
                }
            }, {
                '$unwind': {
                    'path': '$postings'
                }
            }, {
                '$project': {
                    '_id': 0, 
                    'path_id': '$postings.path_id', 
                    'tf_idf': '$postings.tf_idf', 
                    'tf': '$postings.tf', 
                    'idf': '$idf', 
                    'positional_idx': '$postings.positional_idx'
                }
            }
        ]
        return list(self.collection_terms.aggregate(pipeline))
        

    """
    This method uses an aggregation pipeline to get all the postings
    (and it's weighted frequency) of a term.
    """
    def get_weighted_freq(self, term: str):
        pipeline = [
            {
                '$match': {
                    'term': term
                }
            }, {
                '$unwind': {
                    'path': '$postings'
                }
            }, {
                '$project': {
                    '_id': 0, 
                    'path_id': '$postings.path_id', 
                    'weighted_freq': '$postings.weighted_freq', 
                }
            }
        ]
        return list(self.collection_terms.aggregate(pipeline))


    """
    This method uses an aggregation pipeline to get all the postings
    (and it's weighted frequency) of a bigram.
    """
    def get_bigram_freq(self, term):
        pipeline = [
            {
                '$match': {
                    'term': term
                }
            }, {
                '$unwind': {
                    'path': '$postings'
                }
            }, {
                '$project': {
                    '_id': 0, 
                    'path_id': '$postings.path_id', 
                    'bigram_wt_freq': '$postings.bigram_wt_freq', 
                }
            }
        ]
        return list(self.collection_bigrams.aggregate(pipeline))


    """
    This method uses an aggregation pipeline to calculate the document length
    for a multiword query:
        - Matches using an OR operator all the terms that the user searched.
        - Unwind the postings to individual objects in the aggregatio pipeline.
        - Projects (Only shows) the necessary information (TF-IDF and Path ID).
        - Group will do the following:
            - Add the number of documents where the searched terms were found
                (It will match the same path_ids, meaning it comes from the
                same document)
            - Add the TF-IDF values from each of the terms for every matching doc.
            - Starts calculating the doc length by finding the pow of 2 of the TF-IDF
                and adds the values from each of the terms.
        - Sorts the results by number of documents in descending order, and afterwards
            sorts by TF-IDF in descending order.
        - Finally it projects again to finalize the calculation of doc length by finding
            the square root of the summed TF-IDFs
    """
    def get_doc_length_tf_idf(self, terms):
        
        temp = []
        for t in terms:
            temp.append({'term': t })
        
        pipeline = [
            {
                '$match': {
                    '$or': 
                        temp
                }
            }, {
                '$unwind': {
                    'path': '$postings'
                }
            }, {
                '$project': {
                    '_id': 0, 
                    'path_id': '$postings.path_id', 
                    'tf_idf': '$postings.tf_idf'
                }
            }, {
                '$group': {
                    '_id': '$path_id', 
                    'documents': {
                        '$sum': 1
                    }, 
                    'tf_idf': {
                        '$sum': '$tf_idf'
                    }, 
                    'len_pow2': {
                        '$sum': {
                            '$pow': [
                                '$tf_idf', 2
                            ]
                        }
                    }
                }
            }, {
                '$sort': {
                    'documents': -1, 
                    'tf_idf': -1
                }
            }, {
                '$project': {
                    'documents': '$documents', 
                    'tf_idf': '$tf_idf', 
                    'len': {
                        '$sqrt': '$len_pow2'
                    }
                }
            }
        ]
        return list(self.collection_terms.aggregate(pipeline))


    """
    This method uses an aggregation pipeline to calculate the document length
    for a multiword query:
        - Matches using an OR operator all the terms that the user searched.
        - Unwind the postings to individual objects in the aggregatio pipeline.
        - Projects (Only shows) the necessary information (TF and Path ID).
        - Group will do the following:
            - Add the number of documents where the searched terms were found
                (It will match the same path_ids, meaning it comes from the
                same document)
            - Add the TF values from each of the terms for every matching doc.
            - Starts calculating the doc length by finding the pow of 2 of the TF
                and adds the values from each of the terms.
        - Sorts the results by number of documents in descending order, and afterwards
            sorts by TF in descending order.
        - Finally it projects again to finalize the calculation of doc length by finding
            the square root of the summed TF
    """
    def get_doc_length_tf(self, terms):
        
        temp = []
        for t in terms:
            temp.append({'term': t })
        
        pipeline = [
            {
                '$match': {
                    '$or': 
                        temp
                }
            }, {
                '$unwind': {
                    'path': '$postings'
                }
            }, {
                '$project': {
                    '_id': 0, 
                    'path_id': '$postings.path_id', 
                    'tf': '$postings.tf'
                }
            }, {
                '$group': {
                    '_id': '$path_id', 
                    'documents': {
                        '$sum': 1
                    }, 
                    'tf': {
                        '$sum': '$tf'
                    }, 
                    'len_pow2': {
                        '$sum': {
                            '$pow': [
                                '$tf', 2
                            ]
                        }
                    }
                }
            }, {
                '$sort': {
                    'documents': -1, 
                    'tf': -1
                }
            }, {
                '$project': {
                    'documents': '$documents', 
                    'tf': '$tf', 
                    'len': {
                        '$sqrt': '$len_pow2'
                    }
                }
            }
        ]
        return list(self.collection_terms.aggregate(pipeline))


    """
    This method uses an aggregation pipeline to get all the postings associated to
    the term and will return them organized in a dictionary to handling of the
    GET requests.
    """
    def get_term_postings(self, term: str):
        pipeline = [
            {
                '$match': {
                    'term': term
                }
            }, {
                '$unwind': {
                    'path': '$postings'
                }
            }, {
                '$project': {
                    '_id': 0, 
                    'path_id': '$postings.path_id', 
                    'tf': '$postings.tf', 
                    'tf_idf': '$postings.tf_idf', 
                    'positional_idx': '$postings.positional_idx'
                }
            }
        ]
        temp = list(self.collection_terms.aggregate(pipeline))
        dict_postings = defaultdict(dict)
        
        for path in temp:
            dict_postings[path['path_id']]['tf'] = path['tf']
            dict_postings[path['path_id']]['tf_idf'] = path['tf_idf']
            dict_postings[path['path_id']]['positional_idx'] = path['positional_idx']

        return dict_postings


    """
    This method uses an aggregation pipeline to get all the postings associated to
    the bi-gram and will return them organized in a dictionary to handling of the
    GET requests.
    """
    def get_bigram_postings(self, term):
        pipeline = [
            {
                '$match': {
                    'term': term
                }
            }, {
                '$unwind': {
                    'path': '$postings'
                }
            }, {
                '$project': {
                    '_id': 0, 
                    'path_id': '$postings.path_id', 
                    'tf': '$postings.tf', 
                    'tf_idf': '$postings.tf_idf', 
                }
            }
        ]
        temp = list(self.collection_bigrams.aggregate(pipeline))
        dict_postings = defaultdict(dict)
        
        for path in temp:
            dict_postings[path['path_id']]['tf'] = path['tf']
            dict_postings[path['path_id']]['tf_idf'] = path['tf_idf']

        return dict_postings


    """
    This method uses an aggregation pipeline to get all the documents and will
    return the data as a dictionary containing the following items for each document:
        - Path ID
        - URL
        - Page rank
        - Title
        - Snippet
    """
    def get_docs(self):
        pipeline = [
            {
                '$project': {
                    '_id': 0
                }
            }
        ]
        temp = list(self.collection_docs.aggregate(pipeline))
        dict_docs = defaultdict(dict)
        for path in temp:
            dict_docs[path.get('path_id')] = {'url':path.get('url'), 'page_rank': path.get('page_rank'), 'title': path.get('title'), 'snippet': path.get('snippet')}

        return dict_docs

    """
    This method prints the results in a file for the queried terms.

    This was used for Milestone 1
    """
    def print_urls(self, term, limit):
        # Saves the valid URL list to a text file
        try:
            with open('search_results.txt', 'a', encoding="utf-8") as file_results:
                
                if self.postings_count(term.lower()):

                    file_results.write("Search results for: {}\n".format(term))
                    file_results.write("Number of results: {}\n\n".format(self.postings_count(term.lower())[0].get("count")))
                    file_results.write("#\tFreq\tURL\n")

                    results = self.find_term_freq_desc(term.lower(), limit)

                    count = 1

                    for item in results:
                        # content = p.fetch_content(item.get("path_id"))
                        url = self.dict_paths.get(item.get("path_id"))
                        freq = item.get("natural_freq")

                        if len(url) > 80:
                            file_results.write("{}.\t{}\t{} ...\n".format( count, freq, url[:80] ))
                        else:
                            file_results.write("{}.\t{}\t{}\n".format( count, freq, url ))

                        count += 1

                    file_results.write("\n------------------------------------------------------------------------------" \
                                        + "-----------------------------------------\n")

                else:
                    file_results.write("Search results for: {}\n".format(term))
                    file_results.write("Number of results: 0\n")
                    file_results.write("\n------------------------------------------------------------------------------" \
                                        + "-----------------------------------------\n")
                    
        except IOError:
            print("Error writing valid URLs to text file")

    

if __name__ == "__main__":
    q = Query()
    templ = ['open']
    # templ = ['open', 'source', 'project']

    # print(q.get_doc_length(templ))

    # print(q.get_term_postings('open'))

    # print(q.get_docs())
    q.postings_count()

    # print(q.postings_count('open'))

    # q.term_count()
    # q.doc_count()

    # q.print_urls('Informatics', 20)
    # q.print_urls('Mondego', 20)
    # q.print_urls('Irvine', 20)

    # list_terms = q.get_all_terms()
    # print(list_terms)
    # print(q.get_all_terms())