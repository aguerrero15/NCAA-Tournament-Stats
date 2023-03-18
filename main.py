import re

import pandas as pd
import requests
from bs4 import BeautifulSoup

# The URL of the NCAA page
url = 'https://www.ncaa.com/news/basketball-men/article/2020-05-06/2019-ncaa-tournament-bracket-scores-stats-records'

# Send a GET request to the URL
response = requests.get(url)

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')

# Find the section for the Scores
section = soup.find_all('h2')[2]

# Find the scores list within the section
scores_list = section.find_next('ul')

# Find the unordered lists for each of the rounds
all_round_list = section.find_next('ul').find_all('li', recursive=False)[1:]

# Create array that contains each game from each round
games = []
for round in all_round_list:
    # Get the name from the list and save it to add later
    round_name = '_'.join(re.split('\s', round.text, 2)[0:2]).lower()

    for region in round.find_all_next('ul')[0].find_all('li', recursive=False):
        # Clean and strip game line from list
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
            games.append([winner_seed, winner_name, winner_score, loser_seed, loser_name, loser_score, round_name])
    
# Set the last game of the Final Four as the championship game
games[-1][-1] = 'championship'

# Create a pandas dataframe from the table rows
df = pd.DataFrame(games, columns=['Winner Seed', 'Winner Name', 'Winner Score', 'Loser Seed', 'Loser Name', 'Loser Score', 'Round'])
print(df)

# Save the dataframe to a csv file
df.to_csv('data\\2019.csv', index=False)