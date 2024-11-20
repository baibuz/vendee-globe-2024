"""
This script processes the 2020 Vendee Globe routes data by performing the following tasks:
- Data Sanitization: 
Cleans and organizes the raw data for further analysis.
- Integration of Wind Data:
Adds wind data from https://www.visualcrossing.com/ to the positions of skippers for specific days and times.
Requires a path to API key, which should be stored in a separate file and 
specified in src/functions/get_data.py
- Adding wind data to each skipper on each day and timeslot requires numerous queries, which can be costly. To mitigate this, the script includes an option to keep one data point per day and one file per skipper

2020 Vendee Globe routes data should be taken from https://www.bislins.ch/walti/bloge/index.asp?page=Media%3AVendee+Globe+Race+GPS+Data%2Ezip 

Author: Eka Baibuz
"""
import pandas as pd
from functions.get_data import sanitize_2020_data
from functions.get_data import add_wind_data
import os 
import warnings
warnings.simplefilter(action='ignore', category=pd.errors.SettingWithCopyWarning)

once_per_day = False
one_file_per_skipper = True
file_path_2020 = 'data/2020/Vendee Globe 2020-2021 unprocessed.ods'

if once_per_day:
    file_to_save = 'data/ranking_history_withwind_2020_once_per_day.csv'
else:
    file_to_save = 'data/ranking_history_withwind_2020_full'
    
ranking_history_2020 = pd.read_excel(file_path_2020, engine='odf')
ranking_history_2020 = sanitize_2020_data(ranking_history_2020)

if once_per_day:
    ranking_history_2020["date"] = pd.to_datetime(ranking_history_2020["date"])
        
    # Extract one data point per skipper per day at midnight
    ranking_history_2020["day"] = ranking_history_2020["date"].dt.date
    ranking_history_2020 = ranking_history_2020.groupby(["skipper", "day"]).first().reset_index()
if one_file_per_skipper:
    # Save one skipper per file
    for skipper in ranking_history_2020.skipper.unique():
        print('Processing skipper '+ skipper)
        file_to_save_skipper = file_to_save+"_"+skipper+'.csv'
        if os.path.exists(file_to_save_skipper):
            print(f'Skipping {file_to_save_skipper}, file already exists.')
            continue  # Skip to the next skipper
        ranking_history_skipper = ranking_history_2020[ranking_history_2020.skipper == skipper]
        ranking_history_skipper = add_wind_data(ranking_history_skipper)
        print('Saving into ', file_to_save_skipper)
        ranking_history_skipper.to_csv(file_to_save_skipper,index = False)
else:
    ranking_history_wind_2020 = add_wind_data(ranking_history_2020)
    ranking_history_wind_2020.to_csv(file_to_save,index = False)

