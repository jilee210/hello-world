#!/usr/bin/env python
# https://github.com/datacamp/datacamp_facebook_live_nlp/
# Jupyter notebook version 
# Web scraping & NLP in Python
# 10/17/17
#========================================
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import seaborn as sns
%matplotlib inline
import nltk
from nltk.tokenize import RegexpTokenizer

def plot_word_freq(url):
    """Takes a url (from Project Gutenberg) and plots a word frequency
    distribution"""
    # Make the request and check object type
    r = requests.get(url)
    # Extract HTML from Response object and print
    html = r.text
    # Create a BeautifulSoup object from the HTML
    soup = BeautifulSoup(html, "html5lib")
    # Get the text out of the soup and print it
    text = soup.get_text()
    # Create tokenizer
    tokenizer = RegexpTokenizer('\w+')
    # Create tokens
    tokens = tokenizer.tokenize(text)
    # Initialize new list
    words = []
    # Loop through list tokens and make lower case
    for word in tokens:
        words.append(word.lower())
    # Get English stopwords and print some of them
    sw = nltk.corpus.stopwords.words('english')
    # Initialize new list
    words_ns = []
    # Add to words_ns all words that are in words but not in sw
    for word in words:
        if word not in sw:
            words_ns.append(word)
    # Create freq dist and plot
    #Import datavis libraries

    #import matplotlib.pyplot as plt
    #import seaborn as sns
    
    # Figures inline and set visualization style

    #%matplotlib inline
    #sns.set()

    freqdist1 = nltk.FreqDist(words_ns)
    freqdist1.plot(25)

plot_word_freq('https://www.gutenberg.org/files/10/10-h/10-h.htm') # KJV
