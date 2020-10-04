import gspread
from oauth2client.service_account import ServiceAccountCredentials

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer

from prettytable import PrettyTable
from time import time
import parse
from datetime import datetime
from pytz import timezone

from utils import parse_args

class Status():
    
    def __init__(self):
        self.scope = ["https://spreadsheets.google.com/feeds",
                      "https://www.googleapis.com/auth/spreadsheets",
                      "https://www.googleapis.com/auth/drive.file",
                      "https://www.googleapis.com/auth/drive"]
        self.creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", self.scope)
        self.gclient = gspread.authorize(self.creds)
        
        self.writers = ['anushk', 'anshita', 'somaditya',
                        'bhavesh', 'ishaan', 'mriganka',
                        'nandini', 'piyush', 'dhwaj', 'divya', 'kushagra']
        
        # Load Spreadsheet
        self.db = self.gclient.open("Content-DB")
        
        # Category shorthands
        self.cat_map = {'fringe': 'Fringe Bureau', 
                        'psyche': 'Psyche', 
                        'stem': 'STEM Lab',
                        'mint': 'Mint Affairs',
                        'footprints': 'Footprints',
                        'inspire': 'Inspire',
                        'yolo': 'YOLO'}
        
        
    def query(self, msg):
        '''Query and Filter entries in Content Sheet'''
        
        # Parse the input text into a list of dicts
        args = parse_args(msg)
        
        # Get the worksheet
        sheet = self.db.get_worksheet(0)
        data = sheet.get_all_values()[1:]
        
        # Create a dataframe
        df = pd.DataFrame(np.array(data)[:, :-1], columns=['name', 'title', 'status', 'category'])
        
        try:
            for arg in args:
                
                if arg['col'].strip() == 'category':
                    val = self.cat_map[arg['val']]
                else:
                    val = arg['val'].strip().title()
                    
                df = df[df[arg['col'].strip().lower()] == val]
        except:
            return "That command doesn't seem right?!"
        
        if len(df) < 1:
            return "No data found for the requested query"
        
        # Create a formatted response string 
        table = PrettyTable(['Name', 'Title', 'Status', 'Category'])
        
        for row in df.values.tolist():
            table.add_row(row)
            
        response_string = f'**Content Sheet Query Results**\nFor Query Command `{msg}`\n```\n{table}\n```'
            
        return response_string
    
    
    def add(self, msg):
        '''Add a new row in the content sheet'''
        
        # Parse the input text into a list of dicts
        args = parse_args(msg)
        
        # Convert the args list into a dictionary
        try:
            add_info = {}
            for arg in args:
                if arg['col'].strip() == 'category':
                    add_info[arg['col'].strip()] = self.cat_map[arg['val']]
                elif arg['col'].strip() == 'title':
                    add_info[arg['col'].strip()] = arg['val'].strip()
                else:
                    add_info[arg['col'].strip()] = arg['val'].strip().title()
            
            if len(add_info) < 2:
                return "Please provide data for atleast 2 columns (eg: name, title)"
        
        except:
            return "That command doesn't seem right?!"
              
        if 'status' not in add_info:
            add_info['status'] = 'Proposed'
        
        df = pd.DataFrame(columns=['name', 'title', 'status', 'category'])
        row = df.append(add_info, ignore_index=True).fillna('').values.tolist()[0]
        
        # Create a formatted response string 
        table = PrettyTable(['Name', 'Title', 'Status', 'Category'])
        table.add_row(row)
        response_string = f'**Added a New Entry to the Content Sheet**\n```\n{table}\n```'
        
        # Add the row to worksheet
        sheet = self.db.get_worksheet(0)
        sheet.append_row(row)
            
        return response_string
    
    def check_similar(self, s1, s2):
        '''Returns the cosine similarity of two strings'''
        vectors = CountVectorizer().fit_transform([s1, s2]).toarray()
        similarity = cosine_similarity(vectors)[0, 1]
        
        return similarity
        
    def update(self, msg):
        '''Update the status of a titled piece'''
        
        # Parse the input text into a list of dicts
        args = parse_args(msg)
        
        try:
            args_map = {}
            for arg in args:
                if arg['col'] == 'title':
                    args_map['title'] = arg['val'].strip()
                elif arg['col'] == 'status':
                    args_map['status'] = arg['val'].strip()

            if len(args_map) < 2:
                return "That command doesn't seem right?!"
        except:
            return "That command doesn't seem right?!"
        
        # Get the worksheet
        sheet = self.db.get_worksheet(0)
        data = sheet.get_all_values()[1:]
        titles = np.array(data)[:, 1]
        
        similarities = np.array([self.check_similar(title, args_map['title']) for title in titles])
        if max(similarities) > 0.2:
            row_num = similarities.argmax() + 2
        else:
            return "Can't find any row with that title to update the status"
        
        sheet.update_cell(row_num, 3, args_map['status'].title())
        
        # Create a formatted response string 
        table = PrettyTable(['Name', 'Title', 'Status', 'Category'])
        table.add_row(sheet.row_values(row_num))
        response_string = f"**Status Updated**\n```\n{table}\n```"
        
        return response_string
        
        
class Funnel():
    
    def __init__(self):
        pass
    
    def remind(self, msg):
        '''Returns the sleep time in seconds with the parsed reminder message'''
        args = parse_args(msg)
        
        try:
            args_map = {}
            for arg in args:
                if arg['col'] == 'time':
                    args_map['time'] = arg['val'].strip()
                elif arg['col'] == 'msg':
                    args_map['msg'] = arg['val'].strip()
                    
            if len(args_map) < 2:
                return -1, "That command doesn't seem right!"
            
            t_remind = datetime.strptime(args_map['time'], "%d-%m-%Y %H:%M")
            now = datetime.now(timezone('UTC')).astimezone(timezone('Asia/Kolkata'))
            t_delta = (t_remind - now).seconds + 5

            return t_delta, args_map
        
        except:
            return -1, "That command doesn't seem right! Check if the date-time format is correct"
        
        