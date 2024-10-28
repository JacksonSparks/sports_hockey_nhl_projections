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

def calculate_ngfp_color(value, min_val=0, max_val=100):
    """Calculate color for NGFP percentages based on a fixed scale (0 to 100)."""
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

def calculate_ngsfp_color(value, min_val=50, max_val=100):
    """Calculate color for NGFP percentages based on a fixed scale (0 to 100)."""
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
    team_data_df = pd.read_csv('nhl_fp_team_data.csv')
    goalie_data_df = pd.read_csv('nhl_fp_goalie_data.csv')

    # Calculate min and max values for relevant columns
    team_min_max = {
        'Away GS': calculate_min_max(team_data_df, 'Away GS'),
        'Away NGFP': calculate_min_max(team_data_df, 'Away NGFP'),
        'Away YGFP': calculate_min_max(team_data_df, 'Away YGFP'),

        'Home GS': calculate_min_max(team_data_df, 'Home GS'),
        'Home NGFP': calculate_min_max(team_data_df, 'Home NGFP'),
        'Home YGFP': calculate_min_max(team_data_df, 'Home YGFP')
    }

    goalie_min_max = {
        'Away GAA': calculate_min_max(goalie_data_df, 'Away GAA'),
        'Away GA': calculate_min_max(goalie_data_df, 'Away GA'),
        'Away NGFP': calculate_min_max(goalie_data_df, 'Away NGFP'),
        'Away YGFP': calculate_min_max(goalie_data_df, 'Away YGFP'),
        'Away Total NGFP': calculate_min_max(goalie_data_df, 'Total NGFP'),
        'Away Total YGFP': calculate_min_max(goalie_data_df, 'Total YGFP'),

        'Home GAA': calculate_min_max(goalie_data_df, 'Home GAA'),
        'Home GA': calculate_min_max(goalie_data_df, 'Home GA'),
        'Home NGFP': calculate_min_max(goalie_data_df, 'Home NGFP'),
        'Home YGFP': calculate_min_max(goalie_data_df, 'Home YGFP'),
        'Home Total NGFP': calculate_min_max(goalie_data_df, 'Total NGFP'),
        'Home Total YGFP': calculate_min_max(goalie_data_df, 'Total YGFP')
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
            away_team_ngfp = away_team_data['Away NGFP']
            away_team_ygfp = away_team_data['Away YGFP']
            away_team_ngsfp = away_team_data['Away NGSFP']
            away_team_ygsfp = away_team_data['Away YGSFP']
            away_team_total_ngfp = away_team_data['Total NGFP']
            away_team_total_ygfp = away_team_data['Total YGFP']
            away_team_total_ngsfp = away_team_data['Total NGSFP']
            away_team_total_ygsfp = away_team_data['Total YGSFP']
            away_team_intra_ngsfp = away_team_data['Intra NGSFP']
            away_team_intra_ygsfp = away_team_data['Intra YGSFP']
            away_team_l10_games = away_team_data['L10 Streak']
            away_team_ngsfp_streak = away_team_data['NGSFP Streak']
            away_team_ygsfp_streak = away_team_data['YGSFP Streak']
        else:
            away_team_gs = away_team_ngfp = away_team_ygfp = away_team_ngsfp = away_team_ygsfp = away_team_total_ngfp = away_team_total_ygfp = away_team_total_ngsfp = away_team_total_ygsfp = away_team_intra_ngsfp = away_team_intra_ygsfp = away_team_l10_games = away_team_ngsfp_streak = away_team_ygsfp_streak = 'N/A'

        # Extract the data for the home team from mlb_team_data.csv
        home_team_data = team_data_df[team_data_df['Name'] == home_team]
        if not home_team_data.empty:
            home_team_data = home_team_data.iloc[0]
            home_team_gs = home_team_data['Home GS']
            home_team_ngfp = home_team_data['Home NGFP']
            home_team_ygfp = home_team_data['Home YGFP']
            home_team_ngsfp = home_team_data['Home NGSFP']
            home_team_ygsfp = home_team_data['Home YGSFP']
            home_team_total_ngfp = home_team_data['Total NGFP']
            home_team_total_ygfp = home_team_data['Total YGFP']
            home_team_total_ngsfp = home_team_data['Total NGSFP']
            home_team_total_ygsfp = home_team_data['Total YGSFP']
            home_team_intra_ngsfp = home_team_data['Intra NGSFP']
            home_team_intra_ygsfp = home_team_data['Intra YGSFP']
            home_team_l10_games = home_team_data['L10 Streak']
            home_team_ngsfp_streak = home_team_data['NGSFP Streak']
            home_team_ygsfp_streak = home_team_data['YGSFP Streak']
        else:
            home_team_gs = home_team_ngfp = home_team_ygfp = home_team_ngsfp = home_team_ygsfp = home_team_total_ngfp = home_team_total_ygfp = home_team_total_ngsfp = home_team_total_ygsfp = home_team_intra_ngsfp = home_team_intra_ygsfp = home_team_l10_games = home_team_ngsfp_streak = home_team_ygsfp_streak = 'N/A'

        # Format goalie names for matching
        formatted_away_goalie = format_goalie_name(away_goalie)
        formatted_home_goalie = format_goalie_name(home_goalie)

        # Extract the data for the away goalie from mlb_goalie_data.csv
        away_goalie_data = goalie_data_df[goalie_data_df['Name'] == formatted_away_goalie]
        if not away_goalie_data.empty:
            away_goalie_data = away_goalie_data.iloc[0]
            away_gaa = away_goalie_data['Away GAA']
            away_ga = away_goalie_data['Away GA']
            away_ngfp = away_goalie_data['Away NGFP']
            away_ygfp = away_goalie_data['Away YGFP']
            away_total_ngfp = away_goalie_data['Total NGFP']
            away_total_ygfp = away_goalie_data['Total YGFP']
            away_goalie_l5_games = away_goalie_data['L5 Streak']
            away_goalie_ngfp_streak = away_goalie_data['NGFP Streak']
            away_goalie_ygfp_streak = away_goalie_data['YGFP Streak']
        else:
            away_gaa = away_ga = away_ngfp = away_ygfp = away_total_ngfp = away_total_ygfp = away_goalie_l5_games = away_goalie_ngfp_streak = away_goalie_ygfp_streak = 'N/A'

        # Extract the data for the home goalie from mlb_goalie_data.csv
        home_goalie_data = goalie_data_df[goalie_data_df['Name'] == formatted_home_goalie]
        if not home_goalie_data.empty:
            home_goalie_data = home_goalie_data.iloc[0]
            home_gaa = home_goalie_data['Home GAA']
            home_ga = home_goalie_data['Home GA']
            home_ngfp = home_goalie_data['Home NGFP']
            home_ygfp = home_goalie_data['Home YGFP']
            home_total_ngfp = home_goalie_data['Total NGFP']
            home_total_ygfp = home_goalie_data['Total YGFP']
            home_goalie_l5_games = home_goalie_data['L5 Streak']
            home_goalie_ngfp_streak = home_goalie_data['NGFP Streak']
            home_goalie_ygfp_streak = home_goalie_data['YGFP Streak']
        else:
            home_gaa = home_ga = home_ngfp = home_ygfp = home_total_ngfp = home_total_ygfp = home_goalie_l5_games = home_goalie_ngfp_streak = home_goalie_ygfp_streak = 'N/A'

        # Calculate cologs
        away_gs_color = calculate_color(away_team_gs, team_min_max['Away GS'][0], team_min_max['Away GS'][1])

        home_gs_color = calculate_color(home_team_gs, team_min_max['Home GS'][0], team_min_max['Home GS'][1])

        away_ga_goalie_color = calculate_color(away_ga, goalie_min_max['Away GA'][0], goalie_min_max['Away GA'][1])
        away_ngfp_goalie_color = calculate_color(away_ngfp, goalie_min_max['Away NGFP'][0], goalie_min_max['Away NGFP'][1], inverse=True)
        away_ygfp_goalie_color = calculate_color(away_ygfp, goalie_min_max['Away YGFP'][0], goalie_min_max['Away YGFP'][1])
        home_ga_goalie_color = calculate_color(home_ga, goalie_min_max['Home GA'][0], goalie_min_max['Home GA'][1])
        home_ngfp_goalie_color = calculate_color(home_ngfp, goalie_min_max['Home NGFP'][0], goalie_min_max['Home NGFP'][1], inverse=True)
        home_ygfp_goalie_color = calculate_color(home_ygfp, goalie_min_max['Home YGFP'][0], goalie_min_max['Home YGFP'][1])

        # Function to safely calculate percentages
        def safe_percentage(numerator, denominator):
            if isinstance(numerator, str) and numerator == 'N/A':
                return 'N/A'
            if isinstance(denominator, str) and denominator == 'N/A':
                return 'N/A'
            if np.isnan(numerator) or np.isnan(denominator) or denominator == 0:
                return 'N/A'

            return round((numerator / denominator) * 100)

        # Calculate NGFP percentages
        away_ngfp_percent = safe_percentage(away_team_ngfp, away_team_ngfp + away_team_ygfp)
        home_ngfp_percent = safe_percentage(home_team_ngfp, home_team_ngfp + home_team_ygfp)
        away_ngsfp_percent = safe_percentage(away_team_ngsfp, away_team_ngsfp + away_team_ygsfp)
        home_ngsfp_percent = safe_percentage(home_team_ngsfp, home_team_ngsfp + home_team_ygsfp)
        away_total_ngfp_percent = safe_percentage(away_team_total_ngfp, away_team_total_ngfp + away_team_total_ygfp)
        home_total_ngfp_percent = safe_percentage(home_team_total_ngfp, home_team_total_ngfp + home_team_total_ygfp)
        away_total_ngsfp_percent = safe_percentage(away_team_total_ngsfp, away_team_total_ngsfp + away_team_total_ygsfp)
        home_total_ngsfp_percent = safe_percentage(home_team_total_ngsfp, home_team_total_ngsfp + home_team_total_ygsfp)

        team_to_division = {}
        for division, teams in divisions.items():
            for team in teams:
                team_to_division[team] = division

        if (team_to_division[away_team] == team_to_division[home_team]):
            intradivision_game = True
        else:
            intradivision_game = False

        if intradivision_game == True:
            if away_team_intra_ngsfp > 0:
                away_intra_ngsfp_percent = round((away_team_intra_ngsfp / (away_team_intra_ngsfp + away_team_intra_ygsfp)) * 100)
                home_intra_ngsfp_percent = round((home_team_intra_ngsfp / (home_team_intra_ngsfp + home_team_intra_ygsfp)) * 100)
            else:
                away_intra_ngsfp_percent = 'N/A'
                home_intra_ngsfp_percent = 'N/A'
        else:
            away_intra_ngsfp_percent = 'N/A'
            home_intra_ngsfp_percent = 'N/A'



        away_ngfp_goalie_percent = round((away_ngfp / (away_ngfp + away_ygfp)) * 100, 1) if (away_ngfp != 'N/A' and away_ygfp != 'N/A') else 'N/A'
        home_ngfp_goalie_percent = round((home_ngfp / (home_ngfp + home_ygfp)) * 100, 1) if (home_ngfp != 'N/A' and home_ygfp != 'N/A') else 'N/A'
        away_total_ngfp_goalie_percent = round((away_total_ngfp / (away_total_ngfp + away_total_ygfp)) * 100, 1) if (away_total_ngfp != 'N/A' and away_total_ygfp != 'N/A') else 'N/A'
        home_total_ngfp_goalie_percent = round((home_total_ngfp / (home_total_ngfp + home_total_ygfp)) * 100, 1) if (home_total_ngfp != 'N/A' and home_total_ygfp != 'N/A') else 'N/A'
        ngfp_pitchegs_percent = round(home_ngfp_goalie_percent * away_ngfp_goalie_percent / 100) if (home_ngfp_goalie_percent != 'N/A' and not pd.isna(home_ngfp_goalie_percent) and away_ngfp_goalie_percent != 'N/A' and not pd.isna(away_ngfp_goalie_percent)) else 'N/A'



        # Calculate cologs based on NGFP percentages
        away_ngfp_percent_color = calculate_ngfp_color(away_ngfp_percent)
        home_ngfp_percent_color = calculate_ngfp_color(home_ngfp_percent)
        away_ngsfp_percent_color = calculate_ngsfp_color(away_ngsfp_percent)
        home_ngsfp_percent_color = calculate_ngsfp_color(home_ngsfp_percent)
        away_total_ngfp_percent_color = calculate_ngfp_color(away_total_ngfp_percent)
        home_total_ngfp_percent_color = calculate_ngfp_color(home_total_ngfp_percent)
        away_total_ngsfp_percent_color = calculate_ngsfp_color(away_total_ngsfp_percent)
        home_total_ngsfp_percent_color = calculate_ngsfp_color(home_total_ngsfp_percent)
        away_intra_ngsfp_percent_color = calculate_ngsfp_color(away_intra_ngsfp_percent)
        home_intra_ngsfp_percent_color = calculate_ngsfp_color(home_intra_ngsfp_percent)


        away_ngfp_goalie_percent_color = calculate_ngfp_color(away_ngfp_goalie_percent)
        home_ngfp_goalie_percent_color = calculate_ngfp_color(home_ngfp_goalie_percent)
        away_total_ngfp_goalie_percent_color = calculate_ngfp_color(away_total_ngfp_goalie_percent)
        home_total_ngfp_goalie_percent_color = calculate_ngfp_color(home_total_ngfp_goalie_percent)
        ngfp_pitchegs_percent_color = calculate_ngfp_color(ngfp_pitchegs_percent)

        # Calculate cologs based on GAA
        away_gaa_color = calculate_era_color(away_gaa)
        home_gaa_color = calculate_era_color(home_gaa)

        if home_team_ngsfp_streak > 0:
            home_streak = home_team_ngsfp_streak
        else:
            home_streak = home_team_ygsfp_streak

        if away_team_ngsfp_streak > 0:
            away_streak = away_team_ngsfp_streak
        else:
            away_streak = away_team_ygsfp_streak

        home_streak_color = calculate_streak_color(home_team_ngsfp_streak)
        away_streak_color = calculate_streak_color(away_team_ngsfp_streak)

        if home_goalie_ngfp_streak != 'N/A' and home_goalie_ngfp_streak > 0:
            home_goalie_streak = home_goalie_ngfp_streak
        elif home_goalie_ygfp_streak != 'N/A':
            home_goalie_streak = home_goalie_ygfp_streak
        else:
            home_goalie_streak = 'N/A'

        if away_goalie_ngfp_streak != 'N/A' and away_goalie_ngfp_streak > 0:
            away_goalie_streak = away_goalie_ngfp_streak
        elif away_goalie_ygfp_streak != 'N/A':
            away_goalie_streak = away_goalie_ygfp_streak
        else:
            away_goalie_streak = 'N/A'

        if home_goalie_streak != 'N/A':
            home_goalie_streak_color = calculate_streak_color(home_goalie_ngfp_streak)
        else:
            home_goalie_streak_color = 'N/A'

        if away_goalie_streak != 'N/A':
            away_goalie_streak_color = calculate_streak_color(away_goalie_ngfp_streak)
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

        if away_ngfp_goalie_percent != 'N/A':
            away_ngfp_goalie_percent = safe_float(away_ngfp_goalie_percent)
            away_total_ngfp_goalie_percent = safe_float(away_total_ngfp_goalie_percent)
            if (away_ngfp+away_ygfp) >= 2 and (away_total_ngfp+away_total_ygfp) >= 5:
                if away_goalie_ngfp_streak > 0:
                    algo_away_goalie = ((away_ngfp_goalie_percent * 2) + away_total_ngfp_goalie_percent) / 3 + (3 * (away_goalie_l5_games - 2)) + (2 * (away_goalie_ngfp_streak))
                elif away_goalie_ygfp_streak > 0:
                    algo_away_goalie = ((away_ngfp_goalie_percent * 2) + away_total_ngfp_goalie_percent) / 3 + (3 * (away_goalie_l5_games - 2)) - (2 * (away_goalie_ygfp_streak))

        if home_ngfp_goalie_percent != 'N/A':
            home_ngfp_goalie_percent = safe_float(home_ngfp_goalie_percent)
            home_total_ngfp_goalie_percent = safe_float(home_total_ngfp_goalie_percent)
            if (home_ngfp+home_ygfp) >= 2 and (home_total_ngfp+home_total_ygfp) >= 5:
                if home_goalie_ngfp_streak > 0:
                    algo_home_goalie = ((home_ngfp_goalie_percent * 2) + home_total_ngfp_goalie_percent) / 3 + (3 * (home_goalie_l5_games - 2)) + (2 * (home_goalie_ngfp_streak))
                elif home_goalie_ygfp_streak > 0:
                    algo_home_goalie = ((home_ngfp_goalie_percent * 2) + home_total_ngfp_goalie_percent) / 3 + (3 * (home_goalie_l5_games - 2)) - (2 * (home_goalie_ygfp_streak))

        # Convert all necessary variables to floats
        away_ngsfp_percent = safe_float(away_ngsfp_percent)
        away_intra_ngsfp_percent = safe_float(away_intra_ngsfp_percent)
        home_ngsfp_percent = safe_float(home_ngsfp_percent)
        home_intra_ngsfp_percent = safe_float(home_intra_ngsfp_percent)

        if away_team_ngsfp_streak > 0:
            if not math.isnan(away_intra_ngsfp_percent):
                #algo_away_team = ((away_ngsfp_percent) / 2 + away_intra_ngsfp_percent) / 2 + (2 * (away_team_l10_games - 7)) + (1 / 2 * (away_team_ngsfp_streak))
                algo_away_team = (((away_ngsfp_percent * 5) + (away_intra_ngsfp_percent * 3) + ((away_team_l10_games / 10) * 3)) / 12) + (2 * (away_team_ngsfp_streak))
            else:
                #algo_away_team = ((away_ngsfp_percent) ) + (2 * (away_team_l10_games - 7)) + (1 / 2 * (away_team_ngsfp_streak))
                algo_away_team = (((away_ngsfp_percent * 7) + ((away_team_l10_games / 10) * 5)) / 12) + (2 * (away_team_ngsfp_streak))
        elif away_team_ygsfp_streak > 0:
            if not math.isnan(away_intra_ngsfp_percent):
                #algo_away_team = ((away_ngsfp_percent) / 2 + away_intra_ngsfp_percent) / 2 + (2 * (away_team_l10_games - 7)) - (1 / 2 * (away_team_ygsfp_streak))
                algo_away_team = (((away_ngsfp_percent * 5) + (away_intra_ngsfp_percent * 3) + ((away_team_l10_games / 10) * 3)) / 12) - (2 * (away_team_ygsfp_streak))
            else:
                #algo_away_team = ((away_ngsfp_percent) / 2) + (2 * (away_team_l10_games - 7)) - (1 / 2 * (away_team_ygsfp_streak))
                algo_away_team = (((away_ngsfp_percent * 7) + ((away_team_l10_games / 10) * 5)) / 12) - (2 * (away_team_ygsfp_streak))

        if home_team_ngsfp_streak > 0:
            if not math.isnan(home_intra_ngsfp_percent):
                #algo_home_team = ((home_ngsfp_percent) / 2 + home_intra_ngsfp_percent) / 2 + (2 * (home_team_l10_games - 7)) + (1 / 2 * (home_team_ngsfp_streak))
                algo_home_team = (((home_ngsfp_percent * 5) + (home_intra_ngsfp_percent * 3) + ((home_team_l10_games / 10) * 3)) / 12) + (2 * (home_team_ngsfp_streak))
            else:
                #algo_home_team = ((home_ngsfp_percent) ) + (2 * (home_team_l10_games - 7)) + (1 / 2 * (home_team_ngsfp_streak))
                algo_home_team = (((home_ngsfp_percent * 7) + ((home_team_l10_games / 10) * 5)) / 12) + (2 * (home_team_ngsfp_streak))
        elif home_team_ygsfp_streak > 0:
            if not math.isnan(home_intra_ngsfp_percent):
                #algo_home_team = ((home_ngsfp_percent) / 2 + home_intra_ngsfp_percent) / 2 + (2 * (home_team_l10_games - 7)) - (1 / 2 * (home_team_ygsfp_streak))
                algo_home_team = (((home_ngsfp_percent * 5) + (home_intra_ngsfp_percent * 3) + ((home_team_l10_games / 10) * 3)) / 12) - (2 * (home_team_ygsfp_streak))
            else:
                #algo_home_team = ((home_ngsfp_percent) / 2) + (2 * (home_team_l10_games - 7)) - (1 / 2 * (home_team_ygsfp_streak))
                algo_home_team = (((home_ngsfp_percent * 7) + ((home_team_l10_games / 10) * 5)) / 12) - (2 * (home_team_ygsfp_streak))



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
            'Away NGFP %': away_ngfp_percent,
            'Away NGFP % Color': away_ngfp_percent_color,
            'Away NGSFP %': away_ngsfp_percent,
            'Away NGSFP % Color': away_ngsfp_percent_color,
            'Away Total NGFP %': away_total_ngfp_percent,
            'Away Total NGFP % Color': away_total_ngfp_percent_color,
            'Away Total NGSFP %': away_total_ngsfp_percent,
            'Away Total NGSFP % Color': away_total_ngsfp_percent_color,
            'Away Intra NGSFP %': away_intra_ngsfp_percent,
            'Away Intra NGSFP % Color': away_intra_ngsfp_percent_color,

            'Away L10': away_team_l10_games,
            'Away Streak': away_streak,
            'Away Streak Color': away_streak_color,

            'Home Team': home_team,
            'Home GS': home_team_gs,
            'Home GS Color': home_gs_color,
            'Home NGFP %': home_ngfp_percent,
            'Home NGFP % Color': home_ngfp_percent_color,
            'Home NGSFP %': home_ngsfp_percent,
            'Home NGSFP % Color': home_ngsfp_percent_color,
            'Home Total NGFP %': home_total_ngfp_percent,
            'Home Total NGFP % Color': home_total_ngfp_percent_color,
            'Home Total NGSFP %': home_total_ngsfp_percent,
            'Home Total NGSFP % Color': home_total_ngsfp_percent_color,
            'Home Intra NGSFP %': home_intra_ngsfp_percent,
            'Home Intra NGSFP % Color': home_intra_ngsfp_percent_color,

            'Home L10': home_team_l10_games,
            'Home Streak': home_streak,
            'Home Streak Color': home_streak_color,

            # 'Away GAA': away_gaa,
            # 'Away GAA Color': away_gaa_color,
            'Away Goalie': away_goalie,
            # 'Away GA (Goalie)': away_ga,
            # 'Away GA (Goalie) Color': away_ga_goalie_color,
            'Away NGFP (Goalie)': away_ngfp,
            'Away NGFP (Goalie) Color': away_ngfp_goalie_color,
            'Away YGFP (Goalie)': away_ygfp,
            'Away YGFP (Goalie) Color': away_ygfp_goalie_color,
            'Away NGFP % (Goalie)': away_ngfp_goalie_percent,
            'Away NGFP % (Goalie) Color': away_ngfp_goalie_percent_color,
            'Away Total NGFP (Goalie)': away_total_ngfp,
            'Away Total YGFP (Goalie)': away_total_ygfp,
            'Away Total NGFP % (Goalie)': away_total_ngfp_goalie_percent,
            'Away Total NGFP % (Goalie) Color': away_total_ngfp_goalie_percent_color,
            'Away L5 (Goalie)': away_goalie_l5_games,
            'Away Streak (Goalie)': away_goalie_streak,
            'Away Streak (Goalie) Color': away_goalie_streak_color,

            # 'Home GAA': home_gaa,
            # 'Home GAA Color': home_gaa_color,
            'Home Goalie': home_goalie,
            # 'Home GA (Goalie)': home_ga,
            # 'Home GA (Goalie) Color': home_ga_goalie_color,
            'Home NGFP (Goalie)': home_ngfp,
            'Home NGFP (Goalie) Color': home_ngfp_goalie_color,
            'Home YGFP (Goalie)': home_ygfp,
            'Home YGFP (Goalie) Color': home_ygfp_goalie_color,
            'Home NGFP % (Goalie)': home_ngfp_goalie_percent,
            'Home NGFP % (Goalie) Color': home_ngfp_goalie_percent_color,
            'Home Total NGFP (Goalie)': home_total_ngfp,
            'Home Total YGFP (Goalie)': home_total_ygfp,
            'Home Total NGFP % (Goalie)': home_total_ngfp_goalie_percent,
            'Home Total NGFP % (Goalie) Color': home_total_ngfp_goalie_percent_color,
            'Home L5 (Goalie)': home_goalie_l5_games,
            'Home Streak (Goalie)': home_goalie_streak,
            'Home Streak (Goalie) Color': home_goalie_streak_color,

            'NGFP % (Goalies)': ngfp_pitchegs_percent,
            'NGFP % (Goalies) Color': ngfp_pitchegs_percent_color,

            'Away NGSFP Algo Percentage': away_algo_percentage,
            'Home NGSFP Algo Percentage': home_algo_percentage,
            'Algo Percentage': algo_percentage
        })

    # Get the current date
    current_date = datetime.date.today().strftime("%B %d, %Y")

    return render_template('nhl_display_fp_matchups_data.html', data=updated_data, date=current_date)

if __name__ == '__main__':
    app.run(debug=True)
