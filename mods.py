import gspread
from oauth2client.service_account import ServiceAccountCredentials

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer

from prettytable import PrettyTable
from time import time
import parse
from datetime import datetime, timedelta
from pytz import timezone
import asyncio

from utils import parse_args, check_similar

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
                        'nandini', 'piyush', 'dhwaj', 'divya',
                        'kushagra', 'shreyas', 'rishabh']

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
        df = pd.DataFrame(np.array(data), columns=['name', 'title', 'status', 'category'])

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
                col = arg['col'].strip().lower()
                val = arg['val'].strip()

                if col == 'category':
                    add_info[col] = self.cat_map[val.lower()]
                elif arg['col'].strip() == 'title':
                    add_info[col] = val
                else:
                    add_info[col] = val.title()

            if len(add_info) < 2:
                return "Please provide data for atleast 2 columns (eg: name, title)"
        except Exception as e:
            print(e)
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

        # Get the row number of the user provided title
        similarities = np.array([check_similar(title, args_map['title']) for title in titles])
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
        self.scope = ["https://spreadsheets.google.com/feeds",
                      "https://www.googleapis.com/auth/spreadsheets",
                      "https://www.googleapis.com/auth/drive.file",
                      "https://www.googleapis.com/auth/drive"]
        self.creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", self.scope)
        self.gclient = gspread.authorize(self.creds)

        self.writers = ['anushk', 'anshita', 'somaditya',
                        'bhavesh', 'ishaan', 'mriganka',
                        'nandini', 'piyush', 'dhwaj', 'divya',
                        'kushagra', 'shreyas', 'rishabh']

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

    def add_schedule(self, msg):
        '''Returns the t_delta of the schedule'''
        args = parse_args(msg)

        # Convert the args list into a dictionary
        try:
            add_info = {}
            timestamps = []

            for arg in args:
                col = arg['col'].strip().lower()
                val = arg['val'].strip()

                if col not in ['title', 'category', 'date']:
                    continue # verify the col is valid

                if col == 'category':
                    add_info[col] = self.cat_map[val]

                # Create timestamps and date strings
                elif col == 'date':
                    date_str = f"{val} 10:00"

                    post_date = datetime.strptime(date_str, "%d-%m-%Y %H:%M")
                    s1_date = post_date - timedelta(days=1, hours=-8)
                    s2_date = post_date + timedelta(hours=4)

                    timestamps.extend([s1_date, post_date, s2_date])

                    s1_str = "{}-{}-{} 18:00".format(s1_date.day, s1_date.month, s1_date.year)
                    s2_str = "{}-{}-{} 14:00".format(s2_date.day, s2_date.month, s2_date.year)

                    add_info['story 1'] = s1_str
                    add_info['post'] = date_str
                    add_info['story 2'] = s2_str

                else: # for title
                    add_info[col] = val

            if len(add_info) < 3:
                return "Please provide data for all 3 columns (eg: category, title, date)", -1, -1

        except Exception as e:
            print(e)
            return "That command doesn't seem right?!", -1, -1

        df = pd.DataFrame(columns=['category', 'title', 'story 1', 'post', 'story 2'])
        row = df.append(add_info, ignore_index=True).fillna('').values.tolist()[0]

        # Create a formatted response string
        table = PrettyTable(['Category', 'Title', 'Story 1', 'Post', 'Story 2'])
        table.add_row(row)
        response_string = f'**Added to schedule and reminders are set**\n```\n> Category = {row[0]}\
                                                                            \n> Title    = {row[1]}\
                                                                            \n> Story 1  = {row[2]}\
                                                                            \n> Post     = {row[3]}\
                                                                            \n> Story 2  = {row[4]}\
                                                                            \n```'

        # Add the row to worksheet
        sheet = self.db.get_worksheet(1)
        sheet.append_row(row)

        post_details = (row[0], row[1])

        return response_string, timestamps, post_details


    async def schedule_reminders(self, ctx, timestamps, post_details):
        '''Starts the reminder timeout'''

        # Writers and Designers role ids for mentioning
        writer = "<@&747703681985544202>"
        designer = "<@&747703676587737229>"

        # Post details
        category, title = post_details

        # Get the Scheduled timestamps
        s1_t, post_t, s2_t = timestamps

        # Create reminder timestamps
        post_r1 = post_t - timedelta(hours=48)
        post_r2 = post_t - timedelta(hours=24)
        s1_r = s1_t - timedelta(hours=3)
        s2_r = s2_t - timedelta(hours=3)

        # Reminder responses
        rmdr_resps = [('Post', '48'), ('Post', '24'), ('First Story', '3'), ('Second Story', '3')]

        # Timeline: post_r1 -> post_r2 -> s1_r -> s2_r
        for rmdr, resps in zip([post_r1, post_r2, s1_r, s2_r], rmdr_resps):
            # Get the ETA in seconds
            # now = datetime.now() + timedelta(hours=5, minutes=30)
            now = datetime.now()

            # Check if now is less than rmdr
            if now > rmdr:
                print('rmdr is now in the past, so skipping this rmdr')
                continue

            # Get the t_delta in seconds
            delta = (rmdr - now).seconds + 5
            # Log
            print(f'Reminder on {title} at {str(rmdr)} in {delta} seconds')
            # Sleep
            await asyncio.sleep(int(delta))
            # Remind
            await ctx.channel.send(f"**Reminder:** The {resps[0]} on \"{title}\" ({category}) \
                                    needs to be published in {resps[1]} Hours. {writer} {designer}")


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
            print('t_remind:', t_remind)
            # now = datetime.now() + timedelta(hours=5, minutes=30)
            now = datetime.now()
            print('now:', now)
            t_delta = (t_remind - now).seconds + 5

            return t_delta, args_map

        except Exception as E:
            print(E)
            return -1, "That command doesn't seem right! Check if the date-time format is correct"
