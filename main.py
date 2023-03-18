import re

import pandas as pd
import requests
from bs4 import BeautifulSoup

# The URL of the Wikipedia page
url = 'https://www.ncaa.com/news/basketball-men/article/2020-05-06/2019-ncaa-tournament-bracket-scores-stats-records'

# Send a GET request to the URL
response = requests.get(url)

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')

# Find the section for the Scores
section = soup.find_all('h2')[2]

# Find the scores list within the section
scores_list = section.find_next('ul')

# Find the unordered list for the First Round
first_round_list = scores_list.find_all_next('ul', recursive=False)[1]

# Create array that contains each game from first round
games = []
for region in first_round_list.find_all('li', recursive=False):
    lines = [li.text.strip().replace(u'\xa0', u' ') for li in region.find_next('ul').find_all('li')]
    for s in lines:
        # Clean and split the string into winner and loser components
        parts = re.sub(r'No\.|\| Watch full game|\(OT\)', '', s).split(',')
        
        # Split the winner component into seed, name, and score
        winner = parts[0].split()
        winner_seed = winner[0]
        winner_name = ' '.join(winner[1:-1])
        winner_score = winner[-1]
        
        # Split the loser component into seed, name, and score
        loser = parts[1].split()
        loser_seed = loser[0]
        loser_name = ' '.join(loser[1:-1])
        loser_score = loser[-1]

        # Create a table row and add it to the list of games
        games.append([winner_seed, winner_name, winner_score, loser_seed, loser_name, loser_score, "first_round"])


df = pd.DataFrame(games, columns=['Winner Seed', 'Winner Name', 'Winner Score', 'Loser Seed', 'Loser Name', 'Loser Score', 'Round'])
print(df)