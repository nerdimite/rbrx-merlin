import parse
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
import pickle

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

def save_reminders(obj, filename='reminders.pkl'):
    with open(filename, 'wb') as f:
        pickle.dump(obj, f)
         
def load_reminders(filename='reminders.pkl'):
    with open(filename, 'rb') as f:
        obj = pickle.load(f)
    return obj

def update_reminders(obj, filename='reminders.pkl'):
    # Load the reminders object
    try:
        reminders = load_reminders()
        # Update/Append the reminders
        reminders[0].extend(obj[0])
        reminders[1].update(obj[1])
    except:
        reminders = obj
    
    # Save the reminders
    save_reminders(reminders)
    
def remove_save(reminders_ts, reminders_map):
    '''Remove the first element with the corresponding key-value pair and save it'''
    reminders_ts.remove(reminders_ts[0])
    reminders_map.pop(reminders_ts[0])
    save_reminders((reminders_ts, reminders_map))