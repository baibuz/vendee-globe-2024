''' Functions for retrieving and sanitizing data required to predict Vendee Globe 2024 routes
by Eka Baibuz
'''
import os
import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
import io

vendee_globe_2024_daily_url = 'https://www.vendeeglobe.org/classement' # URL with daily data

def save_vendee_2024_data(folder_to_save, reports = [74,134]):
    """
    Downloads and saves ranking data for the Vendée Globe 2024 website as Excel files.

    This function fetches daily ranking data from the Vendée Globe website for a specified 
    range of report numbers (url's) and saves the data as Excel files in the specified folder.

    Report corresponds to a certain day and time and has url in format 
    https://www.vendeeglobe.org/classement?report={report_number}
    For example, url https://www.vendeeglobe.org/classement?report=154 
    has data for 19.11.2024 7am
    
    Parameters:
    ----------
    folder_to_save : str
        The directory where the Excel files should be saved.
    reports : list of int, optional
        A list containing the start and end report numbers to download (default is [74, 134]).

    Returns:
    -------
    None
        The function saves the downloaded Excel files to the specified folder. No value is returned.

    Notes:
    -----
    - The report data is retrieved from the `vendeeglobe.org` website by constructing URLs for each report number.
    - Only downloads data if a valid link is found on the webpage for the specified report number.
    - The Excel files are saved with filenames derived from the URLs on the Vendée Globe website.
    - The urls most likely will stop working after the event is finished

    Example:
    -------
    >>> save_vendee_2024_data('data/2024/excels_orig', [74, 80])
    This will download report files from report 74 to 80 and save them in the 'data/2024/excels_orig' folder.
    """
    for report in range(reports[0],reports[1]+1):
        r = requests.get(vendee_globe_2024_daily_url+f'?report={report}')
        r_content = bs(r.content.decode('utf-8'), 'lxml')
        link_tags = r_content.find_all('a', {'class': 'button button--sm button--primary'})
        if len(link_tags)>0:
            ranking_url = 'https://www.vendeeglobe.org' + link_tags[0]['href']
            excel_filename = os.path.join(folder_to_save,link_tags[0]['href'].split('/')[-1])
            excel_response = requests.get(ranking_url)
            with open(excel_filename, 'wb') as file:
                    file.write(excel_response.content)

