from flask import Flask, render_template
import pandas as pd
import datetime
import unicodedata
import math
import numpy as np

app = Flask(__name__)


# Define divisions
divisions = {
    'Atlantic': ['Red Wings', 'Lightning', 'Panthers', 'Canadiens', 'Maple Leafs', 'Bruins', 'Sabres', 'Senators'],
    'Central': ['Stars', 'Blues', 'Wild', 'Predators', 'Jets', 'Utah Hockey Club', 'Blackhawks', 'Avalanche'],
    'Metropolitan': ['Devils', 'Islanders', 'Capitals', 'Rangers', 'Hurricanes', 'Flyers', 'Penguins', 'Blue Jackets'],
    'Pacific': ['Kraken', 'Sharks', 'Flames', 'Golden Knights', 'Canucks', 'Ducks', 'Kings', 'Oilers'],
}

def format_goalie_name(name):
    """
    Convert goalie name from 'Figst Last' to 'F. Last' and handle three-word names.
    Handles special charactegs by normalizing to ASCII.
    """
    # Normalize the name to remove accents and other diacritics
    normalized_name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('ASCII')

    # # Split the normalized name into parts
    # parts = normalized_name.split()
    #
    # if len(parts) == 2:
    #     return f"{parts[0][0]}. {parts[1]}"
    # elif len(parts) == 3:
    #     return f"{parts[0][0]}. {parts[1]} {parts[2]}"
    return normalized_name

def calculate_min_max(df, column):
    """Calculate the min and max values of a column in a DataFrame."""
    if column in df:
        return df[column].min(), df[column].max()
    return None, None

def calculate_color(value, min_val, max_val, inverse=False):
    """Calculate color based on value, min, and max."""
    if value == 'N/A' or pd.isna(value):
        return '#ffffff'
    ratio = (value - min_val) / (max_val - min_val)
    if inverse:
        green = int(255 * ratio)
        red = int(255 * (1 - ratio))
    else:
        green = int(255 * (1 - ratio))
        red = int(255 * ratio)
    return f'rgb({red},{green},0)'

def calculate_ngtp_color(value, min_val=0, max_val=100):
    """Calculate color for NGTP percentages based on a fixed scale (0 to 100)."""
    if value == 'N/A' or pd.isna(value):
        return '#ffffff'  # White for 'N/A' values

    # Ensure value is within the min-max range
    try:
        value = float(value)
    except ValueError:
        return '#ffffff'  # Return white for invalid numbers

    if value < min_val:
        value = min_val
    elif value > max_val:
        value = max_val

    # Scale value from 0 to 255 for color gradient
    ratio = (value - min_val) / (max_val - min_val)
    green = int(255 * ratio)   # Higher percentage (closer to 100) is more green
    red = int(255 * (1 - ratio))  # Lower percentage (closer to 0) is more red

    return f'rgb({red},{green},0)'

def calculate_ngstp_color(value, min_val=50, max_val=100):
    """Calculate color for NGTP percentages based on a fixed scale (0 to 100)."""
    if value == 'N/A' or pd.isna(value):
        return '#ffffff'  # White for 'N/A' values

    # Ensure value is within the min-max range
    try:
        value = float(value)
    except ValueError:
        return '#ffffff'  # Return white for invalid numbers

    if value < min_val:
        value = min_val
    elif value > max_val:
        value = max_val

    # Scale value from 0 to 255 for color gradient
    ratio = (value - min_val) / (max_val - min_val)
    green = int(255 * ratio)   # Higher percentage (closer to 100) is more green
    red = int(255 * (1 - ratio))  # Lower percentage (closer to 0) is more red

    return f'rgb({red},{green},0)'

def calculate_era_color(value, min_val=0, max_val=9):
    """Calculate color based on a scaled value from 0 to 9."""
    if value == 'N/A' or pd.isna(value):
        return '#ffffff'  # White for 'N/A' values

    # Convert value to a float
    try:
        value = float(value)
    except ValueError:
        return '#ffffff'  # Return white for invalid numbers

    # Ensure value is within the min-max range
    if value < min_val:
        value = min_val
    elif value > max_val:
        value = max_val

    # Scale value from 0 to 9
    scaled_value = 9 * (value - min_val) / (max_val - min_val)
    scaled_value = min(max(scaled_value, 0), 9)  # Ensure the value is between 0 and 9

    # Map scaled value to a color gradient
    red = int(255 * (scaled_value / 9))
    green = int(255 * (1 - scaled_value / 9))

    return f'rgb({red},{green},0)'

def calculate_streak_color(value):
    if value > 0:
        return '#00FF00'
    else:
        return '#FF0000'



@app.route('/')
def display_data():
    # Load data from the existing CSV files
    matchups_df = pd.read_csv('nhl_lineups.csv')
    team_data_df = pd.read_csv('nhl_tp_team_data.csv')
    goalie_data_df = pd.read_csv('nhl_tp_goalie_data.csv')

    # Calculate min and max values for relevant columns
    team_min_max = {
        'Away GS': calculate_min_max(team_data_df, 'Away GS'),
        'Away NGTP': calculate_min_max(team_data_df, 'Away NGTP'),
        'Away YGTP': calculate_min_max(team_data_df, 'Away YGTP'),

        'Home GS': calculate_min_max(team_data_df, 'Home GS'),
        'Home NGTP': calculate_min_max(team_data_df, 'Home NGTP'),
        'Home YGTP': calculate_min_max(team_data_df, 'Home YGTP')
    }

    goalie_min_max = {
        'Away GAA': calculate_min_max(goalie_data_df, 'Away GAA'),
        'Away GA': calculate_min_max(goalie_data_df, 'Away GA'),
        'Away NGTP': calculate_min_max(goalie_data_df, 'Away NGTP'),
        'Away YGTP': calculate_min_max(goalie_data_df, 'Away YGTP'),
        'Away Total NGTP': calculate_min_max(goalie_data_df, 'Total NGTP'),
        'Away Total YGTP': calculate_min_max(goalie_data_df, 'Total YGTP'),

        'Home GAA': calculate_min_max(goalie_data_df, 'Home GAA'),
        'Home GA': calculate_min_max(goalie_data_df, 'Home GA'),
        'Home NGTP': calculate_min_max(goalie_data_df, 'Home NGTP'),
        'Home YGTP': calculate_min_max(goalie_data_df, 'Home YGTP'),
        'Home Total NGTP': calculate_min_max(goalie_data_df, 'Total NGTP'),
        'Home Total YGTP': calculate_min_max(goalie_data_df, 'Total YGTP')
    }

    # Prepare a list to store the updated rows
    updated_data = []

    # Iterate over the rows in matchups_data.csv
    for _, row in matchups_df.iterrows():
        away_team = row['Away Team']
        home_team = row['Home Team']
        away_goalie = row['Away Goalie']
        home_goalie = row['Home Goalie']

        # Extract the data for the away team from mlb_team_data.csv
        away_team_data = team_data_df[team_data_df['Name'] == away_team]
        if not away_team_data.empty:
            away_team_data = away_team_data.iloc[0]
            away_team_gs = away_team_data['Away GS']
            away_team_ngtp = away_team_data['Away NGTP']
            away_team_ygtp = away_team_data['Away YGTP']
            away_team_ngstp = away_team_data['Away NGSTP']
            away_team_ygstp = away_team_data['Away YGSTP']
            away_team_total_ngtp = away_team_data['Total NGTP']
            away_team_total_ygtp = away_team_data['Total YGTP']
            away_team_total_ngstp = away_team_data['Total NGSTP']
            away_team_total_ygstp = away_team_data['Total YGSTP']
            away_team_intra_ngstp = away_team_data['Intra NGSTP']
            away_team_intra_ygstp = away_team_data['Intra YGSTP']
            away_team_l10_games = away_team_data['L10 Streak']
            away_team_ngstp_streak = away_team_data['NGSTP Streak']
            away_team_ygstp_streak = away_team_data['YGSTP Streak']
        else:
            away_team_gs = away_team_ngtp = away_team_ygtp = away_team_ngstp = away_team_ygstp = away_team_total_ngtp = away_team_total_ygtp = away_team_total_ngstp = away_team_total_ygstp = away_team_intra_ngstp = away_team_intra_ygstp = away_team_l10_games = away_team_ngstp_streak = away_team_ygstp_streak = 'N/A'

        # Extract the data for the home team from mlb_team_data.csv
        home_team_data = team_data_df[team_data_df['Name'] == home_team]
        if not home_team_data.empty:
            home_team_data = home_team_data.iloc[0]
            home_team_gs = home_team_data['Home GS']
            home_team_ngtp = home_team_data['Home NGTP']
            home_team_ygtp = home_team_data['Home YGTP']
            home_team_ngstp = home_team_data['Home NGSTP']
            home_team_ygstp = home_team_data['Home YGSTP']
            home_team_total_ngtp = home_team_data['Total NGTP']
            home_team_total_ygtp = home_team_data['Total YGTP']
            home_team_total_ngstp = home_team_data['Total NGSTP']
            home_team_total_ygstp = home_team_data['Total YGSTP']
            home_team_intra_ngstp = home_team_data['Intra NGSTP']
            home_team_intra_ygstp = home_team_data['Intra YGSTP']
            home_team_l10_games = home_team_data['L10 Streak']
            home_team_ngstp_streak = home_team_data['NGSTP Streak']
            home_team_ygstp_streak = home_team_data['YGSTP Streak']
        else:
            home_team_gs = home_team_ngtp = home_team_ygtp = home_team_ngstp = home_team_ygstp = home_team_total_ngtp = home_team_total_ygtp = home_team_total_ngstp = home_team_total_ygstp = home_team_intra_ngstp = home_team_intra_ygstp = home_team_l10_games = home_team_ngstp_streak = home_team_ygstp_streak = 'N/A'

        # Format goalie names for matching
        formatted_away_goalie = format_goalie_name(away_goalie)
        formatted_home_goalie = format_goalie_name(home_goalie)

        # Extract the data for the away goalie from mlb_goalie_data.csv
        away_goalie_data = goalie_data_df[goalie_data_df['Name'] == formatted_away_goalie]
        if not away_goalie_data.empty:
            away_goalie_data = away_goalie_data.iloc[0]
            away_gaa = away_goalie_data['Away GAA']
            away_ga = away_goalie_data['Away GA']
            away_ngtp = away_goalie_data['Away NGTP']
            away_ygtp = away_goalie_data['Away YGTP']
            away_total_ngtp = away_goalie_data['Total NGTP']
            away_total_ygtp = away_goalie_data['Total YGTP']
            away_goalie_l5_games = away_goalie_data['L5 Streak']
            away_goalie_ngtp_streak = away_goalie_data['NGTP Streak']
            away_goalie_ygtp_streak = away_goalie_data['YGTP Streak']
        else:
            away_gaa = away_ga = away_ngtp = away_ygtp = away_total_ngtp = away_total_ygtp = away_goalie_l5_games = away_goalie_ngtp_streak = away_goalie_ygtp_streak = 'N/A'

        # Extract the data for the home goalie from mlb_goalie_data.csv
        home_goalie_data = goalie_data_df[goalie_data_df['Name'] == formatted_home_goalie]
        if not home_goalie_data.empty:
            home_goalie_data = home_goalie_data.iloc[0]
            home_gaa = home_goalie_data['Home GAA']
            home_ga = home_goalie_data['Home GA']
            home_ngtp = home_goalie_data['Home NGTP']
            home_ygtp = home_goalie_data['Home YGTP']
            home_total_ngtp = home_goalie_data['Total NGTP']
            home_total_ygtp = home_goalie_data['Total YGTP']
            home_goalie_l5_games = home_goalie_data['L5 Streak']
            home_goalie_ngtp_streak = home_goalie_data['NGTP Streak']
            home_goalie_ygtp_streak = home_goalie_data['YGTP Streak']
        else:
            home_gaa = home_ga = home_ngtp = home_ygtp = home_total_ngtp = home_total_ygtp = home_goalie_l5_games = home_goalie_ngtp_streak = home_goalie_ygtp_streak = 'N/A'

        # Calculate cologs
        away_gs_color = calculate_color(away_team_gs, team_min_max['Away GS'][0], team_min_max['Away GS'][1])

        home_gs_color = calculate_color(home_team_gs, team_min_max['Home GS'][0], team_min_max['Home GS'][1])

        away_ga_goalie_color = calculate_color(away_ga, goalie_min_max['Away GA'][0], goalie_min_max['Away GA'][1])
        away_ngtp_goalie_color = calculate_color(away_ngtp, goalie_min_max['Away NGTP'][0], goalie_min_max['Away NGTP'][1], inverse=True)
        away_ygtp_goalie_color = calculate_color(away_ygtp, goalie_min_max['Away YGTP'][0], goalie_min_max['Away YGTP'][1])
        home_ga_goalie_color = calculate_color(home_ga, goalie_min_max['Home GA'][0], goalie_min_max['Home GA'][1])
        home_ngtp_goalie_color = calculate_color(home_ngtp, goalie_min_max['Home NGTP'][0], goalie_min_max['Home NGTP'][1], inverse=True)
        home_ygtp_goalie_color = calculate_color(home_ygtp, goalie_min_max['Home YGTP'][0], goalie_min_max['Home YGTP'][1])

        # Function to safely calculate percentages
        def safe_percentage(numerator, denominator):
            if isinstance(numerator, str) and numerator == 'N/A':
                return 'N/A'
            if isinstance(denominator, str) and denominator == 'N/A':
                return 'N/A'
            if np.isnan(numerator) or np.isnan(denominator) or denominator == 0:
                return 'N/A'

            return round((numerator / denominator) * 100)

        # Calculate NGTP percentages
        away_ngtp_percent = safe_percentage(away_team_ngtp, away_team_ngtp + away_team_ygtp)
        home_ngtp_percent = safe_percentage(home_team_ngtp, home_team_ngtp + home_team_ygtp)
        away_ngstp_percent = safe_percentage(away_team_ngstp, away_team_ngstp + away_team_ygstp)
        home_ngstp_percent = safe_percentage(home_team_ngstp, home_team_ngstp + home_team_ygstp)
        away_total_ngtp_percent = safe_percentage(away_team_total_ngtp, away_team_total_ngtp + away_team_total_ygtp)
        home_total_ngtp_percent = safe_percentage(home_team_total_ngtp, home_team_total_ngtp + home_team_total_ygtp)
        away_total_ngstp_percent = safe_percentage(away_team_total_ngstp, away_team_total_ngstp + away_team_total_ygstp)
        home_total_ngstp_percent = safe_percentage(home_team_total_ngstp, home_team_total_ngstp + home_team_total_ygstp)

        team_to_division = {}
        for division, teams in divisions.items():
            for team in teams:
                team_to_division[team] = division

        if (team_to_division[away_team] == team_to_division[home_team]):
            intradivision_game = True
        else:
            intradivision_game = False

        if intradivision_game == True:
            if away_team_intra_ngstp > 0:
                away_intra_ngstp_percent = round((away_team_intra_ngstp / (away_team_intra_ngstp + away_team_intra_ygstp)) * 100)
                home_intra_ngstp_percent = round((home_team_intra_ngstp / (home_team_intra_ngstp + home_team_intra_ygstp)) * 100)
            else:
                away_intra_ngstp_percent = 'N/A'
                home_intra_ngstp_percent = 'N/A'
        else:
            away_intra_ngstp_percent = 'N/A'
            home_intra_ngstp_percent = 'N/A'



        away_ngtp_goalie_percent = round((away_ngtp / (away_ngtp + away_ygtp)) * 100, 1) if (away_ngtp != 'N/A' and away_ygtp != 'N/A') else 'N/A'
        home_ngtp_goalie_percent = round((home_ngtp / (home_ngtp + home_ygtp)) * 100, 1) if (home_ngtp != 'N/A' and home_ygtp != 'N/A') else 'N/A'
        away_total_ngtp_goalie_percent = round((away_total_ngtp / (away_total_ngtp + away_total_ygtp)) * 100, 1) if (away_total_ngtp != 'N/A' and away_total_ygtp != 'N/A') else 'N/A'
        home_total_ngtp_goalie_percent = round((home_total_ngtp / (home_total_ngtp + home_total_ygtp)) * 100, 1) if (home_total_ngtp != 'N/A' and home_total_ygtp != 'N/A') else 'N/A'
        ngtp_pitchegs_percent = round(home_ngtp_goalie_percent * away_ngtp_goalie_percent / 100) if (home_ngtp_goalie_percent != 'N/A' and not pd.isna(home_ngtp_goalie_percent) and away_ngtp_goalie_percent != 'N/A' and not pd.isna(away_ngtp_goalie_percent)) else 'N/A'



        # Calculate cologs based on NGTP percentages
        away_ngtp_percent_color = calculate_ngtp_color(away_ngtp_percent)
        home_ngtp_percent_color = calculate_ngtp_color(home_ngtp_percent)
        away_ngstp_percent_color = calculate_ngstp_color(away_ngstp_percent)
        home_ngstp_percent_color = calculate_ngstp_color(home_ngstp_percent)
        away_total_ngtp_percent_color = calculate_ngtp_color(away_total_ngtp_percent)
        home_total_ngtp_percent_color = calculate_ngtp_color(home_total_ngtp_percent)
        away_total_ngstp_percent_color = calculate_ngstp_color(away_total_ngstp_percent)
        home_total_ngstp_percent_color = calculate_ngstp_color(home_total_ngstp_percent)
        away_intra_ngstp_percent_color = calculate_ngstp_color(away_intra_ngstp_percent)
        home_intra_ngstp_percent_color = calculate_ngstp_color(home_intra_ngstp_percent)


        away_ngtp_goalie_percent_color = calculate_ngtp_color(away_ngtp_goalie_percent)
        home_ngtp_goalie_percent_color = calculate_ngtp_color(home_ngtp_goalie_percent)
        away_total_ngtp_goalie_percent_color = calculate_ngtp_color(away_total_ngtp_goalie_percent)
        home_total_ngtp_goalie_percent_color = calculate_ngtp_color(home_total_ngtp_goalie_percent)
        ngtp_pitchegs_percent_color = calculate_ngtp_color(ngtp_pitchegs_percent)

        # Calculate cologs based on GAA
        away_gaa_color = calculate_era_color(away_gaa)
        home_gaa_color = calculate_era_color(home_gaa)

        if home_team_ngstp_streak > 0:
            home_streak = home_team_ngstp_streak
        else:
            home_streak = home_team_ygstp_streak

        if away_team_ngstp_streak > 0:
            away_streak = away_team_ngstp_streak
        else:
            away_streak = away_team_ygstp_streak

        home_streak_color = calculate_streak_color(home_team_ngstp_streak)
        away_streak_color = calculate_streak_color(away_team_ngstp_streak)

        if home_goalie_ngtp_streak != 'N/A' and home_goalie_ngtp_streak > 0:
            home_goalie_streak = home_goalie_ngtp_streak
        elif home_goalie_ygtp_streak != 'N/A':
            home_goalie_streak = home_goalie_ygtp_streak
        else:
            home_goalie_streak = 'N/A'

        if away_goalie_ngtp_streak != 'N/A' and away_goalie_ngtp_streak > 0:
            away_goalie_streak = away_goalie_ngtp_streak
        elif away_goalie_ygtp_streak != 'N/A':
            away_goalie_streak = away_goalie_ygtp_streak
        else:
            away_goalie_streak = 'N/A'

        if home_goalie_streak != 'N/A':
            home_goalie_streak_color = calculate_streak_color(home_goalie_ngtp_streak)
        else:
            home_goalie_streak_color = 'N/A'

        if away_goalie_streak != 'N/A':
            away_goalie_streak_color = calculate_streak_color(away_goalie_ngtp_streak)
        else:
            away_goalie_streak_color = 'N/A'











        def safe_float(value):
            try:
                return float(value)
            except (ValueError, TypeError):
                return float('nan')  # or a default value like 0

        algo_away_goalie = 'N/A'
        algo_home_goalie = 'N/A'
        algo_away_team = 'N/A'
        algo_home_team = 'N/A'

        if away_ngtp_goalie_percent != 'N/A':
            away_ngtp_goalie_percent = safe_float(away_ngtp_goalie_percent)
            away_total_ngtp_goalie_percent = safe_float(away_total_ngtp_goalie_percent)
            if (away_ngtp+away_ygtp) >= 2 and (away_total_ngtp+away_total_ygtp) >= 5:
                if away_goalie_ngtp_streak > 0:
                    algo_away_goalie = ((away_ngtp_goalie_percent * 2) + away_total_ngtp_goalie_percent) / 3 + (3 * (away_goalie_l5_games - 2)) + (2 * (away_goalie_ngtp_streak))
                elif away_goalie_ygtp_streak > 0:
                    algo_away_goalie = ((away_ngtp_goalie_percent * 2) + away_total_ngtp_goalie_percent) / 3 + (3 * (away_goalie_l5_games - 2)) - (2 * (away_goalie_ygtp_streak))

        if home_ngtp_goalie_percent != 'N/A':
            home_ngtp_goalie_percent = safe_float(home_ngtp_goalie_percent)
            home_total_ngtp_goalie_percent = safe_float(home_total_ngtp_goalie_percent)
            if (home_ngtp+home_ygtp) >= 2 and (home_total_ngtp+home_total_ygtp) >= 5:
                if home_goalie_ngtp_streak > 0:
                    algo_home_goalie = ((home_ngtp_goalie_percent * 2) + home_total_ngtp_goalie_percent) / 3 + (3 * (home_goalie_l5_games - 2)) + (2 * (home_goalie_ngtp_streak))
                elif home_goalie_ygtp_streak > 0:
                    algo_home_goalie = ((home_ngtp_goalie_percent * 2) + home_total_ngtp_goalie_percent) / 3 + (3 * (home_goalie_l5_games - 2)) - (2 * (home_goalie_ygtp_streak))

        # Convert all necessary variables to floats
        away_ngstp_percent = safe_float(away_ngstp_percent)
        away_intra_ngstp_percent = safe_float(away_intra_ngstp_percent)
        home_ngstp_percent = safe_float(home_ngstp_percent)
        home_intra_ngstp_percent = safe_float(home_intra_ngstp_percent)

        if away_team_ngstp_streak > 0:
            if not math.isnan(away_intra_ngstp_percent):
                #algo_away_team = ((away_ngstp_percent) / 2 + away_intra_ngstp_percent) / 2 + (2 * (away_team_l10_games - 7)) + (1 / 2 * (away_team_ngstp_streak))
                algo_away_team = (((away_ngstp_percent * 5) + (away_intra_ngstp_percent * 3) + ((away_team_l10_games / 10) * 3)) / 12) + (2 * (away_team_ngstp_streak))
            else:
                #algo_away_team = ((away_ngstp_percent) ) + (2 * (away_team_l10_games - 7)) + (1 / 2 * (away_team_ngstp_streak))
                algo_away_team = (((away_ngstp_percent * 7) + ((away_team_l10_games / 10) * 5)) / 12) + (2 * (away_team_ngstp_streak))
        elif away_team_ygstp_streak > 0:
            if not math.isnan(away_intra_ngstp_percent):
                #algo_away_team = ((away_ngstp_percent) / 2 + away_intra_ngstp_percent) / 2 + (2 * (away_team_l10_games - 7)) - (1 / 2 * (away_team_ygstp_streak))
                algo_away_team = (((away_ngstp_percent * 5) + (away_intra_ngstp_percent * 3) + ((away_team_l10_games / 10) * 3)) / 12) - (2 * (away_team_ygstp_streak))
            else:
                #algo_away_team = ((away_ngstp_percent) / 2) + (2 * (away_team_l10_games - 7)) - (1 / 2 * (away_team_ygstp_streak))
                algo_away_team = (((away_ngstp_percent * 7) + ((away_team_l10_games / 10) * 5)) / 12) - (2 * (away_team_ygstp_streak))

        if home_team_ngstp_streak > 0:
            if not math.isnan(home_intra_ngstp_percent):
                #algo_home_team = ((home_ngstp_percent) / 2 + home_intra_ngstp_percent) / 2 + (2 * (home_team_l10_games - 7)) + (1 / 2 * (home_team_ngstp_streak))
                algo_home_team = (((home_ngstp_percent * 5) + (home_intra_ngstp_percent * 3) + ((home_team_l10_games / 10) * 3)) / 12) + (2 * (home_team_ngstp_streak))
            else:
                #algo_home_team = ((home_ngstp_percent) ) + (2 * (home_team_l10_games - 7)) + (1 / 2 * (home_team_ngstp_streak))
                algo_home_team = (((home_ngstp_percent * 7) + ((home_team_l10_games / 10) * 5)) / 12) + (2 * (home_team_ngstp_streak))
        elif home_team_ygstp_streak > 0:
            if not math.isnan(home_intra_ngstp_percent):
                #algo_home_team = ((home_ngstp_percent) / 2 + home_intra_ngstp_percent) / 2 + (2 * (home_team_l10_games - 7)) - (1 / 2 * (home_team_ygstp_streak))
                algo_home_team = (((home_ngstp_percent * 5) + (home_intra_ngstp_percent * 3) + ((home_team_l10_games / 10) * 3)) / 12) - (2 * (home_team_ygstp_streak))
            else:
                #algo_home_team = ((home_ngstp_percent) / 2) + (2 * (home_team_l10_games - 7)) - (1 / 2 * (home_team_ygstp_streak))
                algo_home_team = (((home_ngstp_percent * 7) + ((home_team_l10_games / 10) * 5)) / 12) - (2 * (home_team_ygstp_streak))



        if algo_away_goalie != 'N/A' and algo_home_team != 'N/A':
            if algo_home_team > 100:
                algo_home_team = 100
            if algo_away_goalie > 100:
                algo_away_goalie = 100
            if algo_home_team < 0:
                algo_home_team = 0
            if algo_away_goalie < 0:
                algo_away_goalie = 0

            algo_away_goalie = safe_float(algo_away_goalie) / 100
            algo_home_team = safe_float(algo_home_team) / 100

            home_algo_percentage = round(((algo_home_team + algo_away_goalie)/2) * 100, 1)
        else:
            home_algo_percentage = 'N/A'


        if algo_home_goalie != 'N/A' and algo_away_team != 'N/A':
            if algo_away_team > 100:
                algo_away_team = 100
            if algo_home_goalie > 100:
                algo_home_goalie = 100
            if algo_away_team < 0:
                algo_away_team = 0
            if algo_home_goalie < 0:
                algo_home_goalie = 0

            algo_home_goalie = safe_float(algo_home_goalie) / 100
            algo_away_team = safe_float(algo_away_team) / 100

            away_algo_percentage = round(((algo_away_team + algo_home_goalie)/2) * 100, 1)
        else:
            away_algo_percentage = 'N/A'


        if algo_away_goalie != 'N/A' and algo_home_goalie != 'N/A' and algo_away_team != 'N/A' and algo_home_team != 'N/A':
            # if algo_away_goalie > 100:
            #     algo_away_goalie = 100
            # if algo_home_goalie > 100:
            #     algo_home_goalie = 100
            # if algo_away_team > 100:
            #     algo_away_team = 100
            # if algo_home_team > 100:
            #     algo_home_team = 100
            #
            # algo_away_goalie = safe_float(algo_away_goalie) / 100
            # algo_home_goalie = safe_float(algo_home_goalie) / 100
            # algo_away_team = safe_float(algo_away_team) / 100
            # algo_home_team = safe_float(algo_home_team) / 100
            #
            # home_algo_percentage = round(((algo_home_team + algo_away_goalie)/2) * 100, 1)
            # away_algo_percentage = round(((algo_away_team + algo_home_goalie)/2) * 100, 1)
            algo_percentage = round(((algo_home_team + algo_away_goalie)/2) * ((algo_away_team + algo_home_goalie)/2) * 100, 1)
        else:
            algo_percentage = 'N/A'
            # home_algo_percentage = 'N/A'
            # away_algo_percentage = 'N/A'




        # Append the row with the extracted data and cologs to the updated_data list
        updated_data.append({
            'Away Team': away_team,
            'Away GS': away_team_gs,
            'Away GS Color': away_gs_color,
            'Away NGTP %': away_ngtp_percent,
            'Away NGTP % Color': away_ngtp_percent_color,
            'Away NGSTP %': away_ngstp_percent,
            'Away NGSTP % Color': away_ngstp_percent_color,
            'Away Total NGTP %': away_total_ngtp_percent,
            'Away Total NGTP % Color': away_total_ngtp_percent_color,
            'Away Total NGSTP %': away_total_ngstp_percent,
            'Away Total NGSTP % Color': away_total_ngstp_percent_color,
            'Away Intra NGSTP %': away_intra_ngstp_percent,
            'Away Intra NGSTP % Color': away_intra_ngstp_percent_color,

            'Away L10': away_team_l10_games,
            'Away Streak': away_streak,
            'Away Streak Color': away_streak_color,

            'Home Team': home_team,
            'Home GS': home_team_gs,
            'Home GS Color': home_gs_color,
            'Home NGTP %': home_ngtp_percent,
            'Home NGTP % Color': home_ngtp_percent_color,
            'Home NGSTP %': home_ngstp_percent,
            'Home NGSTP % Color': home_ngstp_percent_color,
            'Home Total NGTP %': home_total_ngtp_percent,
            'Home Total NGTP % Color': home_total_ngtp_percent_color,
            'Home Total NGSTP %': home_total_ngstp_percent,
            'Home Total NGSTP % Color': home_total_ngstp_percent_color,
            'Home Intra NGSTP %': home_intra_ngstp_percent,
            'Home Intra NGSTP % Color': home_intra_ngstp_percent_color,

            'Home L10': home_team_l10_games,
            'Home Streak': home_streak,
            'Home Streak Color': home_streak_color,

            # 'Away GAA': away_gaa,
            # 'Away GAA Color': away_gaa_color,
            'Away Goalie': away_goalie,
            # 'Away GA (Goalie)': away_ga,
            # 'Away GA (Goalie) Color': away_ga_goalie_color,
            'Away NGTP (Goalie)': away_ngtp,
            'Away NGTP (Goalie) Color': away_ngtp_goalie_color,
            'Away YGTP (Goalie)': away_ygtp,
            'Away YGTP (Goalie) Color': away_ygtp_goalie_color,
            'Away NGTP % (Goalie)': away_ngtp_goalie_percent,
            'Away NGTP % (Goalie) Color': away_ngtp_goalie_percent_color,
            'Away Total NGTP (Goalie)': away_total_ngtp,
            'Away Total YGTP (Goalie)': away_total_ygtp,
            'Away Total NGTP % (Goalie)': away_total_ngtp_goalie_percent,
            'Away Total NGTP % (Goalie) Color': away_total_ngtp_goalie_percent_color,
            'Away L5 (Goalie)': away_goalie_l5_games,
            'Away Streak (Goalie)': away_goalie_streak,
            'Away Streak (Goalie) Color': away_goalie_streak_color,

            # 'Home GAA': home_gaa,
            # 'Home GAA Color': home_gaa_color,
            'Home Goalie': home_goalie,
            # 'Home GA (Goalie)': home_ga,
            # 'Home GA (Goalie) Color': home_ga_goalie_color,
            'Home NGTP (Goalie)': home_ngtp,
            'Home NGTP (Goalie) Color': home_ngtp_goalie_color,
            'Home YGTP (Goalie)': home_ygtp,
            'Home YGTP (Goalie) Color': home_ygtp_goalie_color,
            'Home NGTP % (Goalie)': home_ngtp_goalie_percent,
            'Home NGTP % (Goalie) Color': home_ngtp_goalie_percent_color,
            'Home Total NGTP (Goalie)': home_total_ngtp,
            'Home Total YGTP (Goalie)': home_total_ygtp,
            'Home Total NGTP % (Goalie)': home_total_ngtp_goalie_percent,
            'Home Total NGTP % (Goalie) Color': home_total_ngtp_goalie_percent_color,
            'Home L5 (Goalie)': home_goalie_l5_games,
            'Home Streak (Goalie)': home_goalie_streak,
            'Home Streak (Goalie) Color': home_goalie_streak_color,

            'NGTP % (Goalies)': ngtp_pitchegs_percent,
            'NGTP % (Goalies) Color': ngtp_pitchegs_percent_color,

            'Away NGSTP Algo Percentage': away_algo_percentage,
            'Home NGSTP Algo Percentage': home_algo_percentage,
            'Algo Percentage': algo_percentage
        })

    # Get the current date
    current_date = datetime.date.today().strftime("%B %d, %Y")

    return render_template('nhl_display_tp_matchups_data.html', data=updated_data, date=current_date)

if __name__ == '__main__':
    app.run(debug=True)
