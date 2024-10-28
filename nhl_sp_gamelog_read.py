import csv
from collections import defaultdict, deque

# Function to count team and goalie appearances
def count_appearances(filename):
    # Dictionaries to keep counts
    team_counts = defaultdict(lambda: {
        'Away': 0, 'Away GS': 0, 'Away GA': 0, 'Away NGSP': 0, 'Away YGSP': 0, 'Away NGSSP': 0, 'Away YGSSP': 0,
        'Home': 0, 'Home GS': 0, 'Home GA': 0, 'Home NGSP': 0, 'Home YGSP': 0, 'Home NGSSP': 0, 'Home YGSSP': 0,
        'Total NGSP': 0, 'Total YGSP': 0, 'Total NGSSP': 0, 'Total YGSSP': 0,
        'Intra NGSP': 0, 'Intra YGSP': 0, 'Intra NGSSP': 0, 'Intra YGSSP': 0,
        'L10 NGSSP': deque(maxlen=10),  # Initialize with a deque to keep track of last 10 NGSSP results
        'NGSSP Streak': 0, 'YGSSP Streak': 0  # Initialize streaks
    })

    goalie_counts = defaultdict(lambda: {
        'Away': 0, 'Away GA': 0, 'Away NGSP': 0, 'Away YGSP': 0,
        'Home': 0, 'Home GA': 0, 'Home NGSP': 0, 'Home YGSP': 0,
        'Total NGSP': 0, 'Total YGSP': 0,
        'Season GAA': 0,
        'L5 NGSP': deque(maxlen=5),  # Initialize with a deque to keep track of last 10 NGSSP results
        'NGSP Streak': 0, 'YGSP Streak': 0  # Initialize streaks
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
            team_counts[away_team]['Away NGSP'] += 1 if (home_goals + away_goals) == 0 else 0
            team_counts[away_team]['Away YGSP'] += 1 if (home_goals + away_goals) > 0 else 0
            team_counts[away_team]['Away NGSSP'] += 1 if away_goals == 0 else 0
            team_counts[away_team]['Away YGSSP'] += 1 if away_goals > 0 else 0

            team_counts[home_team]['Home'] += 1
            team_counts[home_team]['Home GS'] += home_goals
            team_counts[home_team]['Home GA'] += away_goals
            team_counts[home_team]['Home NGSP'] += 1 if (home_goals + away_goals) == 0 else 0
            team_counts[home_team]['Home YGSP'] += 1 if (home_goals + away_goals) > 0 else 0
            team_counts[home_team]['Home NGSSP'] += 1 if home_goals == 0 else 0
            team_counts[home_team]['Home YGSSP'] += 1 if home_goals > 0 else 0

            # Update total NGSP and YGSP for teams
            team_counts[away_team]['Total NGSP'] = team_counts[away_team]['Away NGSP'] + team_counts[away_team]['Home NGSP']
            team_counts[away_team]['Total YGSP'] = team_counts[away_team]['Away YGSP'] + team_counts[away_team]['Home YGSP']
            team_counts[away_team]['Total NGSSP'] = team_counts[away_team]['Away NGSSP'] + team_counts[away_team]['Home NGSSP']
            team_counts[away_team]['Total YGSSP'] = team_counts[away_team]['Away YGSSP'] + team_counts[away_team]['Home YGSSP']

            team_counts[home_team]['Total NGSP'] = team_counts[home_team]['Away NGSP'] + team_counts[home_team]['Home NGSP']
            team_counts[home_team]['Total YGSP'] = team_counts[home_team]['Away YGSP'] + team_counts[home_team]['Home YGSP']
            team_counts[home_team]['Total NGSSP'] = team_counts[home_team]['Away NGSSP'] + team_counts[home_team]['Home NGSSP']
            team_counts[home_team]['Total YGSSP'] = team_counts[home_team]['Away YGSSP'] + team_counts[home_team]['Home YGSSP']

            # Update intradivision counts
            if intradivision_game:
                team_counts[away_team]['Intra NGSP'] += 1 if (home_goals + away_goals) == 0 else 0
                team_counts[away_team]['Intra YGSP'] += 1 if (home_goals + away_goals) > 0 else 0
                team_counts[away_team]['Intra NGSSP'] += 1 if away_goals == 0 else 0
                team_counts[away_team]['Intra YGSSP'] += 1 if away_goals > 0 else 0

                team_counts[home_team]['Intra NGSP'] += 1 if (home_goals + away_goals) == 0 else 0
                team_counts[home_team]['Intra YGSP'] += 1 if (home_goals + away_goals) > 0 else 0
                team_counts[home_team]['Intra NGSSP'] += 1 if home_goals == 0 else 0
                team_counts[home_team]['Intra YGSSP'] += 1 if home_goals > 0 else 0

            # Update goalie counts
            goalie_counts[away_goalie]['Away'] += 1
            goalie_counts[away_goalie]['Away GA'] += away_goalie_goals
            goalie_counts[away_goalie]['Away NGSP'] += 1 if away_goalie_goals == 0 else 0
            goalie_counts[away_goalie]['Away YGSP'] += 1 if away_goalie_goals > 0 else 0
            goalie_counts[away_goalie]['Season GAA'] = away_goalie_gaa

            goalie_counts[home_goalie]['Home'] += 1
            goalie_counts[home_goalie]['Home GA'] += home_goalie_goals
            goalie_counts[home_goalie]['Home NGSP'] += 1 if home_goalie_goals == 0 else 0
            goalie_counts[home_goalie]['Home YGSP'] += 1 if home_goalie_goals > 0 else 0
            goalie_counts[home_goalie]['Season GAA'] = home_goalie_gaa

            # Update total NGSP and YGSP for goalies
            goalie_counts[away_goalie]['Total NGSP'] = goalie_counts[away_goalie]['Away NGSP'] + goalie_counts[away_goalie]['Home NGSP']
            goalie_counts[away_goalie]['Total YGSP'] = goalie_counts[away_goalie]['Away YGSP'] + goalie_counts[away_goalie]['Home YGSP']

            goalie_counts[home_goalie]['Total NGSP'] = goalie_counts[home_goalie]['Away NGSP'] + goalie_counts[home_goalie]['Home NGSP']
            goalie_counts[home_goalie]['Total YGSP'] = goalie_counts[home_goalie]['Away YGSP'] + goalie_counts[home_goalie]['Home YGSP']

            # Update the last 10 NGSSP results for both teams
            team_counts[away_team]['L10 NGSSP'].append(1 if away_goals == 0 else 0)
            team_counts[home_team]['L10 NGSSP'].append(1 if home_goals == 0 else 0)
            goalie_counts[away_goalie]['L5 NGSP'].append(1 if home_goals == 0 else 0)
            goalie_counts[home_goalie]['L5 NGSP'].append(1 if away_goals == 0 else 0)


            # Update NGSSP and YGSSP streaks for both teams
            if away_goals == 0:
                team_counts[away_team]['NGSSP Streak'] += 1
                team_counts[away_team]['YGSSP Streak'] = 0
                goalie_counts[home_goalie]['NGSP Streak'] += 1
                goalie_counts[home_goalie]['YGSP Streak'] = 0
            else:
                team_counts[away_team]['NGSSP Streak'] = 0
                team_counts[away_team]['YGSSP Streak'] += 1
                goalie_counts[home_goalie]['NGSP Streak'] = 0
                goalie_counts[home_goalie]['YGSP Streak'] += 1

            if home_goals == 0:
                team_counts[home_team]['NGSSP Streak'] += 1
                team_counts[home_team]['YGSSP Streak'] = 0
                goalie_counts[away_goalie]['NGSP Streak'] += 1
                goalie_counts[away_goalie]['YGSP Streak'] = 0
            else:
                team_counts[home_team]['NGSSP Streak'] = 0
                team_counts[home_team]['YGSSP Streak'] += 1
                goalie_counts[away_goalie]['NGSP Streak'] = 0
                goalie_counts[away_goalie]['YGSP Streak'] += 1

    # Calculate L10 streak for each team
    for team, counts in team_counts.items():
        counts['L10 Streak'] = calculate_l10_streak(counts['L10 NGSSP'])

    for goalie, counts in goalie_counts.items():
        counts['L5 Streak'] = calculate_l5_streak(counts['L5 NGSP'])

    return team_counts, goalie_counts


# Function to calculate the L10 streak for a team
def calculate_l10_streak(l10_ngssp):
    return sum(l10_ngssp)


def calculate_l5_streak(l5_ngsp):
    return sum(l5_ngsp)


# Function to save team counts to CSV
def save_team_counts_to_csv(filename, team_counts):
    # Write to the CSV file
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        # Write header
        writer.writerow([
            'Name', 'Away', 'Away GS', 'Away GA', 'Away NGSP', 'Away YGSP', 'Away NGSSP', 'Away YGSSP',
            'Home', 'Home GS', 'Home GA', 'Home NGSP', 'Home YGSP', 'Home NGSSP', 'Home YGSSP',
            'Total NGSP', 'Total YGSP', 'Total NGSSP', 'Total YGSSP',
            'Intra NGSP', 'Intra YGSP', 'Intra NGSSP', 'Intra YGSSP',
            'L10 Streak',  # Add L10 Streak column
            'NGSSP Streak', 'YGSSP Streak'
        ])



        # Write team counts
        for team, counts in team_counts.items():
            writer.writerow([
                team,
                counts['Away'],
                counts['Away GS'],
                counts['Away GA'],
                counts['Away NGSP'],
                counts['Away YGSP'],
                counts['Away NGSSP'],
                counts['Away YGSSP'],
                counts['Home'],
                counts['Home GS'],
                counts['Home GA'],
                counts['Home NGSP'],
                counts['Home YGSP'],
                counts['Home NGSSP'],
                counts['Home YGSSP'],
                counts['Total NGSP'],
                counts['Total YGSP'],
                counts['Total NGSSP'],
                counts['Total YGSSP'],
                counts['Intra NGSP'],
                counts['Intra YGSP'],
                counts['Intra NGSSP'],
                counts['Intra YGSSP'],
                counts['L10 Streak'],
                counts['NGSSP Streak'],
                counts['YGSSP Streak']
            ])

# Function to save goalie counts to CSV
def save_goalie_counts_to_csv(filename, goalie_counts):
    # Write to the CSV file
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        # Write header
        writer.writerow([
            'Name', 'Away', 'Away GA', 'Away NGSP', 'Away YGSP', 'Away GAA',
            'Home', 'Home GA', 'Home NGSP', 'Home YGSP', 'Home GAA',
            'Total NGSP', 'Total YGSP', 'Season GAA',
            'L5 Streak',
            'NGSP Streak', 'YGSP Streak'
        ])

        # Write goalie counts
        for goalie, counts in goalie_counts.items():
            away_gaa = round(counts['Away GA'] * 3 / counts['Away'], 2) if counts['Away'] > 0 else 0
            home_gaa = round(counts['Home GA'] * 3 / counts['Home'], 2) if counts['Home'] > 0 else 0
            writer.writerow([
                goalie,
                counts['Away'],
                counts['Away GA'],
                counts['Away NGSP'],
                counts['Away YGSP'],
                away_gaa,
                counts['Home'],
                counts['Home GA'],
                counts['Home NGSP'],
                counts['Home YGSP'],
                home_gaa,
                counts['Total NGSP'],
                counts['Total YGSP'],
                counts['Season GAA'],
                counts['L5 Streak'],
                counts['NGSP Streak'],
                counts['YGSP Streak']
            ])

def main():
    input_filename = 'nhl_sp_gamelog.csv'
    team_output_filename = 'nhl_sp_team_data.csv'
    goalie_output_filename = 'nhl_sp_goalie_data.csv'

    team_counts, goalie_counts = count_appearances(input_filename)
    save_team_counts_to_csv(team_output_filename, team_counts)
    save_goalie_counts_to_csv(goalie_output_filename, goalie_counts)

if __name__ == '__main__':
    main()
