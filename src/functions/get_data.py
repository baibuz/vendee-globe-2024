''' Functions for retrieving and sanitizing data required to predict Vendee Globe 2024 routes
by Eka Baibuz
'''
import os
import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
import io
from datetime import datetime

vendee_globe_2024_daily_url = 'https://www.vendeeglobe.org/classement' # URL with daily data
visualcrossing_api_key_file = 'src/functions/visualcrossing_api_key.txt'

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


def sanitize_2020_data(df2):
    """
    Convert Vendee Globe routes 2020 data to match 2024 format     
    Parameters:
    ----------
    df2 : pandas.DataFrame
        The input DataFrame containing 2020 Vendée Globe route data with columns
        such as `utcDate`, `utcTime`, `lat`, `lon`, `vmc`, and `heading`.
    
    Returns:
    -------
    pandas.DataFrame
        A DataFrame with columns 
        ['date', 'skipper', 'boat', 'latitude', 'longitude', 'heading', 'kph', 'vmg'] 
    """
        
    df2['date'] = pd.to_datetime(df2['utcDate'].astype(str) + ' ' + df2['utcTime'].astype(str))

    # Rename columns to match 2024 data
    df2 = df2.rename(columns={
        'lat': 'latitude',
        'lon': 'longitude',
        'vmc': 'vmg',
        'heading': 'heading'
    })

    # add `boat` column with placeholder values
    df2['boat'] = None  # Placeholder for missing boat information

    # Reorder columns to match `df1`
    df2 = df2[['date', 'skipper', 'boat', 'latitude', 'longitude', 'heading', 'kph', 'vmg']]
    return df2

def add_wind_data(df, api_key_file = visualcrossing_api_key_file):
    """
    Adds weather data (temperature, wind gust, wind speed, and wind direction) 
    from Visual Crossing to a DataFrame 
    of Vendée Globe boat positions based on latitude, longitude, and date.

    The function queries the Visual Crossing Weather API for weather data. The API key is read 
    from a file specified by `api_key_file`.

    Parameters:
    ----------
    df : pandas.DataFrame
        The input DataFrame containing the following columns:
        - `latitude` (float): Latitude of the skipper's position.
        - `longitude` (float): Longitude of the skipper's position.
        - `date` (str or datetime): The timestamp of the skipper's position.

    api_key_file : str, optional
        Path to the file containing the Visual Crossing API key. Defaults
        to visualcrossing_api_key_file global variable.

    Returns:
    -------
    pandas.DataFrame
        The input DataFrame with additional columns:
        - `temp`: Temperature at the position and time.
        - `windgust`: Wind gust at the position and time.
        - `windspeed`: Wind speed at the position and time.
        - `winddir`: Wind direction at the position and time.

    Notes:
    -----
    - Ensure the `api_key_file` contains the API key on a single line.
    - API queries can be costly; optimize queries if processing large datasets.

    Example:
    -------
    >>> df = pd.DataFrame({
    ...     "latitude": [47.0, 48.0],
    ...     "longitude": [-3.0, -4.0],
    ...     "date": ["2024-11-10 15:00:00", "2024-11-10 16:00:00"]
    ... })
    >>> df = add_wind_data(df, api_key_file="my_api_key.txt")
    """
    # Ensure the 'date' column is a datetime object
    df["date"] = pd.to_datetime(df["date"])
    # Add columns for weather data
    df["temp"] = None
    df["windgust"] = None
    df["windspeed"] = None
    df["winddir"] = None

    
    # Read the API key from the specified file
    if not os.path.exists(api_key_file):
        raise FileNotFoundError(f"API key file '{api_key_file}' not found.")
    
    with open(api_key_file, "r") as file:
        api_key = file.read().strip()
        
    # Iterate through the DataFrame rows
    for index, row in df.iterrows():
        latitude = row["latitude"]
        longitude = row["longitude"]
        
        # Ensure the date is a datetime object
        if isinstance(row["date"], str):
            date_obj = datetime.strptime(row["date"], "%Y-%m-%d %H:%M:%S")
        else:
            date_obj = row["date"]
        
        date = date_obj.strftime("%Y-%m-%d")
        
        # Build the Weather API URL
        url = (f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/"
               f"{latitude},{longitude}/{date}"
               f"?unitGroup=metric&key={api_key}&contentType=csv&include=hours&elements="
               "datetime,temp,windgust,windspeed,winddir")
        
        # Fetch data from the API
        response = requests.get(url)
        if response.status_code == 200:
            csv_data = io.StringIO(response.text)
            weather_data = pd.read_csv(csv_data)
            
            # Convert datetime in API response to match the DataFrame format
            weather_data["datetime"] = pd.to_datetime(weather_data["datetime"])
            
            # Find the closest time in the weather data to the boat's timestamp
            closest_time = weather_data.iloc[(weather_data["datetime"] - date_obj).abs().argsort()[:1]]
            # Add weather data to the DataFrame
            df.at[index, "temp"] = closest_time["temp"].values[0]
            df.at[index, "windgust"] = closest_time["windgust"].values[0]
            df.at[index, "windspeed"] = closest_time["windspeed"].values[0]
            df.at[index, "winddir"] = closest_time["winddir"].values[0]
        else:
            print(f"Error fetching data for row {index}: {response.status_code} - {response.text}")
    
    return df