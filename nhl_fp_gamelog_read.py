import csv
from collections import defaultdict, deque

# Function to count team and goalie appearances
def count_appearances(filename):
    # Dictionaries to keep counts
    team_counts = defaultdict(lambda: {
        'Away': 0, 'Away GS': 0, 'Away GA': 0, 'Away NGFP': 0, 'Away YGFP': 0, 'Away NGSFP': 0, 'Away YGSFP': 0,
        'Home': 0, 'Home GS': 0, 'Home GA': 0, 'Home NGFP': 0, 'Home YGFP': 0, 'Home NGSFP': 0, 'Home YGSFP': 0,
        'Total NGFP': 0, 'Total YGFP': 0, 'Total NGSFP': 0, 'Total YGSFP': 0,
        'Intra NGFP': 0, 'Intra YGFP': 0, 'Intra NGSFP': 0, 'Intra YGSFP': 0,
        'L10 NGSFP': deque(maxlen=10),  # Initialize with a deque to keep track of last 10 NGSFP results
        'NGSFP Streak': 0, 'YGSFP Streak': 0  # Initialize streaks
    })

    goalie_counts = defaultdict(lambda: {
        'Away': 0, 'Away GA': 0, 'Away NGFP': 0, 'Away YGFP': 0,
        'Home': 0, 'Home GA': 0, 'Home NGFP': 0, 'Home YGFP': 0,
        'Total NGFP': 0, 'Total YGFP': 0,
        'Season GAA': 0,
        'L5 NGFP': deque(maxlen=5),  # Initialize with a deque to keep track of last 10 NGSFP results
        'NGFP Streak': 0, 'YGFP Streak': 0  # Initialize streaks
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
            team_counts[away_team]['Away NGFP'] += 1 if (home_goals + away_goals) == 0 else 0
            team_counts[away_team]['Away YGFP'] += 1 if (home_goals + away_goals) > 0 else 0
            team_counts[away_team]['Away NGSFP'] += 1 if away_goals == 0 else 0
            team_counts[away_team]['Away YGSFP'] += 1 if away_goals > 0 else 0

            team_counts[home_team]['Home'] += 1
            team_counts[home_team]['Home GS'] += home_goals
            team_counts[home_team]['Home GA'] += away_goals
            team_counts[home_team]['Home NGFP'] += 1 if (home_goals + away_goals) == 0 else 0
            team_counts[home_team]['Home YGFP'] += 1 if (home_goals + away_goals) > 0 else 0
            team_counts[home_team]['Home NGSFP'] += 1 if home_goals == 0 else 0
            team_counts[home_team]['Home YGSFP'] += 1 if home_goals > 0 else 0

            # Update total NGFP and YGFP for teams
            team_counts[away_team]['Total NGFP'] = team_counts[away_team]['Away NGFP'] + team_counts[away_team]['Home NGFP']
            team_counts[away_team]['Total YGFP'] = team_counts[away_team]['Away YGFP'] + team_counts[away_team]['Home YGFP']
            team_counts[away_team]['Total NGSFP'] = team_counts[away_team]['Away NGSFP'] + team_counts[away_team]['Home NGSFP']
            team_counts[away_team]['Total YGSFP'] = team_counts[away_team]['Away YGSFP'] + team_counts[away_team]['Home YGSFP']

            team_counts[home_team]['Total NGFP'] = team_counts[home_team]['Away NGFP'] + team_counts[home_team]['Home NGFP']
            team_counts[home_team]['Total YGFP'] = team_counts[home_team]['Away YGFP'] + team_counts[home_team]['Home YGFP']
            team_counts[home_team]['Total NGSFP'] = team_counts[home_team]['Away NGSFP'] + team_counts[home_team]['Home NGSFP']
            team_counts[home_team]['Total YGSFP'] = team_counts[home_team]['Away YGSFP'] + team_counts[home_team]['Home YGSFP']

            # Update intradivision counts
            if intradivision_game:
                team_counts[away_team]['Intra NGFP'] += 1 if (home_goals + away_goals) == 0 else 0
                team_counts[away_team]['Intra YGFP'] += 1 if (home_goals + away_goals) > 0 else 0
                team_counts[away_team]['Intra NGSFP'] += 1 if away_goals == 0 else 0
                team_counts[away_team]['Intra YGSFP'] += 1 if away_goals > 0 else 0

                team_counts[home_team]['Intra NGFP'] += 1 if (home_goals + away_goals) == 0 else 0
                team_counts[home_team]['Intra YGFP'] += 1 if (home_goals + away_goals) > 0 else 0
                team_counts[home_team]['Intra NGSFP'] += 1 if home_goals == 0 else 0
                team_counts[home_team]['Intra YGSFP'] += 1 if home_goals > 0 else 0

            # Update goalie counts
            goalie_counts[away_goalie]['Away'] += 1
            goalie_counts[away_goalie]['Away GA'] += away_goalie_goals
            goalie_counts[away_goalie]['Away NGFP'] += 1 if away_goalie_goals == 0 else 0
            goalie_counts[away_goalie]['Away YGFP'] += 1 if away_goalie_goals > 0 else 0
            goalie_counts[away_goalie]['Season GAA'] = away_goalie_gaa

            goalie_counts[home_goalie]['Home'] += 1
            goalie_counts[home_goalie]['Home GA'] += home_goalie_goals
            goalie_counts[home_goalie]['Home NGFP'] += 1 if home_goalie_goals == 0 else 0
            goalie_counts[home_goalie]['Home YGFP'] += 1 if home_goalie_goals > 0 else 0
            goalie_counts[home_goalie]['Season GAA'] = home_goalie_gaa

            # Update total NGFP and YGFP for goalies
            goalie_counts[away_goalie]['Total NGFP'] = goalie_counts[away_goalie]['Away NGFP'] + goalie_counts[away_goalie]['Home NGFP']
            goalie_counts[away_goalie]['Total YGFP'] = goalie_counts[away_goalie]['Away YGFP'] + goalie_counts[away_goalie]['Home YGFP']

            goalie_counts[home_goalie]['Total NGFP'] = goalie_counts[home_goalie]['Away NGFP'] + goalie_counts[home_goalie]['Home NGFP']
            goalie_counts[home_goalie]['Total YGFP'] = goalie_counts[home_goalie]['Away YGFP'] + goalie_counts[home_goalie]['Home YGFP']

            # Update the last 10 NGSFP results for both teams
            team_counts[away_team]['L10 NGSFP'].append(1 if away_goals == 0 else 0)
            team_counts[home_team]['L10 NGSFP'].append(1 if home_goals == 0 else 0)
            goalie_counts[away_goalie]['L5 NGFP'].append(1 if home_goals == 0 else 0)
            goalie_counts[home_goalie]['L5 NGFP'].append(1 if away_goals == 0 else 0)


            # Update NGSFP and YGSFP streaks for both teams
            if away_goals == 0:
                team_counts[away_team]['NGSFP Streak'] += 1
                team_counts[away_team]['YGSFP Streak'] = 0
                goalie_counts[home_goalie]['NGFP Streak'] += 1
                goalie_counts[home_goalie]['YGFP Streak'] = 0
            else:
                team_counts[away_team]['NGSFP Streak'] = 0
                team_counts[away_team]['YGSFP Streak'] += 1
                goalie_counts[home_goalie]['NGFP Streak'] = 0
                goalie_counts[home_goalie]['YGFP Streak'] += 1

            if home_goals == 0:
                team_counts[home_team]['NGSFP Streak'] += 1
                team_counts[home_team]['YGSFP Streak'] = 0
                goalie_counts[away_goalie]['NGFP Streak'] += 1
                goalie_counts[away_goalie]['YGFP Streak'] = 0
            else:
                team_counts[home_team]['NGSFP Streak'] = 0
                team_counts[home_team]['YGSFP Streak'] += 1
                goalie_counts[away_goalie]['NGFP Streak'] = 0
                goalie_counts[away_goalie]['YGFP Streak'] += 1

    # Calculate L10 streak for each team
    for team, counts in team_counts.items():
        counts['L10 Streak'] = calculate_l10_streak(counts['L10 NGSFP'])

    for goalie, counts in goalie_counts.items():
        counts['L5 Streak'] = calculate_l5_streak(counts['L5 NGFP'])

    return team_counts, goalie_counts


# Function to calculate the L10 streak for a team
def calculate_l10_streak(l10_ngsfp):
    return sum(l10_ngsfp)


def calculate_l5_streak(l5_ngfp):
    return sum(l5_ngfp)


# Function to save team counts to CSV
def save_team_counts_to_csv(filename, team_counts):
    # Write to the CSV file
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        # Write header
        writer.writerow([
            'Name', 'Away', 'Away GS', 'Away GA', 'Away NGFP', 'Away YGFP', 'Away NGSFP', 'Away YGSFP',
            'Home', 'Home GS', 'Home GA', 'Home NGFP', 'Home YGFP', 'Home NGSFP', 'Home YGSFP',
            'Total NGFP', 'Total YGFP', 'Total NGSFP', 'Total YGSFP',
            'Intra NGFP', 'Intra YGFP', 'Intra NGSFP', 'Intra YGSFP',
            'L10 Streak',  # Add L10 Streak column
            'NGSFP Streak', 'YGSFP Streak'
        ])



        # Write team counts
        for team, counts in team_counts.items():
            writer.writerow([
                team,
                counts['Away'],
                counts['Away GS'],
                counts['Away GA'],
                counts['Away NGFP'],
                counts['Away YGFP'],
                counts['Away NGSFP'],
                counts['Away YGSFP'],
                counts['Home'],
                counts['Home GS'],
                counts['Home GA'],
                counts['Home NGFP'],
                counts['Home YGFP'],
                counts['Home NGSFP'],
                counts['Home YGSFP'],
                counts['Total NGFP'],
                counts['Total YGFP'],
                counts['Total NGSFP'],
                counts['Total YGSFP'],
                counts['Intra NGFP'],
                counts['Intra YGFP'],
                counts['Intra NGSFP'],
                counts['Intra YGSFP'],
                counts['L10 Streak'],
                counts['NGSFP Streak'],
                counts['YGSFP Streak']
            ])

# Function to save goalie counts to CSV
def save_goalie_counts_to_csv(filename, goalie_counts):
    # Write to the CSV file
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        # Write header
        writer.writerow([
            'Name', 'Away', 'Away GA', 'Away NGFP', 'Away YGFP', 'Away GAA',
            'Home', 'Home GA', 'Home NGFP', 'Home YGFP', 'Home GAA',
            'Total NGFP', 'Total YGFP', 'Season GAA',
            'L5 Streak',
            'NGFP Streak', 'YGFP Streak'
        ])

        # Write goalie counts
        for goalie, counts in goalie_counts.items():
            away_gaa = round(counts['Away GA'] * 3 / counts['Away'], 2) if counts['Away'] > 0 else 0
            home_gaa = round(counts['Home GA'] * 3 / counts['Home'], 2) if counts['Home'] > 0 else 0
            writer.writerow([
                goalie,
                counts['Away'],
                counts['Away GA'],
                counts['Away NGFP'],
                counts['Away YGFP'],
                away_gaa,
                counts['Home'],
                counts['Home GA'],
                counts['Home NGFP'],
                counts['Home YGFP'],
                home_gaa,
                counts['Total NGFP'],
                counts['Total YGFP'],
                counts['Season GAA'],
                counts['L5 Streak'],
                counts['NGFP Streak'],
                counts['YGFP Streak']
            ])

def main():
    input_filename = 'nhl_fp_gamelog.csv'
    team_output_filename = 'nhl_fp_team_data.csv'
    goalie_output_filename = 'nhl_fp_goalie_data.csv'

    team_counts, goalie_counts = count_appearances(input_filename)
    save_team_counts_to_csv(team_output_filename, team_counts)
    save_goalie_counts_to_csv(goalie_output_filename, goalie_counts)

if __name__ == '__main__':
    main()
