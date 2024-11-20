# Vendée Globe 2024
A predictive modeling project to analyze and forecast the routes of boats participating in the ongoing Vendée Globe 2024 race.

## Overview
This project collects, processes, and models data from the Vendée Globe 2024 race to gain insights and make route predictions for participating skippers.

---

## Fetching Data
### Vendee Globe routes 2024
To fetch the Vendée Globe 2024 routes data from [https://www.vendeeglobe.org/classement](https://www.vendeeglobe.org/classement), run the following command:

```bash
python src/get_2024_routes.py
```

#### Parameters
The script requires the following parameters:

- **`reports`**: A list containing the range of report numbers `[reports_start, reports_end]` specifying the period to fetch data for:
  - **`reports_start`**: The report number corresponding to the first day and time of the race. For example, the URL `https://www.vendeeglobe.org/classement?report=74` corresponds to **10.11.2024 15h**, so `reports_start` would be `74`.
  - **`reports_end`**: The report number corresponding to the last day and time to fetch. 

#### Example
To fetch data from the start of the race on **10.11.2024 15h** (`report=74`) to 16.11.2024 19h (`report=134`), pass the `reports` parameter as:

```bash
python src/get_2024_routes.py --reports [74, 134]
```
#### Notes
- The script will most likely stop working once the webpage is updated for the next race.

- If you encounter errors while reading the Excel files with Python, try opening and saving them again using a spreadsheet application like Microsoft Excel or LibreOffice.

### Download Vendee Globe 2020 data
You can download 2020 data from https://www.bislins.ch/walti/bloge/index.asp?page=Media%3AVendee+Globe+Race+GPS+Data%2Ezip

## Preparing the Data for Modeling
To enhance route data with wind data for certain checkpoint times, there are two separate scripts for the 2020 and 2024 data:

### For 2020 Data:
Run the following script to add the wind information to the 2020 Vendée Globe data:
```bash
python src/ranking_history_with_wind_2020.py
```
The scripts will add the following columns to the route data:

- **`temp`**: Temperature at the skipper's location.
- **`windgust`**: Wind gust speed at the skipper's location.
- **`windspeed`**: Wind speed at the skipper's location.
- **`winddir`**: Wind direction at the skipper's location.

To enable fetching wind data from the Visual Crossing Weather API:

1. Obtain an API key from [Visual Crossing Weather](https://www.visualcrossing.com/).
2. Store the API key in a separate file (e.g., `api_key.txt`).
3. Specify the path to the API key file in the `src/functions/get_data.py` script.
