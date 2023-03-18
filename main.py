import pandas as pd
import requests
from bs4 import BeautifulSoup

# The URL of the Wikipedia page
url = 'https://www.ncaa.com/news/basketball-men/article/2020-05-06/2019-ncaa-tournament-bracket-scores-stats-records'

# Send a GET request to the URL
response = requests.get(url)

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')

# Find the section for the First Round
section = soup.find_all('h2')[2]

# Find the unordered list within the section
scores_list = section.find_next('ul')

print(scores_list)