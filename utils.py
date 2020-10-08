import parse
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer

def parse_args(msg):
    # Get the argument pairs in a list
    args = list(map(lambda x: x.strip(), msg.split(',')))
    # Parse the arguments into a list of dicts
    args = list(map(lambda x: parse.parse('{col}={val}', x), args))

    return args

def check_similar(s1, s2):
    '''Returns the cosine similarity of two strings'''
    vectors = CountVectorizer().fit_transform([s1, s2]).toarray()
    similarity = cosine_similarity(vectors)[0, 1]

    return similarity