# Gugol Search Engine


*Disclaimer: While the design of the UI is clearly based on Google, this project is not for commercialization or for-profit purposes. The main purpose of the project is to understand the system of a search engine and the process behind it without using libraries such as ElasticSearch.*

## Summary

* Tests were done using a static corpus that was previously crawled, which consisted of HTML files in a contained subdomain (ics.uci.edu).
* Constructed the inverted index by using tokenization, filters, and lemmatization of the content with NLTK.
* Applied TF-IDF, cosine similarity (vectorization), and page ranking to calculation of the final scoring of query and document terms.
* Designed a RESTful backend server to manage the requests from the front-end and adjusted results to a custom pagination method.
* Implementation of the front-end using React, JavaScript, and Material UI to create a GUI resembling Google’s approach.
* Utilized: Python, NLTK, NetworkX, Flask-RESTful, MongoDB, JavaScript, React, Axios, Material UI.


## Table of Contents

<!--ts-->
   * [Summary](#summary)
   * [Table of Contents](#table-of-contents)
   * [Screenshots](#ss)
   * [Process](#process)
      * [Pre-processing](#pre-processing)
        * [Web Crawling](#web-crawling)
        * [HTML Parsing](#html-parsing)
        * [Tag Categorization](#tag-categorization)
        * [Tokenization and Lemmatization](#tokenization-lemmatization)
        * [Inverted Index](#inverted-index)
        * [Calculating Scores](#calculating-scores)
      * [Ranking and Querying](#ranking)
        * [PageRank](#page-rank)
      * [Database](#database)
      * [API](#api)
      * [Front-End](#front-end)
   * [Installation](#installation)
   * [Dependencies](#dependencies)
<!--te-->

## Screenshots

**Landing Page**

Landing page containing the logo, search bar, and search button. A search can be initiated by pressing the enter button or clicking the search button.<br><br>
![Landing Page](/docs/screenshots/landing-page.jpg?raw=true)<br>

**Search Page: "Informatics Donald Bren"**

After searching for a term, the website will query and retrieve the results from the database. The interface includes a top bar or header with the logo (Clicking it will take the user back to the home page), the search bar, and a clickable search button (Magnifying glass). The result includes statistics such as the estimated number of results and the time it took to query and calculate the ranking of the search terms. Additionally, the title of the result is underlined on hover and the relevant terms in the snippet are be bolded.<br><br>
![Search Page](/docs/screenshots/informatics-donald-bren.jpg?raw=true)<br>

**Search Page Bottom Pagination: "professor"**

Each page consists of 20 results and can be navigated through a pagination system where it changes the URL of the query.<br><br>
![Search Page Bottom Pagination](/docs/screenshots/informatics-donald-bren.jpg?raw=true)<br>

**Search Page Bottom Pagination (Page 13): "professor"**

For quick navigation it includes the first and last pages of the search result.<br><br>
![Search Page Bottom Pagination Page 13](/docs/screenshots/professor-pagination-13.jpg?raw=true)<br>

**1 Minute Demo**

[![Watch the video](/docs/screenshots/demo-preview.jpg?raw=true)](https://streamable.com/u49vx)

<a href="https://streamable.com/u49vx" target="_blank">
  <img width="220" height="250" border="0" align="center"  src="/docs/screenshots/demo-preview.jpg?raw=true"/>
</a>


## Process


### Pre-processing

The pre-processing part of the search engine will encompass everything related to analyzing the content from the websites or pages and extracting relevant information such as the frequency of the terms and positional index of each word. This data is later used to calculate scores that will speed up the process of finding the websites that rank the highest according to the search terms.

#### Web Crawling

The "web" crawling part has been excluded from this final part of the project as the search engine tests were done on a static corpus that was previously downloaded. This is mainly done to avoid any kind of disruptions and denial of access while doing live web crawling.

The concept behind web crawling relies on having a starting point or domain and adding all the outgoing links on the page to a queue of URLs. Once all the outgoing links from a page is added to the queue, it will continue to the next one and so on. To make sure it doesn't go over the ones that were already visited, there will be a set/list containing the URLs that were visited.

The URLs also must go through a filtering mechanism to exclude URLs that are traps and could potentially stop the progress of the web crawler or add duplicate content to the index of the search engine. These URLs include dynamically generated URLs such as calendars or events, e-commerce carts, account settings, scripts, sort and filtering systems, user sessions, and many other custom URLs generated by the server. The most common patterns are using parameters, repetitive subdirectories and patterns, and duplicate meta descriptions. A lot of the traps also include websites that constantly links to its own content.

#### HTML Parsing

All the HTML content will have to be parsed correctly to ensure the extraction of the text stays relevant to what the users are looking for. During the HTML parsing, it will go through a HTML validator by using the library TidyLib which detects which parts of the HTML content has broken tags and fix them by adding the corresponding closing or opening missing tags. Additionally, during the parsing, it will assess content from websites that include an extremely high amount of numbers as content, or pages that have an abnormally large body text (greater than 5 MB of text). Other content that is stripped off the raw HTML file are the scripts, javascript, and styling tags.

#### Tag Categorization

Beautiful soup 4 and LXML are used primarily to categorize the content of the HTML file into 6 categories which will be useful for scoring and having different weighting schemes to construct the inverted index. The 6 categories from most important to least important are:

1. Title: TITLE
2. H1-H2: H1, H2
3. H3-H6: H3, H4, H5, H6
4. Strong: STRONG, B, EM, I, U, DL, OL, UL
5. Anchor words (Links): A
6. Plain text or body: The rest

#### Tokenization and Lemmatization

The process of tokenization is done by using the NLTK library which will separate the text into words and include the position it was found. The structure used is a list of tuples that contain the word and the positional index it was found. After the tokenization, the following step is the lemmatization and frequency count. In this case, it will not go through the word stemming process as it will considerably impact the result of the search in this particular case. The lemmatization uses the WordNetLemmatizer and NLTK to reduce the number of tokens that are indexed. The final filtering process includes removing all commong stop words, words that are shorter than 4 characters, and characters that are not part of ASCII.

#### Inverted Index

Two inverted indexes are created to add different weighting schemes and robustness to the search engine. The main inverted index contains each term as an MongoDB document followed by a list of postings where each element or node represents the page (URL) it was found on. The other inverted index is used for bi-grams, which allows a more precise ranking of queries that contain two words that are next to each other. The implementation of a bi-gram is more expensive in terms of capacity as it roughly takes up 10 times more disk space compared to the regular inverted index.

#### Calculating Scores

After creating the inverted index, the scores have to be calculated and stored in the database under each term's posting. The trade-off between calculating the scores pre-querying versus calculating it post-query in a real scenario has to do with how hard it is to maintain live content updated and the time it takes to retrieve the ranked results. In this case, all possible calculations that can be done pre-querying, will be stored in the database to increase the look-up speed for a slower indexing process. The scores were calculated using the logarithmic approach for normalization:

1. TF (Term Frequency): How frequent are the terms on each document (page)
2. IDF (Inverted Document Frequency): How rare is the term in relation to the others
3. TF-IDF (Term Frequency - Inverted Document Frequency): Dot product of both scores<br>

![Example of a term and it's posting](/docs/screenshots/informatics-mongodb.jpg?raw=true)<br>

For the bi-gram inverted index, the only score that was calculated was the Term Frequency due to space concerns.

### Ranking and Querying

Once all the pre-processing is finalized there is nothing else that can be calculated before the user inputs the search terms. Before ranking the search terms, these must be treated the same way the pre-processing dealt with the content of the web pages. It must go through the steps of tokenization, lemmatization, and filtration of unnecessary words, with the end goal of matching what is stored on the inverted index. It has to be done in parallel with the bi-gram version as both scores are needed to rank search terms containing more than 1 term or word.

The SMART notation of this search engine is ltc.ltc, meaning that both document and query will be treated with the same exact weightings. For this notation it uses logarithmic TF, logarithmic IDF, and cosine normalization. A slight variance of the version was tested (lnc.ltc) but it resulted in slightly worse results in comparison with the use of IDF for documents. Cosine normalization is used to calculate the final scores of the documents and query terms. Cosine normalization uses vectorization to find how close the query terms match the terms that can be found in a document (page).

The convenience of using MongoDB and aggregations is retrieving the data as organized and sorted as possible. This method uses an aggregation pipeline to calculate the document length for a multiword query:
1. Matches using an OR operator all the terms that the user searched.
2. Unwind the postings to individual objects in the aggregatio pipeline.
3. Projects (Only shows) the necessary information (TF and Path ID).
4. Group will do the following:
    * Add the number of documents where the searched terms were found
        (It will match the same path_ids, meaning it comes from the
        same document)
    * Add the TF values from each of the terms for every matching doc.
    * Starts calculating the doc length by finding the pow of 2 of the TF
        and adds the values from each of the terms.
5. Sorts the results by number of documents in descending order, and afterwards
    sorts by TF in descending order.
6. Finally it projects again to finalize the calculation of doc length by finding
    the square root of the summed TF

```python
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
```

#### PageRank

Finally, before retrieving the URLs that are scored the highest, the PageRank of each URL is used as a tiebreaker. PageRank will score pages that are more important in a higher position as these are the ones that other pages point towards (outgoing links). If other reputable pages point towards a single page, it means that they think highly of it. The PageRank is another calculation that is done pre-querying as it depends on analyzing the outgoing links of each page and creating a graph where each node represents a page URL, and the edges point towards another page it links to. For the creation of the graph and calculation of PageRank, the library NetworkX was used.


### Database

The database chosen for the project was MongoDB as the NoSQL and JSON format goes well with the data models used throughout the creation of the index and the retrieval of the search results. The look-up speed for ranking and querying proved to be faster than other type of storage methods, especially after the creation of MongoDB indexes such as Term (which would be the ideal Primary Key for the inverted indexes). A third MongoDB collection was added to keep the PageRank scores and other type of metadata related to a page (or document).

The following models were used to store additional data that was collected after pre-processing. This proves useful if there's a requirement to recalculate scores based on another style of weighting for search engines.<br>

![MongoDB Schema](/docs/screenshots/diagram-mongodb.JPG?raw=true)<br>

### API

The API was created using Flask-RESTful and it was designed to handle simple parameters from the URL. The first parameter is 'query' containing the search terms, and the second parameter is 'start' which is the number of the search result that the specific page will start displaying. This means that the API can handle pagination, but the system could be vastly improved by using a library that would automatically paginate it. For demostration purposes, since it is done on a local machine it would cache the last searched results, but in a real scenario when prompting a change of page, it would query the database once again and only retreive the information in batches.


### Front-End

By using React and MaterialUI, the goal of re-creating the front-end as a simple UI extremely similar to the Google search engine was easily achieved. Axios is a library used to make HTTP requests to the API (using promises) and additionally it facilitates the handling of the incoming data as JSON. React router was used for the management of query parameters and pagination purposes. The interaction of the interface feels familiar to the existing solutions on the market and it is easy to navigate. The most important feature of the web app is the responsiveness to changes of screen resolution.

## Installation

Unfortunately for the installation of the search engine, the corpus containing the HTML files is required, along with the mapping of the files to iterate through the corpus. With a valid corpus, the main.py module would handle the creation and calculation of the inverted indexes and add them to a MongoDB database. With this, api.py must be running and for testing purposes Yarn or npm must be used to create a development build of the React app.

## Dependencies

**Search Engine:**
* Python 3 (3.8 was used)
* TidyLib
* BeautifulSoup4
* LXML
* NLTK
* NetworkX
* pymongo

**API:**
* Flask
* Flask-RESTful
* Flask CORS

**Front-end:**
* node.js
* Yarn/npm
* React
* React Router
* MaterialUI
* Axios
* Lodash

**Database:**
* MongoDB