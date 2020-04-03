# -----------------------------------------------------------
# Jack Yang Huang
# Search Engine Project
# -----------------------------------------------------------

import json
import lxml
import nltk

import os #testing file size small 1722 bytes(4kb) med 13041 bytes (16kb) # 115KB~111K BYTES
from tidylib import tidy_document # pip install pytidylib / Requires tidy.dll
from pprint import pprint
import re
from bs4 import BeautifulSoup
from collections import defaultdict
from lxml import html
from nltk.util import ngrams
# nltk.download('wordnet') # Download wordnet dependency if it's the first time running

FILE_SIZE_CAP = 500000 # File size cap for the filtering: 5 MegaBytes
NUMBER_ALPHA = 0.20

# Regex compiling

# Finds words that are only numbers or decimals/float (including negative)
regex_numbers = re.compile(r"-?\b\d*\.?\d+(e(\+|-)\d*)?\b")

# Finds all the links that contain common extensions or files
regex_links = re.compile(r"(?:(?:http|https):\/\/)?([-a-zA-Z0-9.]{2,256}\.[a-z]{2,4})\b(?:\/[-a-zA-Z0-9@:%_\+.~#?&//=]*)?")


class Preprocessing:
    """
    This class is responsible for handling all document preprocessing.
    Includes fetching the content, fixing broken tags, separating the content into
    different categories, tokenizing (different types), lemmatization, porter stemmer, 
    and word frequency.
    """

    def __init__(self):
        self.stop_words = set()
        # By using the lemmatizer for the first time it will load WordNet into memory.
        # This is to speedup the search query by 1s (Which is the time it takes to load
        # WordNet into memory)
        nltk.WordNetLemmatizer().lemmatize("preloading")

        # Load all the stop words from the text file to the set
        try:
            with open("stopwords.txt", "r", encoding="utf-8") as file:
                for word in file:
                    self.stop_words.add(word.strip())
        except IOError:
            print("Stop words file not found in the directory.")


    
    def fetch_content(self, path: str) -> 'Dict{id, len_doc, broken_body, number_alpha_ratio,' \
                                            + 'removed_numbers, title, body, h1h2, h3h6, strong, anchor, paragraph}':
        """
        This method will fetch the content that is located in the file path.
        Separates the content into the following 6 categories for scoring and
        weighting:
            1. Title: TITLE
            2. H1-H2: H1, H2
            3. H3-H6: H3, H4, H5, H6
            4. Strong: STRONG, B, EM, I, U, DL, OL, UL
            5. Plain text or body: The rest
            6. Anchor words (Links): A

        Returns a dictionary containing the following keys containing information:
            - id : identifier of the document (same as path)
            - len_doc : total length of the document (by character)
            - broken_body : True if body tags are incomplete
            - number_alpha_ratio : the ratio between numbers and alphabets
            - removed_numbers : True if the numbers were removed in preprocessing
            - title : String containing title of the document (text before body tag
                if no title tags)
            - body : String containing the text surrounded by the body tags, or
                usually the rest of the doc
            - h1h2 : String containing the text with h1 and h2 tags
            - h3h6 : String containing the text with h3, h4, h5, and h6 tags
            - strong : String containg all the text that have strong, bold, emphasis,
                italic, underlined, description list, ordered list, unordered list tags
            - anchor : String containing text related to hyperlinks
        """
        
        
        doc_dict = {'id': path}
        raw = ""
        try:
            with open("WEBPAGES_RAW/{}".format(path), "r", encoding="utf-8") as html_file:
            # with open("/Users/lindale/Desktop/M2/WEBPAGES_TEST/{}".format(path), "r", encoding="utf-8") as html_file:
                raw = html_file.read()

        except IOError:
            print("HTML file not found in the directory.")

        raw = self.html_validator(raw)

        # html parser doesn't automatically add tags at the beginning of the document,
        # which is useful to find out if the file has a broken body.
        soup_html = BeautifulSoup(raw, 'html.parser')      

        # Checks if the content is HTML or not by checking if there's a Body tag (Using html.parser)
        if not soup_html.find('body'):
            doc_dict["broken_body"] = True
            # For the offline content, it checks the file size or how much content there is in each "page"
            # For online content, urllib would help checking the content size and even length without downloading
            if os.path.getsize("WEBPAGES_RAW/{}".format(path)) > FILE_SIZE_CAP:
                # Will truncate the file if the content is NOT html and is greater than 500 lines
                raw_split = str.splitlines(raw)
                if len(raw_split) > 500:
                    raw_split = raw_split[:500]
                    raw = '\n'.join(raw_split)

            # Removes the links if it has a broken body, otherwise it will be handled by BS4
            raw = self.remove_link_content(raw)

        else:
            doc_dict["broken_body"] = False

        # Checks if the ratio between numbers and alphabets is more than 20%
        # Removes all the numeric content replacing it with whitespaces if true.
        if raw is not None:
            number_alpha_ratio = self.check_percentage_numeric(raw)
            doc_dict["number_alpha_ratio"] = number_alpha_ratio
            if number_alpha_ratio > NUMBER_ALPHA:
                raw = self.remove_numbers_content(raw)
                doc_dict["removed_numbers"] = True
        # Before proceding checks if the content is empty after removal of unnecessary text
        else:
            return doc_dict

        # Note: BS4 automatic broken tag handling
        # 1)    If there is only an opening tag and no closing tag the parser by default adds the
        #       rest of the text as part of the corresponding opening tag.
        # 2)    If there is only a closing tag and no opening tag the parser by default does NOT
        #       add any of the text.
        # 3)    If the tag is incomplete in the form of '<strong' it will not add any more text.
        # 4)    If the tag is incomplete in the form of 'strong>' it will keep adding all the text.

        # Broken tags automatic handling by bs4 and respective parser
        # lxml parser tries to add <body><p> tags at the beginning of the document, which is
        # not very useful for this case/scenario as the clean version of the URLs
        # do not contain title tags.
        soup_lxml = BeautifulSoup(raw, 'lxml')
        # raw = soup_lxml.prettify()

        # Removes all style, scripts / javascript tags
        for script in soup_lxml(["script", "style"]):
            script.decompose()

        # Get length of the text.
        doc_dict["len_doc"] = len(soup_lxml.get_text())

        # TITLE
        # Checks if the document has a title tag
        if soup_lxml.title:
            doc_dict["title"] = soup_lxml.title.get_text()

        # BODY
        # If the <body> tag is broken it will get the entire text of the document as body
        if doc_dict.get("broken_body"):
            # Gets all the text
            doc_dict["body"] = soup_lxml.get_text()
        else:
            # Only gets what's in between <body> tags
            if soup_lxml.find('body') is not None:
                doc_dict["body"] = soup_lxml.find('body').get_text()
            else:
                doc_dict["body"] = ""

        # PARAGRAPH for snippet
        # Checks if the document has a paragraph tag
        if soup_lxml.find_all('p'):
            temp_list = [paragraph.get_text() for paragraph in soup_lxml.find_all('p')]
            doc_dict["paragraph"] = ' '.join([str(elem) for elem in temp_list])
      
        # BS4 find_all will find all tags regardless of case (All upper and lower)
        # H1 - H2
        if soup_lxml.find_all(['h1', 'h2']):
            temp_list = [header.get_text() for header in soup_lxml.find_all(['h1', 'h2'])]
            doc_dict["h1h2"] = ' '.join([str(elem) for elem in temp_list])

        # H3 - H6
        if soup_lxml.find_all(['h3', 'h4', 'h5', 'h6']):
            temp_list = [header.get_text() for header in soup_lxml.find_all(['h3', 'h4', 'h5', 'h6'])]
            doc_dict["h3h6"] = ' '.join([str(elem) for elem in temp_list])

        # STRONG (strong, bold, emphasis, italic, underlined, description list, ordered list, unordered list)
        if soup_lxml.find_all(['strong', 'b', 'em', 'i', 'u', 'dl', 'ol', 'ul']):
            temp_list = [strong.get_text() for strong in soup_lxml.find_all(['strong', 'b', 'em', 'i', 'u', 'dl', 'ol', 'ul'])]
            doc_dict["strong"] = ' '.join([str(elem) for elem in temp_list])

        # ANCHOR
        if soup_lxml.find_all('a'):
            temp_list = [anchor.get_text() for anchor in soup_lxml.find_all('a')]
            doc_dict["anchor"] = ' '.join([str(elem) for elem in temp_list])

        return doc_dict


    def tokenize_no_filter(self, content: str) -> 'List[tokens]':
        """
        Tokenizer without any kind of stop word filters nor minimum char limits
        """

        tokenList = []
        mainString = ""

        for c in content: 
            if c.isalnum() and c.isascii():
                mainString+=c
            else:
                mainString+=" "

        mainString = mainString.lower()
        tokenList.extend(mainString.split())

        return tokenList


    def tokenize(self, content: str) -> 'List[tokens]':
        """
        Tokenizer that uses punctuation as delimiter and will remove all stop words,
        words shorter than 4 characters, and any special characters that do not
        belong to ascii.
        Returns a list of strings (tokens)
        """

        words = []
        if content:
            tokens = nltk.tokenize.WordPunctTokenizer().tokenize(content.lower())
            #tokens = nltk.tokenize.WhitespaceTokenizer().tokenize(content.lower())

            words = [word for word in tokens if word.isalnum() and
                word not in self.stop_words and
                word.isascii() and
                len(word) > 3 and len(word) < 70]
        
        return words


    def tokenize_span(self, content: str) -> 'List[tuples]':
        """
        This tokenizer will account for the positional index of each of the tokens
        inside the original text.

        Also, uses punctuation as delimiter and will remove all stop words,
        words shorter than 4 characters, and any special characters that do not
        belong to ascii.

        Returns a list of tuples (token, index)
        """

        words = []

        if content:
            tokens = nltk.tokenize.WordPunctTokenizer().tokenize(content.lower())
            spans = nltk.tokenize.WordPunctTokenizer().span_tokenize(content.lower())

            #tokens = nltk.tokenize.WhitespaceTokenizer().tokenize(content.lower())
            #spans = nltk.tokenize.WhitespaceTokenizer().span_tokenize(content.lower())

            # Using zip to group into tuples
            merged = list(zip(tokens, [s[0] for s in spans]))
            words = [word for word in merged if word[0].isalnum() and
                word[0] not in self.stop_words and
                word[0].isascii() and
                len(word[0]) > 3 and len(word[0]) < 70]
                #and not word[0].isdigit()]

        return words


    def word_frequency(self, tokens: 'List[token] or List[(token, span)]') -> 'Dict':
        """
        This method will calculate the word frequency of the list of tokens.
        It accepts as parameter both types of tokens created, those that only have
        frequency and those that are tuples containing (token, index).
        Lemmatization is applied to all the words that go through the frequency
        counter.

        Returns a dictionary containing tokens or terms as key and frequency as value.
        For the processing of the List[(token, span/index)] it will return
        the token as key, and a nested list [frequency, [indexes it appears]]
        """

        freq_dict = defaultdict(list)

        # Checks if the incoming container is a List of tokens
        # or a List of Tuples (token, span)
        if any(isinstance(i, tuple) for i in tokens):
            
            # Lemmatization using WordNetLemmatizer
            lemmatized = [(nltk.WordNetLemmatizer().lemmatize(word[0]), word[1]) for word in tokens]

            # Porter Stemmer
            # porter = [(nltk.PorterStemmer().stem(word[0]), word[1]) for word in lemmatized]

            for tup in lemmatized:
                if freq_dict.get(tup[0]):
                    freq_dict[tup[0]][0] = freq_dict[tup[0]][0] + 1
                    freq_dict[tup[0]][1].append(tup[1])
                else:
                    freq_dict[tup[0]].insert(0, 1)
                    freq_dict[tup[0]].insert(1, [tup[1]])
                
        elif isinstance(tokens, list):
            # Lemmatization using WordNetLemmatizer
            lemmatized = [nltk.WordNetLemmatizer().lemmatize(word) for word in tokens]

            # Porter Stemmer
            # porter = [nltk.PorterStemmer().stem(word) for word in lemmatized]

            fdist = nltk.FreqDist(lemmatized)
            freq_dict = dict((word, f) for word, f in fdist.items())

        return freq_dict

    
    def tokenize_bigram(self, content: str) -> list:
        words = []
        dict_bigrams = {}

        if content:
            tokens = nltk.tokenize.WordPunctTokenizer().tokenize(content.lower())

            words = [word for word in tokens if word.isalnum() and
                word not in self.stop_words and
                word.isascii() and
                len(word) > 3 and len(word) < 70]

            bigrams = list(ngrams(words, 2))

        return bigrams


    def bigram_freq(self, content: str) -> 'Dict':
        """
        This method will calculate the word frequency using bi-grams or bi-words
        """

        words = []
        dict_bigrams = {}
        if content:
            tokens = nltk.tokenize.WordPunctTokenizer().tokenize(content.lower())

            words = [word for word in tokens if word.isalnum() and
                word not in self.stop_words and
                word.isascii() and
                len(word) > 3 and len(word) < 70]

            lemmatized = [nltk.WordNetLemmatizer().lemmatize(word) for word in words]
            bigrams = list(ngrams(lemmatized, 2))

            for word in bigrams:
                joint = ''.join(word)
                if joint in dict_bigrams:
                    dict_bigrams[joint] += 1
                else:
                    dict_bigrams[joint] = 1

        return dict_bigrams


    # Appends the tag to the end of the line
    def append_eol(self, tag, message, line):
        fixed_line = ""
        if tag in message:
            fixed_line = f'{line}</{tag}>'
        return fixed_line


    # Appends the tag to the start of the line
    def append_sol(self, tag, message, line):
        fixed_line = ""
        if tag in message:
            fixed_line = f'<{tag}>{line}'
        return fixed_line


    # Check how much of the content is numbers vs alpha
    def check_percentage_numeric(self, content):
        special = len([c for c in content if not c.isalnum()])
        if len(content) == special:
            return 1
        else:
            result = len([c for c in content if c.isdigit()]) / (len(content) - special)
            return round(result, 2)


    # Removes all words that are only numbers from the text
    def remove_numbers_content(self, content):
        # Calculates the length of the removed numbers and replaces it with whitespace
        # for positional index purposes
        match = re.search(regex_numbers, content)
        if match is not None:
            span = match.span()
            length = span[1] - span[0]
            return re.sub(regex_numbers, " " * length, content)

    # removes urls
    def remove_link_content(self, content):
        match = re.search(regex_links, content)
        if match is not None:
            span = match.span()
            length = span[1] - span[0]
            return re.sub(regex_links, " " * length, content)


    def html_validator(self, raw):
        """
        TIDYLIB
        """

        try:
            document, errors = tidy_document(raw,
            options = {'numeric-entities':1,
                    'input-encoding': 'utf8',
                    'output-encoding': 'utf8',
                    'tidy-mark': False,
                    'indent': False,
                    'wrap': 0
                    })
            # print("ERRORS: {}".format(errors))

            # Split the raw content of the page into a list separated by new line
            list_raw = raw.split("\n")

            errors = errors.splitlines()
            # Loop through the errors and fixes the broken tags
            for e in errors:
                line_number = e.split()[1]
                if line_number.isdigit():
                    line_number = int(line_number)

                    # Check for unclosed elements. Adds the missing tag to the end of the line.
                    if "missing </" in e:
                        tag = e.split("</")[1].split(">")[0]
                        list_raw[line_number - 1] = self.append_eol(tag, e, list_raw[line_number - 1])
                    # Check for unopened elements. Adds the missing tag to the start of the line.
                    elif "discarding unexpected </" in e:
                        tag = e.split("</")[1].split(">")[0]

                        list_raw[line_number - 1] = self.append_sol(tag, e, list_raw[line_number - 1])

            # Joins the list with the fixed tags back into a string
            raw = "\n".join(list_raw)
            # print("RAW FIX: {}\n\n".format(raw))

        except UnicodeDecodeError:
            print("Tidylib can't decode characters from the file using utf-8")

        except OSError:
            print("Tidylib error handling the file.")

        finally:
            return raw



if __name__ == "__main__":
    
    p = Preprocessing()
    # p.read_json()
    # temp = p.fetch_content("3")
    # temp = p.fetch_content("39/373")
    # temp = p.fetch_content("55/271")
    temp = p.fetch_content("65/278")

    # temp = p.fetch_content("373")
    print("\n\n--------TITLE---------")
    print(p.tokenize(temp.get('title')))
    print("\n--------BODY---------")
    print("Broken body? : {}\n".format(temp.get('broken_body')))
    print(p.tokenize_span(temp.get('body')))
    print("\n--------H1H2---------")
    print(p.tokenize(temp.get('h1h2')))
    print("\n--------H3H6---------")
    print(p.tokenize(temp.get('h3h6')))
    print("\n--------STRONG---------")
    print(p.tokenize(temp.get('strong')))
    print("\n--------ANCHORS---------")
    print(p.tokenize(temp.get('anchor')))
    print("\n---------FREQ--------")
    tok = p.tokenize_span(temp.get('body'))
    print(p.word_frequency(tok))
    print("\n---------BIGRAMS--------")
    print(p.bigram_freq(temp.get('body')))

