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

def calculate_ngsp_color(value, min_val=0, max_val=100):
    """Calculate color for NGSP percentages based on a fixed scale (0 to 100)."""
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

def calculate_ngssp_color(value, min_val=50, max_val=100):
    """Calculate color for NGSP percentages based on a fixed scale (0 to 100)."""
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
    team_data_df = pd.read_csv('nhl_sp_team_data.csv')
    goalie_data_df = pd.read_csv('nhl_sp_goalie_data.csv')

    # Calculate min and max values for relevant columns
    team_min_max = {
        'Away GS': calculate_min_max(team_data_df, 'Away GS'),
        'Away NGSP': calculate_min_max(team_data_df, 'Away NGSP'),
        'Away YGSP': calculate_min_max(team_data_df, 'Away YGSP'),

        'Home GS': calculate_min_max(team_data_df, 'Home GS'),
        'Home NGSP': calculate_min_max(team_data_df, 'Home NGSP'),
        'Home YGSP': calculate_min_max(team_data_df, 'Home YGSP')
    }

    goalie_min_max = {
        'Away GAA': calculate_min_max(goalie_data_df, 'Away GAA'),
        'Away GA': calculate_min_max(goalie_data_df, 'Away GA'),
        'Away NGSP': calculate_min_max(goalie_data_df, 'Away NGSP'),
        'Away YGSP': calculate_min_max(goalie_data_df, 'Away YGSP'),
        'Away Total NGSP': calculate_min_max(goalie_data_df, 'Total NGSP'),
        'Away Total YGSP': calculate_min_max(goalie_data_df, 'Total YGSP'),

        'Home GAA': calculate_min_max(goalie_data_df, 'Home GAA'),
        'Home GA': calculate_min_max(goalie_data_df, 'Home GA'),
        'Home NGSP': calculate_min_max(goalie_data_df, 'Home NGSP'),
        'Home YGSP': calculate_min_max(goalie_data_df, 'Home YGSP'),
        'Home Total NGSP': calculate_min_max(goalie_data_df, 'Total NGSP'),
        'Home Total YGSP': calculate_min_max(goalie_data_df, 'Total YGSP')
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
            away_team_ngsp = away_team_data['Away NGSP']
            away_team_ygsp = away_team_data['Away YGSP']
            away_team_ngssp = away_team_data['Away NGSSP']
            away_team_ygssp = away_team_data['Away YGSSP']
            away_team_total_ngsp = away_team_data['Total NGSP']
            away_team_total_ygsp = away_team_data['Total YGSP']
            away_team_total_ngssp = away_team_data['Total NGSSP']
            away_team_total_ygssp = away_team_data['Total YGSSP']
            away_team_intra_ngssp = away_team_data['Intra NGSSP']
            away_team_intra_ygssp = away_team_data['Intra YGSSP']
            away_team_l10_games = away_team_data['L10 Streak']
            away_team_ngssp_streak = away_team_data['NGSSP Streak']
            away_team_ygssp_streak = away_team_data['YGSSP Streak']
        else:
            away_team_gs = away_team_ngsp = away_team_ygsp = away_team_ngssp = away_team_ygssp = away_team_total_ngsp = away_team_total_ygsp = away_team_total_ngssp = away_team_total_ygssp = away_team_intra_ngssp = away_team_intra_ygssp = away_team_l10_games = away_team_ngssp_streak = away_team_ygssp_streak = 'N/A'

        # Extract the data for the home team from mlb_team_data.csv
        home_team_data = team_data_df[team_data_df['Name'] == home_team]
        if not home_team_data.empty:
            home_team_data = home_team_data.iloc[0]
            home_team_gs = home_team_data['Home GS']
            home_team_ngsp = home_team_data['Home NGSP']
            home_team_ygsp = home_team_data['Home YGSP']
            home_team_ngssp = home_team_data['Home NGSSP']
            home_team_ygssp = home_team_data['Home YGSSP']
            home_team_total_ngsp = home_team_data['Total NGSP']
            home_team_total_ygsp = home_team_data['Total YGSP']
            home_team_total_ngssp = home_team_data['Total NGSSP']
            home_team_total_ygssp = home_team_data['Total YGSSP']
            home_team_intra_ngssp = home_team_data['Intra NGSSP']
            home_team_intra_ygssp = home_team_data['Intra YGSSP']
            home_team_l10_games = home_team_data['L10 Streak']
            home_team_ngssp_streak = home_team_data['NGSSP Streak']
            home_team_ygssp_streak = home_team_data['YGSSP Streak']
        else:
            home_team_gs = home_team_ngsp = home_team_ygsp = home_team_ngssp = home_team_ygssp = home_team_total_ngsp = home_team_total_ygsp = home_team_total_ngssp = home_team_total_ygssp = home_team_intra_ngssp = home_team_intra_ygssp = home_team_l10_games = home_team_ngssp_streak = home_team_ygssp_streak = 'N/A'

        # Format goalie names for matching
        formatted_away_goalie = format_goalie_name(away_goalie)
        formatted_home_goalie = format_goalie_name(home_goalie)

        # Extract the data for the away goalie from mlb_goalie_data.csv
        away_goalie_data = goalie_data_df[goalie_data_df['Name'] == formatted_away_goalie]
        if not away_goalie_data.empty:
            away_goalie_data = away_goalie_data.iloc[0]
            away_gaa = away_goalie_data['Away GAA']
            away_ga = away_goalie_data['Away GA']
            away_ngsp = away_goalie_data['Away NGSP']
            away_ygsp = away_goalie_data['Away YGSP']
            away_total_ngsp = away_goalie_data['Total NGSP']
            away_total_ygsp = away_goalie_data['Total YGSP']
            away_goalie_l5_games = away_goalie_data['L5 Streak']
            away_goalie_ngsp_streak = away_goalie_data['NGSP Streak']
            away_goalie_ygsp_streak = away_goalie_data['YGSP Streak']
        else:
            away_gaa = away_ga = away_ngsp = away_ygsp = away_total_ngsp = away_total_ygsp = away_goalie_l5_games = away_goalie_ngsp_streak = away_goalie_ygsp_streak = 'N/A'

        # Extract the data for the home goalie from mlb_goalie_data.csv
        home_goalie_data = goalie_data_df[goalie_data_df['Name'] == formatted_home_goalie]
        if not home_goalie_data.empty:
            home_goalie_data = home_goalie_data.iloc[0]
            home_gaa = home_goalie_data['Home GAA']
            home_ga = home_goalie_data['Home GA']
            home_ngsp = home_goalie_data['Home NGSP']
            home_ygsp = home_goalie_data['Home YGSP']
            home_total_ngsp = home_goalie_data['Total NGSP']
            home_total_ygsp = home_goalie_data['Total YGSP']
            home_goalie_l5_games = home_goalie_data['L5 Streak']
            home_goalie_ngsp_streak = home_goalie_data['NGSP Streak']
            home_goalie_ygsp_streak = home_goalie_data['YGSP Streak']
        else:
            home_gaa = home_ga = home_ngsp = home_ygsp = home_total_ngsp = home_total_ygsp = home_goalie_l5_games = home_goalie_ngsp_streak = home_goalie_ygsp_streak = 'N/A'

        # Calculate cologs
        away_gs_color = calculate_color(away_team_gs, team_min_max['Away GS'][0], team_min_max['Away GS'][1])

        home_gs_color = calculate_color(home_team_gs, team_min_max['Home GS'][0], team_min_max['Home GS'][1])

        away_ga_goalie_color = calculate_color(away_ga, goalie_min_max['Away GA'][0], goalie_min_max['Away GA'][1])
        away_ngsp_goalie_color = calculate_color(away_ngsp, goalie_min_max['Away NGSP'][0], goalie_min_max['Away NGSP'][1], inverse=True)
        away_ygsp_goalie_color = calculate_color(away_ygsp, goalie_min_max['Away YGSP'][0], goalie_min_max['Away YGSP'][1])
        home_ga_goalie_color = calculate_color(home_ga, goalie_min_max['Home GA'][0], goalie_min_max['Home GA'][1])
        home_ngsp_goalie_color = calculate_color(home_ngsp, goalie_min_max['Home NGSP'][0], goalie_min_max['Home NGSP'][1], inverse=True)
        home_ygsp_goalie_color = calculate_color(home_ygsp, goalie_min_max['Home YGSP'][0], goalie_min_max['Home YGSP'][1])

        # Function to safely calculate percentages
        def safe_percentage(numerator, denominator):
            if isinstance(numerator, str) and numerator == 'N/A':
                return 'N/A'
            if isinstance(denominator, str) and denominator == 'N/A':
                return 'N/A'
            if np.isnan(numerator) or np.isnan(denominator) or denominator == 0:
                return 'N/A'

            return round((numerator / denominator) * 100)

        # Calculate NGSP percentages
        away_ngsp_percent = safe_percentage(away_team_ngsp, away_team_ngsp + away_team_ygsp)
        home_ngsp_percent = safe_percentage(home_team_ngsp, home_team_ngsp + home_team_ygsp)
        away_ngssp_percent = safe_percentage(away_team_ngssp, away_team_ngssp + away_team_ygssp)
        home_ngssp_percent = safe_percentage(home_team_ngssp, home_team_ngssp + home_team_ygssp)
        away_total_ngsp_percent = safe_percentage(away_team_total_ngsp, away_team_total_ngsp + away_team_total_ygsp)
        home_total_ngsp_percent = safe_percentage(home_team_total_ngsp, home_team_total_ngsp + home_team_total_ygsp)
        away_total_ngssp_percent = safe_percentage(away_team_total_ngssp, away_team_total_ngssp + away_team_total_ygssp)
        home_total_ngssp_percent = safe_percentage(home_team_total_ngssp, home_team_total_ngssp + home_team_total_ygssp)

        team_to_division = {}
        for division, teams in divisions.items():
            for team in teams:
                team_to_division[team] = division

        if (team_to_division[away_team] == team_to_division[home_team]):
            intradivision_game = True
        else:
            intradivision_game = False

        if intradivision_game == True:
            if away_team_intra_ngssp > 0:
                away_intra_ngssp_percent = round((away_team_intra_ngssp / (away_team_intra_ngssp + away_team_intra_ygssp)) * 100)
                home_intra_ngssp_percent = round((home_team_intra_ngssp / (home_team_intra_ngssp + home_team_intra_ygssp)) * 100)
            else:
                away_intra_ngssp_percent = 'N/A'
                home_intra_ngssp_percent = 'N/A'
        else:
            away_intra_ngssp_percent = 'N/A'
            home_intra_ngssp_percent = 'N/A'



        away_ngsp_goalie_percent = round((away_ngsp / (away_ngsp + away_ygsp)) * 100, 1) if (away_ngsp != 'N/A' and away_ygsp != 'N/A') else 'N/A'
        home_ngsp_goalie_percent = round((home_ngsp / (home_ngsp + home_ygsp)) * 100, 1) if (home_ngsp != 'N/A' and home_ygsp != 'N/A') else 'N/A'
        away_total_ngsp_goalie_percent = round((away_total_ngsp / (away_total_ngsp + away_total_ygsp)) * 100, 1) if (away_total_ngsp != 'N/A' and away_total_ygsp != 'N/A') else 'N/A'
        home_total_ngsp_goalie_percent = round((home_total_ngsp / (home_total_ngsp + home_total_ygsp)) * 100, 1) if (home_total_ngsp != 'N/A' and home_total_ygsp != 'N/A') else 'N/A'
        ngsp_pitchegs_percent = round(home_ngsp_goalie_percent * away_ngsp_goalie_percent / 100) if (home_ngsp_goalie_percent != 'N/A' and not pd.isna(home_ngsp_goalie_percent) and away_ngsp_goalie_percent != 'N/A' and not pd.isna(away_ngsp_goalie_percent)) else 'N/A'



        # Calculate cologs based on NGSP percentages
        away_ngsp_percent_color = calculate_ngsp_color(away_ngsp_percent)
        home_ngsp_percent_color = calculate_ngsp_color(home_ngsp_percent)
        away_ngssp_percent_color = calculate_ngssp_color(away_ngssp_percent)
        home_ngssp_percent_color = calculate_ngssp_color(home_ngssp_percent)
        away_total_ngsp_percent_color = calculate_ngsp_color(away_total_ngsp_percent)
        home_total_ngsp_percent_color = calculate_ngsp_color(home_total_ngsp_percent)
        away_total_ngssp_percent_color = calculate_ngssp_color(away_total_ngssp_percent)
        home_total_ngssp_percent_color = calculate_ngssp_color(home_total_ngssp_percent)
        away_intra_ngssp_percent_color = calculate_ngssp_color(away_intra_ngssp_percent)
        home_intra_ngssp_percent_color = calculate_ngssp_color(home_intra_ngssp_percent)


        away_ngsp_goalie_percent_color = calculate_ngsp_color(away_ngsp_goalie_percent)
        home_ngsp_goalie_percent_color = calculate_ngsp_color(home_ngsp_goalie_percent)
        away_total_ngsp_goalie_percent_color = calculate_ngsp_color(away_total_ngsp_goalie_percent)
        home_total_ngsp_goalie_percent_color = calculate_ngsp_color(home_total_ngsp_goalie_percent)
        ngsp_pitchegs_percent_color = calculate_ngsp_color(ngsp_pitchegs_percent)

        # Calculate cologs based on GAA
        away_gaa_color = calculate_era_color(away_gaa)
        home_gaa_color = calculate_era_color(home_gaa)

        if home_team_ngssp_streak > 0:
            home_streak = home_team_ngssp_streak
        else:
            home_streak = home_team_ygssp_streak

        if away_team_ngssp_streak > 0:
            away_streak = away_team_ngssp_streak
        else:
            away_streak = away_team_ygssp_streak

        home_streak_color = calculate_streak_color(home_team_ngssp_streak)
        away_streak_color = calculate_streak_color(away_team_ngssp_streak)

        if home_goalie_ngsp_streak != 'N/A' and home_goalie_ngsp_streak > 0:
            home_goalie_streak = home_goalie_ngsp_streak
        elif home_goalie_ygsp_streak != 'N/A':
            home_goalie_streak = home_goalie_ygsp_streak
        else:
            home_goalie_streak = 'N/A'

        if away_goalie_ngsp_streak != 'N/A' and away_goalie_ngsp_streak > 0:
            away_goalie_streak = away_goalie_ngsp_streak
        elif away_goalie_ygsp_streak != 'N/A':
            away_goalie_streak = away_goalie_ygsp_streak
        else:
            away_goalie_streak = 'N/A'

        if home_goalie_streak != 'N/A':
            home_goalie_streak_color = calculate_streak_color(home_goalie_ngsp_streak)
        else:
            home_goalie_streak_color = 'N/A'

        if away_goalie_streak != 'N/A':
            away_goalie_streak_color = calculate_streak_color(away_goalie_ngsp_streak)
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

        if away_ngsp_goalie_percent != 'N/A':
            away_ngsp_goalie_percent = safe_float(away_ngsp_goalie_percent)
            away_total_ngsp_goalie_percent = safe_float(away_total_ngsp_goalie_percent)
            if (away_ngsp+away_ygsp) >= 2 and (away_total_ngsp+away_total_ygsp) >= 5:
                if away_goalie_ngsp_streak > 0:
                    algo_away_goalie = ((away_ngsp_goalie_percent * 2) + away_total_ngsp_goalie_percent) / 3 + (3 * (away_goalie_l5_games - 2)) + (2 * (away_goalie_ngsp_streak))
                elif away_goalie_ygsp_streak > 0:
                    algo_away_goalie = ((away_ngsp_goalie_percent * 2) + away_total_ngsp_goalie_percent) / 3 + (3 * (away_goalie_l5_games - 2)) - (2 * (away_goalie_ygsp_streak))

        if home_ngsp_goalie_percent != 'N/A':
            home_ngsp_goalie_percent = safe_float(home_ngsp_goalie_percent)
            home_total_ngsp_goalie_percent = safe_float(home_total_ngsp_goalie_percent)
            if (home_ngsp+home_ygsp) >= 2 and (home_total_ngsp+home_total_ygsp) >= 5:
                if home_goalie_ngsp_streak > 0:
                    algo_home_goalie = ((home_ngsp_goalie_percent * 2) + home_total_ngsp_goalie_percent) / 3 + (3 * (home_goalie_l5_games - 2)) + (2 * (home_goalie_ngsp_streak))
                elif home_goalie_ygsp_streak > 0:
                    algo_home_goalie = ((home_ngsp_goalie_percent * 2) + home_total_ngsp_goalie_percent) / 3 + (3 * (home_goalie_l5_games - 2)) - (2 * (home_goalie_ygsp_streak))

        # Convert all necessary variables to floats
        away_ngssp_percent = safe_float(away_ngssp_percent)
        away_intra_ngssp_percent = safe_float(away_intra_ngssp_percent)
        home_ngssp_percent = safe_float(home_ngssp_percent)
        home_intra_ngssp_percent = safe_float(home_intra_ngssp_percent)

        if away_team_ngssp_streak > 0:
            if not math.isnan(away_intra_ngssp_percent):
                #algo_away_team = ((away_ngssp_percent) / 2 + away_intra_ngssp_percent) / 2 + (2 * (away_team_l10_games - 7)) + (1 / 2 * (away_team_ngssp_streak))
                algo_away_team = (((away_ngssp_percent * 5) + (away_intra_ngssp_percent * 3) + ((away_team_l10_games / 10) * 3)) / 12) + (2 * (away_team_ngssp_streak))
            else:
                #algo_away_team = ((away_ngssp_percent) ) + (2 * (away_team_l10_games - 7)) + (1 / 2 * (away_team_ngssp_streak))
                algo_away_team = (((away_ngssp_percent * 7) + ((away_team_l10_games / 10) * 5)) / 12) + (2 * (away_team_ngssp_streak))
        elif away_team_ygssp_streak > 0:
            if not math.isnan(away_intra_ngssp_percent):
                #algo_away_team = ((away_ngssp_percent) / 2 + away_intra_ngssp_percent) / 2 + (2 * (away_team_l10_games - 7)) - (1 / 2 * (away_team_ygssp_streak))
                algo_away_team = (((away_ngssp_percent * 5) + (away_intra_ngssp_percent * 3) + ((away_team_l10_games / 10) * 3)) / 12) - (2 * (away_team_ygssp_streak))
            else:
                #algo_away_team = ((away_ngssp_percent) / 2) + (2 * (away_team_l10_games - 7)) - (1 / 2 * (away_team_ygssp_streak))
                algo_away_team = (((away_ngssp_percent * 7) + ((away_team_l10_games / 10) * 5)) / 12) - (2 * (away_team_ygssp_streak))

        if home_team_ngssp_streak > 0:
            if not math.isnan(home_intra_ngssp_percent):
                #algo_home_team = ((home_ngssp_percent) / 2 + home_intra_ngssp_percent) / 2 + (2 * (home_team_l10_games - 7)) + (1 / 2 * (home_team_ngssp_streak))
                algo_home_team = (((home_ngssp_percent * 5) + (home_intra_ngssp_percent * 3) + ((home_team_l10_games / 10) * 3)) / 12) + (2 * (home_team_ngssp_streak))
            else:
                #algo_home_team = ((home_ngssp_percent) ) + (2 * (home_team_l10_games - 7)) + (1 / 2 * (home_team_ngssp_streak))
                algo_home_team = (((home_ngssp_percent * 7) + ((home_team_l10_games / 10) * 5)) / 12) + (2 * (home_team_ngssp_streak))
        elif home_team_ygssp_streak > 0:
            if not math.isnan(home_intra_ngssp_percent):
                #algo_home_team = ((home_ngssp_percent) / 2 + home_intra_ngssp_percent) / 2 + (2 * (home_team_l10_games - 7)) - (1 / 2 * (home_team_ygssp_streak))
                algo_home_team = (((home_ngssp_percent * 5) + (home_intra_ngssp_percent * 3) + ((home_team_l10_games / 10) * 3)) / 12) - (2 * (home_team_ygssp_streak))
            else:
                #algo_home_team = ((home_ngssp_percent) / 2) + (2 * (home_team_l10_games - 7)) - (1 / 2 * (home_team_ygssp_streak))
                algo_home_team = (((home_ngssp_percent * 7) + ((home_team_l10_games / 10) * 5)) / 12) - (2 * (home_team_ygssp_streak))



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
            'Away NGSP %': away_ngsp_percent,
            'Away NGSP % Color': away_ngsp_percent_color,
            'Away NGSSP %': away_ngssp_percent,
            'Away NGSSP % Color': away_ngssp_percent_color,
            'Away Total NGSP %': away_total_ngsp_percent,
            'Away Total NGSP % Color': away_total_ngsp_percent_color,
            'Away Total NGSSP %': away_total_ngssp_percent,
            'Away Total NGSSP % Color': away_total_ngssp_percent_color,
            'Away Intra NGSSP %': away_intra_ngssp_percent,
            'Away Intra NGSSP % Color': away_intra_ngssp_percent_color,

            'Away L10': away_team_l10_games,
            'Away Streak': away_streak,
            'Away Streak Color': away_streak_color,

            'Home Team': home_team,
            'Home GS': home_team_gs,
            'Home GS Color': home_gs_color,
            'Home NGSP %': home_ngsp_percent,
            'Home NGSP % Color': home_ngsp_percent_color,
            'Home NGSSP %': home_ngssp_percent,
            'Home NGSSP % Color': home_ngssp_percent_color,
            'Home Total NGSP %': home_total_ngsp_percent,
            'Home Total NGSP % Color': home_total_ngsp_percent_color,
            'Home Total NGSSP %': home_total_ngssp_percent,
            'Home Total NGSSP % Color': home_total_ngssp_percent_color,
            'Home Intra NGSSP %': home_intra_ngssp_percent,
            'Home Intra NGSSP % Color': home_intra_ngssp_percent_color,

            'Home L10': home_team_l10_games,
            'Home Streak': home_streak,
            'Home Streak Color': home_streak_color,

            # 'Away GAA': away_gaa,
            # 'Away GAA Color': away_gaa_color,
            'Away Goalie': away_goalie,
            # 'Away GA (Goalie)': away_ga,
            # 'Away GA (Goalie) Color': away_ga_goalie_color,
            'Away NGSP (Goalie)': away_ngsp,
            'Away NGSP (Goalie) Color': away_ngsp_goalie_color,
            'Away YGSP (Goalie)': away_ygsp,
            'Away YGSP (Goalie) Color': away_ygsp_goalie_color,
            'Away NGSP % (Goalie)': away_ngsp_goalie_percent,
            'Away NGSP % (Goalie) Color': away_ngsp_goalie_percent_color,
            'Away Total NGSP (Goalie)': away_total_ngsp,
            'Away Total YGSP (Goalie)': away_total_ygsp,
            'Away Total NGSP % (Goalie)': away_total_ngsp_goalie_percent,
            'Away Total NGSP % (Goalie) Color': away_total_ngsp_goalie_percent_color,
            'Away L5 (Goalie)': away_goalie_l5_games,
            'Away Streak (Goalie)': away_goalie_streak,
            'Away Streak (Goalie) Color': away_goalie_streak_color,

            # 'Home GAA': home_gaa,
            # 'Home GAA Color': home_gaa_color,
            'Home Goalie': home_goalie,
            # 'Home GA (Goalie)': home_ga,
            # 'Home GA (Goalie) Color': home_ga_goalie_color,
            'Home NGSP (Goalie)': home_ngsp,
            'Home NGSP (Goalie) Color': home_ngsp_goalie_color,
            'Home YGSP (Goalie)': home_ygsp,
            'Home YGSP (Goalie) Color': home_ygsp_goalie_color,
            'Home NGSP % (Goalie)': home_ngsp_goalie_percent,
            'Home NGSP % (Goalie) Color': home_ngsp_goalie_percent_color,
            'Home Total NGSP (Goalie)': home_total_ngsp,
            'Home Total YGSP (Goalie)': home_total_ygsp,
            'Home Total NGSP % (Goalie)': home_total_ngsp_goalie_percent,
            'Home Total NGSP % (Goalie) Color': home_total_ngsp_goalie_percent_color,
            'Home L5 (Goalie)': home_goalie_l5_games,
            'Home Streak (Goalie)': home_goalie_streak,
            'Home Streak (Goalie) Color': home_goalie_streak_color,

            'NGSP % (Goalies)': ngsp_pitchegs_percent,
            'NGSP % (Goalies) Color': ngsp_pitchegs_percent_color,

            'Away NGSSP Algo Percentage': away_algo_percentage,
            'Home NGSSP Algo Percentage': home_algo_percentage,
            'Algo Percentage': algo_percentage
        })

    # Get the current date
    current_date = datetime.date.today().strftime("%B %d, %Y")

    return render_template('nhl_sp_matchups_data_display.html', data=updated_data, date=current_date)

if __name__ == '__main__':
    app.run(debug=True)
