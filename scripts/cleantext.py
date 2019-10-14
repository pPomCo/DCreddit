from collections import Counter
import math, csv, re
#from emoji import UNICODE_EMOJI
import datetime

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize 
#nltk.download("stopwords")
stop_words = set(stopwords.words('english')) 


def removeURL(string): 
    # findall() has been used  
    # with valid conditions for urls in string 
    text = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', ' ',string)
    return text 

#def remove_emoji(text):
#    for emoji in UNICODE_EMOJI:
#        text = text.replace(emoji,' ')
#    return text

def remove_sign(text):
    text = re.sub('[^a-zA-Z\d\s:]+',' ',text)
    return text

def clean_text(row):
    '''
    Return list of words filtered : without urls, emojis and signs
    '''
    text = row
    text = text.lower()
    
    #remove URLs, Emojis
    text = removeURL(text)
    #text = remove_emoji(text)
    text = remove_sign(text)
    
    # tokenize word by nltk
    word_tokens = word_tokenize(text) 
    filtered_text = [w for w in word_tokens if not w in stop_words] 
    
    return filtered_text
