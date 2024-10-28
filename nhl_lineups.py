import requests
from bs4 import BeautifulSoup
import pandas as pd

# URL and headers for the backup website
backup_url = "https://rotogrinders.com/lineups/nhl"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def replace_player_name(name):
    return name


def replace_team_name(name):
    name = name.replace("Hockey Club", "Utah Hockey Club")
    return name


# Function to fetch and parse the backup lineups
def fetch_backup_lineups():
    response = requests.get(backup_url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all the lineup divs
    lineups_div = soup.find('div', class_='container-body columns')
    if not lineups_div:
        print("Lineups container not found.")
        return []

    lineups = lineups_div.find_all('div', class_='module game-card')
    if not lineups:
        print("No lineup divs found.")
        return []

    backup_lineups = []

    for lineup in lineups:
        lineup_header = lineup.find('div', class_='module-header game-card-header')
        if not lineup_header:
            print("Lineup header not found for a game.")
            continue  # Skip if lineup_box is not found

        teams_container = lineup_header.find('div', class_='game-card-teams')
        if not teams_container:
            print("Teams container not found for a game.")
            continue  # Skip if teams_container is not found

        teams_containers = teams_container.find_all('div', class_='team-nameplate')
        if len(teams_containers) < 2:
            print("Teams containers not found properly.")
            continue  # Ensure both teams are present

        away_team_city = teams_containers[0].find('span', class_='team-nameplate-title').find('span', class_='team-nameplate-city').text.strip()
        home_team_city = teams_containers[1].find('span', class_='team-nameplate-title').find('span', class_='team-nameplate-city').text.strip()
        away_team_mascot = teams_containers[0].find('span', class_='team-nameplate-title').find('span', class_='team-nameplate-mascot').text.strip()
        home_team_mascot = teams_containers[1].find('span', class_='team-nameplate-title').find('span', class_='team-nameplate-mascot').text.strip()

        # Extract the team names, ignoring the win-loss records
        if away_team_city and away_team_mascot and home_team_city and home_team_mascot:
            away_team = replace_team_name(away_team_mascot)
            home_team = replace_team_name(home_team_mascot)
        else:
            print("Team city or mascot missing.")
            continue  # Skip if either team div is not found

        lineup_body = lineup.find('div', class_='module-body game-card-body')
        if not lineup_body:
            print("Lineup body not found for a game.")
            continue  # Skip if lineup_main is not found

        lineup_body_inner = lineup_body.find('div', class_='game-card-lineups')
        if not lineup_body_inner:
            print("Lineup inner body not found for a game.")
            continue  # Skip if lineup_main is not found

        lineups_divs = lineup_body_inner.find_all('div', class_='lineup-card')
        if len(lineups_divs) < 2:
            print("Lineups divs not found properly.")
            continue  # Ensure both lineups are present

        away_div = lineups_divs[0]
        home_div = lineups_divs[1]

        if away_div and home_div:
            away_div_header = away_div.find('div', class_='lineup-card-header')
            home_div_header = home_div.find('div', class_='lineup-card-header')

            if away_div_header and home_div_header:
                away_pitcher_div = away_div_header.find('div', class_='lineup-card-pitcher break')
                if away_pitcher_div:
                    away_pitcher_div = away_pitcher_div.find('span')
                    if away_pitcher_div:
                        away_pitcher_div = away_pitcher_div.find('div', class_='player-nameplate-info')
                    else:
                        print("Away pitcher span not found.")
                        continue
                else:
                    print("Away pitcher div not found.")
                    continue

                home_pitcher_div = home_div_header.find('div', class_='lineup-card-pitcher break')
                if home_pitcher_div:
                    home_pitcher_div = home_pitcher_div.find('span')
                    if home_pitcher_div:
                        home_pitcher_div = home_pitcher_div.find('div', class_='player-nameplate-info')
                    else:
                        print("Home pitcher span not found.")
                        continue
                else:
                    print("Home pitcher div not found.")
                    continue

            else:
                print("Header divs not found.")
                continue

            if away_pitcher_div and home_pitcher_div:
                away_goalie = replace_player_name(away_pitcher_div.find('a', class_='player-nameplate-name').text.strip())
                home_goalie = replace_player_name(home_pitcher_div.find('a', class_='player-nameplate-name').text.strip())
            else:
                print("Goalie information not found.")
                continue  # Skip if pitcher information is not found

            backup_lineups.append({
                'Away Team': away_team,
                'Away Goalie': away_goalie,
                'Home Team': home_team,
                'Home Goalie': home_goalie,
            })
        else:
            print("Away or home div not found.")
            continue  # Skip if away or home div is not found

    return backup_lineups

# Function to save backup lineups to CSV
def save_backup_lineups():
    # Fetch the backup lineups
    backup_lineups = fetch_backup_lineups()

    if not backup_lineups:
        print("No lineups found.")
        return

    # Convert the backup lineups to a DataFrame
    lineups_df = pd.DataFrame(backup_lineups)

    # Save the data to a CSV file
    lineups_df.to_csv('nhl_lineups.csv', index=False)
    print("Lineups saved to nhl_lineups.csv")

if __name__ == "__main__":
    save_backup_lineups()
