import re

import pandas as pd
import requests
from bs4 import BeautifulSoup

# The URL of the NCAA page
url = 'https://www.ncaa.com/basketball-men/d1/every-ncaa-bracket-1939-today-tournament-stats-records'
headers = {'User-Agent': 'Mozilla/5.0'}

# Send a GET request to the URL
response = requests.get(url, headers)

# Parse the HTML content using BeautifulSoup of the main page
soup = BeautifulSoup(response.content, 'html.parser')

# Find all the links from 2006-2019 and include the year
links = []
for link in soup.find_all('a', href=True):
    if link.text.startswith('Click or tap here'):
        year = link.get('href').split('/')[-1][:4]
        links.append({"year": year, "url":link.get('href')})

# Manually add the links for 2021-2023 since they were not included on the original page
# There was no tournament during 2020
links.append({"year": '2021', "url": r"https://www.ncaa.com/news/basketball-men/article/2022-07-20/2021-ncaa-bracket-scores-stats-records-march-madness-mens-tournament"})
links.append({"year": '2022', "url": r"https://www.ncaa.com/news/basketball-men/article/2022-07-12/2022-ncaa-bracket-mens-march-madness-scores-stats-records"})
links.append({"year": '2023', "url": r"https://www.ncaa.com/news/basketball-men/article/2023-04-18/2023-ncaa-bracket-scores-stats-march-madness-mens-tournament"})

# Go through every year and link until the 2006 tournament
for page in links:
    year = page['year']
    url = page['url']

    # Send a GET request to the URL
    response = requests.get(url, headers)

    # Parse the HTML content using BeautifulSoup of the bracket page
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the section for the Scores
    section = soup.find_all('h2')[2] if year != '2023' else soup.find_all('h3')[8] # Different formarting used 2023

    # Find the scores list within the section
    scores_list = section.find_next('ul')

    # Find the unordered lists for each of the rounds
    match year:
        case '2009': # The 2009 page did not have the opening round game listed
            all_round_list = section.find_next('ul').find_all('li', recursive=False)
        case _:
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
                # Different clean and split logic needed due to the inconsistency on the website
                match year:
                    case '2014': # Typo on the page in 'No. 7 Texas 87 No. 10 Arizona State 85' has no comma, new logic required for split
                        parts = re.sub(r'\,|\| Watch full game|\| Watch the full game|\(OT\)|\(2OT\)', '', s).split('No.')
                        winner = parts[1].split()
                        loser = parts[2].split()
                    case _:
                        parts = re.sub(r'No\.|No |\| Watch full game|\| Watch the highlights|\| Watch the highlights\'|\| Watch the full game|\(OT\)|\(2OT\)', '', s).split(',')
                        winner = parts[0].split()
                        loser = parts[1].split()
                
                # Split the winner component into seed, name, and score
                winner_seed = winner[0]
                winner_name = ' '.join(winner[1:-1])
                winner_score = winner[-1]
                
                # Split the loser component into seed, name, and score
                loser_seed = loser[0]
                loser_name = ' '.join(loser[1:-1])
                loser_score = loser[-1]

                # Create a table row and add it to the list of games
                games.append([year, round_name, winner_seed, winner_name, winner_score, loser_seed, loser_name, loser_score])
        
    # Set the last game of the Final Four as the championship game
    games[-1][1] = 'championship'

    # Misc. typos that need to be manually due to missing data
    match year:
        case '2023':
            # Fixed loser score from first_round Miami v. Drake
            games[2] = [2023,'first_round',5,'Miami (FL)',63,12,'Drake',56]

            # Fixed loser score due to addtional apostrophe
            games[54] = [2023,'sweet_16',5,'San Diego St.',71,1,'Alabama',64]

            # Fixed the championship game due to the change in formating
            for i in range(7):
                games.pop()
            games.append([2023,'championship',4,'UConn',76,5,'San Diego St.',59])

        case '2021': 
            # Missing loser score from first_round Florida St. v. UNC Greensboro
            games[19] = [2021, 'first_round',4,'Florida St.',64,13,'UNC Greensboro',54]

            # Removed Oregon v. VCU due to no-contest
            games.pop(14)

        case '2018': # Missing loser score from second_round Gonzaga v. Ohio State
            games[39] = [2018,'second_round',4,'Gonzaga',90,5,'Ohio State',84]
        case '2017': # Missing loser seed from first_round North Carolina v. Texas Southern
            games[16] = [2017,'first_round',1,'North Carolina',103,16,'Texas Southern',64]
        case '2009': # Missing loser seed from first_round UConn v. Chattanooga
            games[24] = [2009,'first_round',1,'UConn',103,16,'Chattanooga',47]

    # Create a pandas dataframe from the table rows
    df = pd.DataFrame(games, columns=['Year', 'Round', 'Winner Seed', 'Winner Name', 'Winner Score', 'Loser Seed', 'Loser Name', 'Loser Score'])
    print(df)

    # Save the dataframe to a csv file
    df.to_csv(f'data\\{year}.csv', index=False)