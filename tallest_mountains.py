from io import StringIO
import requests

import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
from streamlit_globe import streamlit_globe

# tallest mountains wikipedia url:
ASIA_URL = 'https://en.wikipedia.org/wiki/List_of_highest_mountains_on_Earth'
AFRICA_URL = 'https://en.wikipedia.org/wiki/List_of_highest_mountain_peaks_of_Africa'
ANDES_URL = 'https://en.wikipedia.org/wiki/List_of_mountains_in_the_Andes'
NORTH_AMERICA_URL = 'https://en.wikipedia.org/wiki/List_of_the_highest_major_summits_of_North_America'
EUROPE_URL = 'https://en.wikipedia.org/wiki/List_of_prominent_mountains_of_the_Alps_above_3000_m'

# select number of mountains to display per region
NUM_PER_REGION = st.sidebar.slider(label="Select the Number of Mountains to Display per Region", min_value=1, max_value=20, value=10)

# Asia data parsing
response = requests.get(ASIA_URL)

# find table in webpage
soup = BeautifulSoup(response.text,'html.parser')
asia_html = soup.find_all('table')[2]

# convert to pandas df
asia_list = pd.read_html(StringIO(asia_html))
asia_df = pd.DataFrame(asia_list[0]).head(NUM_PER_REGION)

asia_data = asia_df.values.tolist()
asia_data[0][1] = "Mount Everest"


# Africa data parsing
response = requests.get(AFRICA_URL)

soup = BeautifulSoup(response.text, 'html.parser')
africa_html = soup.find_all('table')[2]

africa_list = pd.read_html(StringIO(africa_html))
africa_df = pd.DataFrame(africa_list[0]).head(NUM_PER_REGION)
africa_data = africa_df.values.tolist()


# Andes Data Parsing
response = requests.get(ANDES_URL)

soup = BeautifulSoup(response.text, 'html.parser')
andes_html = soup.find_all('table')[1]

andes_list = pd.read_html(StringIO(andes_html))
andes_df = pd.DataFrame(andes_list[0]).drop(['Image'], axis=1).dropna().head(NUM_PER_REGION)
andes_data = andes_df.values.tolist()


# North America

response = requests.get(NORTH_AMERICA_URL)
soup = BeautifulSoup(response.text, 'html.parser')
na_html = soup.find_all('table')[0]

na_list = pd.read_html(StringIO(na_html))
na_df = pd.DataFrame(na_list[0]).head(NUM_PER_REGION)
na_data = na_df.values.tolist()


# europe

response = requests.get(EUROPE_URL)
soup = BeautifulSoup(response.text, 'html.parser')
europe_html = soup.find_all('table')[5]

europe_list = pd.read_html(StringIO(europe_html))
europe_df = pd.DataFrame(europe_list[0]).head(NUM_PER_REGION)
europe_data = europe_df.values.tolist()


def create_rows(data, africa=False, andes=False, north_america=False, europe=False):
    """Utiility to create rows and labels based upon a dataframe of mountain data."""

    COORD_COL = 7
    COLOR="#7ddb9b"
    HEIGHT_COL = 2
    LONG_FACTOR = 1
    LAT_FACTOR = 1
    if africa:
        COORD_COL = 6
        COLOR = "#e6d19a"
    elif andes:
        COORD_COL = 3
        HEIGHT_COL = 0
        COLOR = '#9acde6'
        LONG_FACTOR = -1
        LAT_FACTOR = -1
    elif north_america:
        COORD_COL = 7
        HEIGHT_COL = 4
        COLOR = "#bfa4eb"
        LONG_FACTOR = -1
    elif europe:
        COORD_COL = 4
        HEIGHT_COL = 2
        COLOR = '#e68585'

    lats = [float(row[COORD_COL].split('/')[1].split(' ')[1][1:-2]) for row in data]
    longs = [float(row[COORD_COL].split('/')[1].split(' ')[2][:-2]) for row in data]

    if north_america:
        heights = [(float(row[HEIGHT_COL][:-3].replace(',',"")) / 3.281) for row in data]
    else:
        heights = [float(row[HEIGHT_COL]) for row in data]    

    labels = [row[1] for row in data]

    rows = [
                {'lat': lat*LAT_FACTOR, 'lng': long*LONG_FACTOR, 'size': .00005*height, 'color': COLOR}
                for lat, long, height in zip(lats, longs, heights)
            ]

    labels = [
                {'lat': lat*LAT_FACTOR, 'lng': long*LONG_FACTOR, 'size': .00005*height, 'color': COLOR, 'text': label}
                for lat, long, height, label in zip(lats, longs, heights, labels)
            ]
    
    return rows, labels


asia_rows, asia_labels = create_rows(asia_data)
africa_rows, africa_labels = create_rows(africa_data, africa=True)
andes_rows, andes_labels = create_rows(andes_data, andes=True)
north_america_rows, north_america_labels = create_rows(na_data, north_america=True)
europe_rows, europe_labels = create_rows(europe_data, europe=True)

ALL_ROWS = asia_rows + africa_rows + andes_rows + north_america_rows + europe_rows
ALL_LABELS = asia_labels + africa_labels + andes_labels + north_america_labels + europe_labels

st.header("The World's Tallest Mountains")

streamlit_globe(pointsData=ALL_ROWS, labelsData=ALL_LABELS, daytime='day', width=700, height=1000)

