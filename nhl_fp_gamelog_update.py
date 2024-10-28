import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime, timedelta
from urllib.parse import urljoin


# User-Agent header to avoid getting blocked
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def remove_periods(last_name):
    """
    Removes all periods from the given last name.

    Parameters:
    last_name (str): The last name to be checked and modified.

    Returns:
    str: The modified last name with all periods removed.
    """
    return last_name.replace(".", "")


def scrape_goalie_gaa(goalie_url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(goalie_url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        soup = BeautifulSoup(response.text, 'html.parser')

        # Debugging prints
        print("Pitcher page fetched successfully")

        # Find the specific stat block container
        stat_container = soup.find('aside', class_='StatBlock br-5 ba overflow-hidden flex-expand StatBlock--multiple bg-clr-white brdr-clr-gray-06 PlayerHeader__StatBlock')

        # If stat_container is None, print an error message and return
        if not stat_container:
            print(f"Error: Stat container not found on pitcher page {goalie_url}")
            return None

        # Find the ul element within the stat block container
        stat_list = stat_container.find('ul', class_='StatBlock__Content flex list ph4 pv3 justify-between')
        if not stat_list:
            print(f"Error: Stat list not found on pitcher page {goalie_url}")
            return None

        # Find all li elements within the ul element
        li_elements = stat_list.find_all('li', class_='flex-expand')
        if len(li_elements) < 2:
            print(f"Error: Not enough li elements found on pitcher page {goalie_url}")
            return None

        # Find the div with the class "StatBlockInner" in the second li element
        gaa_info = li_elements[1].find('div', class_='StatBlockInner')
        if not gaa_info:
            print(f"Error: GAA info div not found on pitcher page {goalie_url}")
            return None

        # Try to find the GAA value div using more generalized classes
        gaa_value_div = gaa_info.find('div', class_='StatBlockInner__Value')
        if not gaa_value_div:
            # Print the content of gaa_info for debugging
            print(f"Debug: GAA info div content: {gaa_info}")
            print(f"Error: GAA value div not found on pitcher page {goalie_url}")
            return None

        # Extract the text and strip any surrounding whitespace
        gaa_number = gaa_value_div.text.strip()
        return gaa_number

    except requests.RequestException as e:
        print(f"Request error for pitcher URL {goalie_url}: {e}")
        return None


def scrape_goalie_name(goalie_url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(goalie_url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        soup = BeautifulSoup(response.text, 'html.parser')

        # Debugging prints
        print("Pitcher page fetched successfully")

        # Find the specific stat block container
        name_container = soup.find('div', class_='PlayerHeader__Main_Aside min-w-0 flex-grow flex-basis-0')

        if not name_container:
            print("name_container not found")

        name_container_inner = name_container.find('h1')

        if not name_container_inner:
            print("name_container_inner not found")

        name_parts = name_container_inner.find_all('span')

        if not name_parts:
            print("name_parts not found")

        first_name = name_parts[0].text.strip()
        last_name = name_parts[1].text.strip()

        last_name = remove_periods(last_name)
        first_name = remove_periods(first_name)

        full_name = f"{first_name} {last_name}"

        return full_name

    except requests.RequestException as e:
        print(f"Request error for pitcher URL {goalie_url}: {e}")
        return None


# Function to scrape box score page
def scrape_box_score(box_score_url):
    try:
        response = requests.get(box_score_url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        soup = BeautifulSoup(response.text, 'html.parser')

        # Debugging prints
        print("Box score page fetched successfully")

        # Extract the first inning runs from each team
        table = soup.find('table', class_='Table Table--align-right')
        if not table:
            print("Error: Table not found")
            return None, None, None, None, None, None, None, None, None, None

        rows = table.find('tbody').find_all('tr', class_='Table__TR Table__TR--sm Table__even')
        if len(rows) < 2:
            print("Error: Not enough rows found in table")
            return None, None, None, None, None, None, None, None, None, None

        # Extract first inning runs from each team
        first_period_goals = [row.find_all('td')[1].text.strip() for row in rows]

        if len(first_period_goals) == 2:
            away_team_goals = first_period_goals[0]
            home_team_goals = first_period_goals[1]
        else:
            print("Error: Could not retrieve first inning runs")
            return None, None, None, None, None, None, None, None, None, None

        soup_inner = soup.find('div', class_='Boxscore Boxscore__ResponsiveWrapper')

        # Extract starting pitchers
        player_sections = soup_inner.find_all('div', class_='Wrapper')
        if len(player_sections) < 2:
            print("Error: Not enough player sections found")
            return away_team_goals, home_team_goals, None, None, None, None, None, None, None, None

        # The second div with class 'Wrapper' is for the goalies
        away_goalie_table = player_sections[0]
        home_goalie_table = player_sections[1]

        away_goalie_table = away_goalie_table.find_all('div', class_='Boxscore flex flex-column')[1]
        home_goalie_table = home_goalie_table.find_all('div', class_='Boxscore flex flex-column')[1]

        away_goalies = away_goalie_table.find_all('a', class_='AnchorLink truncate db Boxscore__AthleteName')
        home_goalies = home_goalie_table.find_all('a', class_='AnchorLink truncate db Boxscore__AthleteName')

        base_url = 'https://www.espn.com'

        if away_goalies and home_goalies:
            away_goalie = away_goalies[0].text.strip()
            home_goalie = home_goalies[0].text.strip()
            away_goalie_url = urljoin(base_url, away_goalies[0]['href'])
            home_goalie_url = urljoin(base_url, home_goalies[0]['href'])
        else:
            print("Error: Could not retrieve goalie names")
            return away_team_goals, home_team_goals, None, None, None, None, None, None, None, None

        # Extract starting pitchers' innings and earned runs
        away_goalie_boxscore = away_goalie_table.find('div', class_='Table__ScrollerWrapper relative overflow-hidden').find_all('tr', class_='Table__TR Table__TR--sm Table__even')[1]
        home_goalie_boxscore = home_goalie_table.find('div', class_='Table__ScrollerWrapper relative overflow-hidden').find_all('tr', class_='Table__TR Table__TR--sm Table__even')[1]
        if not (away_goalie_boxscore and home_goalie_boxscore):
            print("Error: Not enough pitcher boxscores found")
            return away_team_goals, home_team_goals, away_goalie, home_goalie, None, None, None, None, None, None

        away_goalie_stats = away_goalie_boxscore.find_all('td', class_="Table__TD")
        home_goalie_stats = home_goalie_boxscore.find_all('td', class_="Table__TD")

        if away_goalie_stats and home_goalie_stats:
            away_goalie_ga = away_goalie_stats[1].text.strip()
            away_goalie_toi = away_goalie_stats[9].text.strip()
            home_goalie_ga = home_goalie_stats[1].text.strip()
            home_goalie_toi = home_goalie_stats[9].text.strip()

            away_goalie_toi = away_goalie_toi.split(':')[0]
            home_goalie_toi = home_goalie_toi.split(':')[0]

        else:
            print("Error: Could not retrieve pitcher stats")
            return away_team_goals, home_team_goals, away_goalie, home_goalie, None, None, None, None

        # Normalize innings pitched to 1 if >= 1
        if float(away_goalie_toi) >= 20:
            away_goalie_toi = 20
            away_goalie_ga = home_team_goals
        else:
            away_goalie_toi = away_goalie_toi
            away_goalie_ga = away_goalie_ga

        if float(home_goalie_toi) >= 20:
            home_goalie_toi = 20
            home_goalie_ga = away_team_goals
        else:
            home_goalie_toi = home_goalie_toi
            home_goalie_ga = home_goalie_ga

        if away_goalie_url and home_goalie_url:
            # Scrape pitcher orientations
            away_gaa = scrape_goalie_gaa(away_goalie_url)
            home_gaa = scrape_goalie_gaa(home_goalie_url)
            away_goalie_full_name = scrape_goalie_name(away_goalie_url)
            home_goalie_full_name = scrape_goalie_name(home_goalie_url)
        else:
            return away_team_goals, home_team_goals, away_goalie, home_goalie, away_goalie_toi, home_goalie_toi, away_goalie_ga, home_goalie_ga, None, None

        if away_gaa and home_gaa:
            if away_goalie_full_name and home_goalie_full_name:
                away_goalie = away_goalie_full_name
                home_goalie = home_goalie_full_name
                return away_team_goals, home_team_goals, away_goalie, home_goalie, away_goalie_toi, home_goalie_toi, away_goalie_ga, home_goalie_ga, away_gaa, home_gaa
            else:
                return away_team_goals, home_team_goals, away_goalie, home_goalie, away_goalie_toi, home_goalie_toi, away_goalie_ga, home_goalie_ga, None, None
        else:
            return away_team_goals, home_team_goals, away_goalie, home_goalie, away_goalie_toi, home_goalie_toi, away_goalie_ga, home_goalie_ga, None, None

    except requests.RequestException as e:
        print(f"Request error for box score URL {box_score_url}: {e}")
        return None, None, None, None, None, None, None, None, None, None


# Function to scrape a single day's games
def scrape_games(date):
    url = f'http://espn.com/nhl/scoreboard/_/date/{date}'

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract all sections that contain game information
        games = soup.find_all('section', class_='Scoreboard bg-clr-white flex flex-auto justify-between')

        if not games:
            print(f"No games found for date: {date}")

        game_data = []

        # Iterate over each game section and extract information
        for game in games:
            # Extract team names
            teams = game.find_all('div', class_='ScoreCell__TeamName')
            if len(teams) >= 2:
                away_team = teams[0].text.strip()
                home_team = teams[1].text.strip()

                # Extract the box score URL
                box_score_link = game.find('a', text='Box Score')
                if box_score_link:
                    box_score_url = 'http://espn.com' + box_score_link['href']
                    print(f"Fetching box score for URL: {box_score_url}")
                    away_goals, home_goals, away_goalie, home_goalie, away_goalie_toi, home_goalie_toi, away_goalie_ga, home_goalie_ga, away_gaa, home_gaa = scrape_box_score(box_score_url)
                    if away_goals is not None and home_goals is not None:
                        # Create a dictionary with the scraped data
                        game_data.append({
                            'Date': date,
                            'Away Team': away_team,
                            'Home Team': home_team,
                            'Away Team Goals': away_goals,
                            'Home Team Goals': home_goals,
                            'Away Goalie': away_goalie,
                            'Home Goalie': home_goalie,
                            'Away Goalie TOI': away_goalie_toi,
                            'Home Goalie TOI': home_goalie_toi,
                            'Away Goalie GA': away_goalie_ga,
                            'Home Goalie GA': home_goalie_ga,
                            'Away GAA': away_gaa,
                            'Home GAA': home_gaa
                        })
                    else:
                        print(f"Error retrieving data for game on {date}")
                else:
                    print(f"No box score link found for game on {date}")

        return game_data

    except requests.RequestException as e:
        print(f"Request error for date {date}: {e}")
        return []


def update_csv_with_new_data(start_date, end_date, csv_filename):
    date_format = "%Y%m%d"
    current_date = datetime.strptime(start_date, date_format)
    end_date = datetime.strptime(end_date, date_format)

    with open(csv_filename, 'a', newline='') as csvfile:
        fieldnames = [
            'Date', 'Away Team', 'Home Team', 'Away Team Goals', 'Home Team Goals',
            'Away Goalie', 'Home Goalie', 'Away Goalie TOI', 'Home Goalie TOI',
            'Away Goalie GA', 'Home Goalie GA',
            'Away GAA', 'Home GAA'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        while current_date <= end_date:
            date_str = current_date.strftime(date_format)
            print(f"Scraping data for date: {date_str}")
            daily_games = scrape_games(date_str)
            for game in daily_games:
                writer.writerow(game)
            current_date += timedelta(days=1)

if __name__ == "__main__":
    start_date = "20241027"  # Example start date
    end_date = "20241027"    # Example end date
    csv_filename = "nhl_fp_gamelog.csv"  # The CSV file you want to update

    update_csv_with_new_data(start_date, end_date, csv_filename)