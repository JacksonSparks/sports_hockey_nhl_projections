import csv
from collections import defaultdict, deque

# Function to count team and goalie appearances
def count_appearances(filename):
    # Dictionaries to keep counts
    team_counts = defaultdict(lambda: {
        'Away': 0, 'Away GS': 0, 'Away GA': 0, 'Away NGTP': 0, 'Away YGTP': 0, 'Away NGSTP': 0, 'Away YGSTP': 0,
        'Home': 0, 'Home GS': 0, 'Home GA': 0, 'Home NGTP': 0, 'Home YGTP': 0, 'Home NGSTP': 0, 'Home YGSTP': 0,
        'Total NGTP': 0, 'Total YGTP': 0, 'Total NGSTP': 0, 'Total YGSTP': 0,
        'Intra NGTP': 0, 'Intra YGTP': 0, 'Intra NGSTP': 0, 'Intra YGSTP': 0,
        'L10 NGSTP': deque(maxlen=10),  # Initialize with a deque to keep track of last 10 NGSTP results
        'NGSTP Streak': 0, 'YGSTP Streak': 0  # Initialize streaks
    })

    goalie_counts = defaultdict(lambda: {
        'Away': 0, 'Away GA': 0, 'Away NGTP': 0, 'Away YGTP': 0,
        'Home': 0, 'Home GA': 0, 'Home NGTP': 0, 'Home YGTP': 0,
        'Total NGTP': 0, 'Total YGTP': 0,
        'Season GAA': 0,
        'L5 NGTP': deque(maxlen=5),  # Initialize with a deque to keep track of last 10 NGSTP results
        'NGTP Streak': 0, 'YGTP Streak': 0  # Initialize streaks
    })

    # Define divisions
    divisions = {
        'Atlantic': ['Red Wings', 'Lightning', 'Panthers', 'Canadiens', 'Maple Leafs', 'Bruins', 'Sabres', 'Senators'],
        'Central': ['Stars', 'Blues', 'Wild', 'Predators', 'Jets', 'Utah Hockey Club', 'Blackhawks', 'Avalanche'],
        'Metropolitan': ['Devils', 'Islanders', 'Capitals', 'Rangers', 'Hurricanes', 'Flyers', 'Penguins', 'Blue Jackets'],
        'Pacific': ['Kraken', 'Sharks', 'Flames', 'Golden Knights', 'Canucks', 'Ducks', 'Kings', 'Oilers'],
    }

    team_to_division = {}
    for division, teams in divisions.items():
        for team in teams:
            team_to_division[team] = division


    # Read the CSV file
    with open(filename, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            away_team = row['Away Team']
            home_team = row['Home Team']
            away_goals = int(row['Away Team Goals'])
            home_goals = int(row['Home Team Goals'])
            away_goalie = row['Away Goalie']
            home_goalie = row['Home Goalie']
            away_goalie_goals = float(row['Away Goalie GA'])
            home_goalie_goals = float(row['Home Goalie GA'])
            home_goalie_gaa = row['Home GAA']
            away_goalie_gaa = row['Away GAA']

            # Check if the game is intradivision
            if team_to_division[away_team] == team_to_division[home_team]:
                intradivision_game = True
            else:
                intradivision_game = False

            # Update team counts
            team_counts[away_team]['Away'] += 1
            team_counts[away_team]['Away GS'] += away_goals
            team_counts[away_team]['Away GA'] += home_goals
            team_counts[away_team]['Away NGTP'] += 1 if (home_goals + away_goals) == 0 else 0
            team_counts[away_team]['Away YGTP'] += 1 if (home_goals + away_goals) > 0 else 0
            team_counts[away_team]['Away NGSTP'] += 1 if away_goals == 0 else 0
            team_counts[away_team]['Away YGSTP'] += 1 if away_goals > 0 else 0

            team_counts[home_team]['Home'] += 1
            team_counts[home_team]['Home GS'] += home_goals
            team_counts[home_team]['Home GA'] += away_goals
            team_counts[home_team]['Home NGTP'] += 1 if (home_goals + away_goals) == 0 else 0
            team_counts[home_team]['Home YGTP'] += 1 if (home_goals + away_goals) > 0 else 0
            team_counts[home_team]['Home NGSTP'] += 1 if home_goals == 0 else 0
            team_counts[home_team]['Home YGSTP'] += 1 if home_goals > 0 else 0

            # Update total NGTP and YGTP for teams
            team_counts[away_team]['Total NGTP'] = team_counts[away_team]['Away NGTP'] + team_counts[away_team]['Home NGTP']
            team_counts[away_team]['Total YGTP'] = team_counts[away_team]['Away YGTP'] + team_counts[away_team]['Home YGTP']
            team_counts[away_team]['Total NGSTP'] = team_counts[away_team]['Away NGSTP'] + team_counts[away_team]['Home NGSTP']
            team_counts[away_team]['Total YGSTP'] = team_counts[away_team]['Away YGSTP'] + team_counts[away_team]['Home YGSTP']

            team_counts[home_team]['Total NGTP'] = team_counts[home_team]['Away NGTP'] + team_counts[home_team]['Home NGTP']
            team_counts[home_team]['Total YGTP'] = team_counts[home_team]['Away YGTP'] + team_counts[home_team]['Home YGTP']
            team_counts[home_team]['Total NGSTP'] = team_counts[home_team]['Away NGSTP'] + team_counts[home_team]['Home NGSTP']
            team_counts[home_team]['Total YGSTP'] = team_counts[home_team]['Away YGSTP'] + team_counts[home_team]['Home YGSTP']

            # Update intradivision counts
            if intradivision_game:
                team_counts[away_team]['Intra NGTP'] += 1 if (home_goals + away_goals) == 0 else 0
                team_counts[away_team]['Intra YGTP'] += 1 if (home_goals + away_goals) > 0 else 0
                team_counts[away_team]['Intra NGSTP'] += 1 if away_goals == 0 else 0
                team_counts[away_team]['Intra YGSTP'] += 1 if away_goals > 0 else 0

                team_counts[home_team]['Intra NGTP'] += 1 if (home_goals + away_goals) == 0 else 0
                team_counts[home_team]['Intra YGTP'] += 1 if (home_goals + away_goals) > 0 else 0
                team_counts[home_team]['Intra NGSTP'] += 1 if home_goals == 0 else 0
                team_counts[home_team]['Intra YGSTP'] += 1 if home_goals > 0 else 0

            # Update goalie counts
            goalie_counts[away_goalie]['Away'] += 1
            goalie_counts[away_goalie]['Away GA'] += away_goalie_goals
            goalie_counts[away_goalie]['Away NGTP'] += 1 if away_goalie_goals == 0 else 0
            goalie_counts[away_goalie]['Away YGTP'] += 1 if away_goalie_goals > 0 else 0
            goalie_counts[away_goalie]['Season GAA'] = away_goalie_gaa

            goalie_counts[home_goalie]['Home'] += 1
            goalie_counts[home_goalie]['Home GA'] += home_goalie_goals
            goalie_counts[home_goalie]['Home NGTP'] += 1 if home_goalie_goals == 0 else 0
            goalie_counts[home_goalie]['Home YGTP'] += 1 if home_goalie_goals > 0 else 0
            goalie_counts[home_goalie]['Season GAA'] = home_goalie_gaa

            # Update total NGTP and YGTP for goalies
            goalie_counts[away_goalie]['Total NGTP'] = goalie_counts[away_goalie]['Away NGTP'] + goalie_counts[away_goalie]['Home NGTP']
            goalie_counts[away_goalie]['Total YGTP'] = goalie_counts[away_goalie]['Away YGTP'] + goalie_counts[away_goalie]['Home YGTP']

            goalie_counts[home_goalie]['Total NGTP'] = goalie_counts[home_goalie]['Away NGTP'] + goalie_counts[home_goalie]['Home NGTP']
            goalie_counts[home_goalie]['Total YGTP'] = goalie_counts[home_goalie]['Away YGTP'] + goalie_counts[home_goalie]['Home YGTP']

            # Update the last 10 NGSTP results for both teams
            team_counts[away_team]['L10 NGSTP'].append(1 if away_goals == 0 else 0)
            team_counts[home_team]['L10 NGSTP'].append(1 if home_goals == 0 else 0)
            goalie_counts[away_goalie]['L5 NGTP'].append(1 if home_goals == 0 else 0)
            goalie_counts[home_goalie]['L5 NGTP'].append(1 if away_goals == 0 else 0)


            # Update NGSTP and YGSTP streaks for both teams
            if away_goals == 0:
                team_counts[away_team]['NGSTP Streak'] += 1
                team_counts[away_team]['YGSTP Streak'] = 0
                goalie_counts[home_goalie]['NGTP Streak'] += 1
                goalie_counts[home_goalie]['YGTP Streak'] = 0
            else:
                team_counts[away_team]['NGSTP Streak'] = 0
                team_counts[away_team]['YGSTP Streak'] += 1
                goalie_counts[home_goalie]['NGTP Streak'] = 0
                goalie_counts[home_goalie]['YGTP Streak'] += 1

            if home_goals == 0:
                team_counts[home_team]['NGSTP Streak'] += 1
                team_counts[home_team]['YGSTP Streak'] = 0
                goalie_counts[away_goalie]['NGTP Streak'] += 1
                goalie_counts[away_goalie]['YGTP Streak'] = 0
            else:
                team_counts[home_team]['NGSTP Streak'] = 0
                team_counts[home_team]['YGSTP Streak'] += 1
                goalie_counts[away_goalie]['NGTP Streak'] = 0
                goalie_counts[away_goalie]['YGTP Streak'] += 1

    # Calculate L10 streak for each team
    for team, counts in team_counts.items():
        counts['L10 Streak'] = calculate_l10_streak(counts['L10 NGSTP'])

    for goalie, counts in goalie_counts.items():
        counts['L5 Streak'] = calculate_l5_streak(counts['L5 NGTP'])

    return team_counts, goalie_counts


# Function to calculate the L10 streak for a team
def calculate_l10_streak(l10_ngstp):
    return sum(l10_ngstp)


def calculate_l5_streak(l5_ngtp):
    return sum(l5_ngtp)


# Function to save team counts to CSV
def save_team_counts_to_csv(filename, team_counts):
    # Write to the CSV file
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        # Write header
        writer.writerow([
            'Name', 'Away', 'Away GS', 'Away GA', 'Away NGTP', 'Away YGTP', 'Away NGSTP', 'Away YGSTP',
            'Home', 'Home GS', 'Home GA', 'Home NGTP', 'Home YGTP', 'Home NGSTP', 'Home YGSTP',
            'Total NGTP', 'Total YGTP', 'Total NGSTP', 'Total YGSTP',
            'Intra NGTP', 'Intra YGTP', 'Intra NGSTP', 'Intra YGSTP',
            'L10 Streak',  # Add L10 Streak column
            'NGSTP Streak', 'YGSTP Streak'
        ])



        # Write team counts
        for team, counts in team_counts.items():
            writer.writerow([
                team,
                counts['Away'],
                counts['Away GS'],
                counts['Away GA'],
                counts['Away NGTP'],
                counts['Away YGTP'],
                counts['Away NGSTP'],
                counts['Away YGSTP'],
                counts['Home'],
                counts['Home GS'],
                counts['Home GA'],
                counts['Home NGTP'],
                counts['Home YGTP'],
                counts['Home NGSTP'],
                counts['Home YGSTP'],
                counts['Total NGTP'],
                counts['Total YGTP'],
                counts['Total NGSTP'],
                counts['Total YGSTP'],
                counts['Intra NGTP'],
                counts['Intra YGTP'],
                counts['Intra NGSTP'],
                counts['Intra YGSTP'],
                counts['L10 Streak'],
                counts['NGSTP Streak'],
                counts['YGSTP Streak']
            ])

# Function to save goalie counts to CSV
def save_goalie_counts_to_csv(filename, goalie_counts):
    # Write to the CSV file
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        # Write header
        writer.writerow([
            'Name', 'Away', 'Away GA', 'Away NGTP', 'Away YGTP', 'Away GAA',
            'Home', 'Home GA', 'Home NGTP', 'Home YGTP', 'Home GAA',
            'Total NGTP', 'Total YGTP', 'Season GAA',
            'L5 Streak',
            'NGTP Streak', 'YGTP Streak'
        ])

        # Write goalie counts
        for goalie, counts in goalie_counts.items():
            away_gaa = round(counts['Away GA'] * 3 / counts['Away'], 2) if counts['Away'] > 0 else 0
            home_gaa = round(counts['Home GA'] * 3 / counts['Home'], 2) if counts['Home'] > 0 else 0
            writer.writerow([
                goalie,
                counts['Away'],
                counts['Away GA'],
                counts['Away NGTP'],
                counts['Away YGTP'],
                away_gaa,
                counts['Home'],
                counts['Home GA'],
                counts['Home NGTP'],
                counts['Home YGTP'],
                home_gaa,
                counts['Total NGTP'],
                counts['Total YGTP'],
                counts['Season GAA'],
                counts['L5 Streak'],
                counts['NGTP Streak'],
                counts['YGTP Streak']
            ])

def main():
    input_filename = 'nhl_tp_gamelog.csv'
    team_output_filename = 'nhl_tp_team_data.csv'
    goalie_output_filename = 'nhl_tp_goalie_data.csv'

    team_counts, goalie_counts = count_appearances(input_filename)
    save_team_counts_to_csv(team_output_filename, team_counts)
    save_goalie_counts_to_csv(goalie_output_filename, goalie_counts)

if __name__ == '__main__':
    main()
