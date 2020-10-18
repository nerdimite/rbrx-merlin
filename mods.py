import gspread
from oauth2client.service_account import ServiceAccountCredentials

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer

from prettytable import PrettyTable
from time import time
import parse
import random
from datetime import datetime, timedelta
from pytz import timezone
import asyncio

from utils import *

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

    def member_remove(self, member):
        '''Member Removed/Left'''
        now = str(datetime.now())
        sheet = self.db.get_worksheet(2)
        sheet.append_row([str(member.id), member.name, now])
        print(f'{member.name} left the server at {now}')


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


class Scheduler():

    def __init__(self):
        # Category shorthands
        self.cat_map = {'fringe': 'Fringe Bureau',
                        'psyche': 'Psyche',
                        'stem': 'STEM Lab',
                        'mint': 'Mint Affairs',
                        'footprints': 'Footprints',
                        'inspire': 'Inspire',
                        'yolo': 'YOLO'}

    def get_schedule(self, msg):
        '''Returns the timestamps of the stories and post for a particular post'''
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
                    date_str = f"{val} 11:00"

                    post_date = datetime.strptime(date_str, "%d-%m-%Y %H:%M")
                    s1_date = post_date - timedelta(days=1, hours=-7)
                    s2_date = post_date + timedelta(hours=3)

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
        values = df.append(add_info, ignore_index=True).fillna('').values.tolist()[0]

        # Create a formatted response string
        response_string = f'**Added to schedule and reminders are set**\n```\n> Category = {values[0]}\
                                                                            \n> Title    = {values[1]}\
                                                                            \n> Story 1  = {values[2]}\
                                                                            \n> Post     = {values[3]}\
                                                                            \n> Story 2  = {values[4]}\
                                                                            \n```'

        post_details = [values[0], values[1]]

        return response_string, timestamps, post_details


    def get_reminders(self, timestamps, post_details):
        '''Returns the timestamps of the reminders'''

        # Get the Scheduled timestamps
        s1_t, post_t, s2_t = timestamps

        # Create reminder timestamps
        post_r1 = post_t - timedelta(hours=48)
        post_r2 = post_t - timedelta(hours=24)
        post_r3 = post_t - timedelta(minutes=30)

        s1_r1 = s1_t - timedelta(hours=3)
        s1_r2 = s1_t - timedelta(minutes=30)

        s2_r1 = s2_t - timedelta(hours=3)
        s2_r2 = s2_t - timedelta(minutes=30)

        # Reminders
        reminders_ts = [post_r1, post_r2, post_r3, s1_r1, s1_r2, s2_r1, s2_r2]

        meta_data = [['Post', post_t], ['Post', post_t], ['Post', post_t],
                     ['Story 1', s1_t], ['Story 1', s1_t], ['Story 2', s2_t], ['Story 2', s2_t]]

        reminders_map = {t: post_details + m for t, m in zip(reminders_ts, meta_data)}


        return reminders_ts, reminders_map


    async def run_scheduler(self, bot):
        '''Starts the reminder timeout'''
        print('Running Scheduler...')

        # Roles and channels for mentioning
        writer = "<@&747703681985544202>"
        designer = "<@&747703676587737229>"
        channel = bot.get_channel(755142334496243892) # publishing channel <#755142334496243892>

        while(1):
            # Pre-Sleep
            await asyncio.sleep(60)

            # Load reminders
            try:
                reminders_ts, reminders_map = load_reminders()
                print('\nLoading Reminders...')
            except:
                reminders_ts, reminders_map = [], {}
                print('\nNo reminders')

            if len(reminders_ts) == 0:
                continue

            # Sort reminders
            reminders_ts.sort()

            print('[TS]', reminders_ts)
#             print('\n[MAP]',reminders_map)

            # Current timestamp
            now = datetime.now().replace(second=0, microsecond=0)

            # Post meta data
            meta = reminders_map[reminders_ts[0]] # category, title, type, timestamp

            # Check if current time is equal to reminder time
            if now == reminders_ts[0]:
                print(f'\nReminding Now at {reminders_ts[0]}')

                response_string = f"**Reminder for {meta[2]}**\n```\n> Title        = {meta[1]}\
                                                                   \n> Category     = {meta[0]}\
                                                                   \n> Publish On   = {meta[3]}\
                                                                   \n``` {writer} {designer}"

                print(response_string)
                await channel.send(response_string)

                remove_save(reminders_ts, reminders_map)

            # If its in the past
            elif now > reminders_ts[0]:
                print(f"**Skipping the Reminder**\n```\n> Content-Type = {meta[2]}\
                                                      \n> Title        = {meta[1]}\
                                                      \n> Category     = {meta[0]}\
                                                      \n> Publish On   = {meta[3]}\
                                                      \n> Reminder     = {reminders_ts[0]}\
                                                      \n```")
                remove_save(reminders_ts, reminders_map)


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
            now = datetime.now()
            print('now:', now)
            t_delta = (t_remind - now).seconds + 5

            return t_delta, args_map

        except Exception as E:
            print(E)
            return -1, "That command doesn't seem right! Check if the date-time format is correct"


class NewsBot():

    def __init__(self):
        self.scope = ["https://spreadsheets.google.com/feeds",
                      "https://www.googleapis.com/auth/spreadsheets",
                      "https://www.googleapis.com/auth/drive.file",
                      "https://www.googleapis.com/auth/drive"]
        self.creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", self.scope)
        self.gclient = gspread.authorize(self.creds)

        # Load Spreadsheet
        self.db = self.gclient.open("Content-DB")
        self.sheet = self.db.get_worksheet(1)

        self.channel_ids = {'bot-testing-zone': 755079000962891891, 'discussions': 754337556023345223}
        self.rubrix_id = 737282578117034004


    async def run(self, bot):
        '''Sends a news article link with an optional caption and mentions a user every 24 hours'''
        print('Running NewsBot...')

        timings = [datetime.strptime("10:30", "%H:%M").time(),
                   datetime.strptime("14:00", "%H:%M").time(),
                   datetime.strptime("18:00", "%H:%M").time(),
                   datetime.strptime("19:30", "%H:%M").time()]

        while(1):
            # Pre-Sleep
            await asyncio.sleep(60)

            # Get the data
            data = self.sheet.get_all_values()[1:]
            df = pd.DataFrame(np.array(data), columns=['link', 'caption', 'isDone'])
            buffer = df[df['isDone'] == ""].T.to_dict()

            if len(buffer) < 1:
                print('[NEWSBOT] Links Buffer is Empty!')
                continue

            # Current time
            now = datetime.now().replace(second=0, microsecond=0).time()

            if now not in timings:
                print('[NEWSBOT] Ping')
                continue

            print('[NEWSBOT] Sharing the article link...')

            # Get the first article from the buffer
            idx, info = list(buffer.items())[0]

            # Select 2 random members
            members = [member for member in bot.get_guild(self.rubrix_id).members if not member.bot]
            select = random.sample(members, k=2)

            # Format message
            message = f"{info['link']} \n{info['caption'] if info['caption'] != '' else f'What are your thoughts?'} <@!{select[0].id}> <@!{select[1].id}>"

            # Send message
            channel = bot.get_channel(self.channel_ids['discussions'])
            await channel.send(message)

            # Update status to done (1)
            self.sheet.update_cell(idx+2, 3, '1')
