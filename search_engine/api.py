# -----------------------------------------------------------
# Jack Yang Huang
# Search Engine Project
# -----------------------------------------------------------

from flask import Flask, request, Response
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS
from search import Search

app = Flask(__name__)
api = Api(app)

# Cross-origin resource sharing (CORS) allows request of restricted resources
# from another domain
cors = CORS(app, resources={r"/api*": {"origins": "*"}})

s = Search()
last_results = []
last_query = ""
last_number_results_found = 0
last_query_speed = 0
last_search_lemmatized = []

# Handling of the parameters from the URL
parser = reqparse.RequestParser()
parser.add_argument('query', type = str, required = True, help = "Enter query words")
parser.add_argument('start', type = int, required = True, help = "Enter start number")

class SearchAPI(Resource):
    def __init__(self):
        self.__query = parser.parse_args().get('query', None)
        self.__start = parser.parse_args().get('start', None)

    # This method handles the GET requests
    def get(self):
        global last_query
        global last_results 
        global last_number_results_found
        global last_query_speed
        global last_search_lemmatized

        # print("Query: "+self.__query)
        # print("Start: {}".format(self.__start))
        
        # If the query terms changed it will refresh the cache with new results
        if self.__query != last_query:
            last_query = self.__query
            temp = s.retrieve_results(self.__query)
            last_results = temp[0]
            last_number_results_found = temp[1]
            last_query_speed = temp[2]
            last_search_lemmatized = temp[3]

        results = s.construct_results(last_results, self.__start)

        return {'results':results,
                'number_results_found': last_number_results_found,
                'query_speed': last_query_speed,
                'search_lemmatized': last_search_lemmatized}
        

api.add_resource(SearchAPI, '/api')

if __name__ == '__main__':
    app.run(debug = True)