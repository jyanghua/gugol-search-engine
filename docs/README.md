# Gugol Search Engine


_Disclaimer: While the design of the UI is clearly based on Google, this project is not for commercialization or for-profit purposes. The main purpose of the project is to understand the system of a search engine and the process behind it._

## Summary

* Created a web crawler that would go through a set of URLs and HTML content in the subdomain of ics.uci.edu.
* Constructed the inverted index by using tokenization, filters, and lemmatization of the content with NLTK.
* Applied TF-IDF, cosine similarity (vectorization), and page ranking to calculation of the final scoring of query and document terms.
* Designed a RESTful backend server to manage the requests from the front-end and adjusted results to a custom pagination method.
* Implementation of the front-end using React, JavaScript, and Material UI to create a GUI resembling Google’s approach.
* Utilized: Python, NLTK, NetworkX, Flask-RESTful, MongoDB, JavaScript, React, Axios, Material UI.


## Table of contents

<!--ts-->
   * [Summary](#summary)
   * [Table of Contents](#table-of-contents)
   * [Screenshots](#ss)
   * [Process](#process)
      * [Pre-processing](#pre-processing)
        * [Web Crawling](#web-crawling)
        * [Inverted Index](#inverted-index)
      * [Ranking](#ranking)
      * [Database](#database)
      * [API](#api)
      * [Front-End](#front-end)
   * [Installation](#installation)
   * [Dependencies](#dependencies)
<!--te-->

## Screenshots

**Landing Page**
Landing page containing the logo, search bar, and search button. A search can be initiated by pressing the enter button or clicking the search button.
![Landing Page](/docs/screenshots/landing-page.jpg?raw=true)

**Search Page: "Informatics Donald Bren"**
After searching for a term, the website will query and retrieve the results from the database. The interface includes a top bar or header with the logo (Clicking it will take the user back to the home page), the search bar, and a clickable search button (Magnifying glass). The result includes statistics such as the estimated number of results and the time it took to query and calculate the ranking of the search terms. Additionally, the title of the result is underlined on hover and the relevant terms in the snippet are be bolded.
![Search Page](/docs/screenshots/informatics-donald-bren.jpg?raw=true)

**Search Page Bottom Pagination: "professor"**
Each page consists of 20 results and can be navigated through a pagination system where it changes the URL of the query.
![Search Page Bottom Pagination](/docs/screenshots/informatics-donald-bren.jpg?raw=true)

**Search Page Bottom Pagination (Page 13): "professor"**
For quick navigation it includes the first and last pages of the search result.
![Search Page Bottom Pagination Page 13](/docs/screenshots/professor-pagination-13.jpg?raw=true)

## Process


### Pre-processing


#### Web Crawling


#### Inverted Index


### Ranking


### Database


### API


### Front-End


## Installation


## Dependencies
