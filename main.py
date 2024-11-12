import requests
from datetime import datetime

# Set your RapidAPI host and key
API_HOST = 'api-nba-v1.p.rapidapi.com'
API_KEY = '2a13a376ccmsha04475c0610e2d7p1d2679jsn9fd2690835e7'

# Weighting factors
POINTS_WEIGHT = 1.5
ASSISTS_WEIGHT = 1.0
REBOUNDS_WEIGHT = 1.0

# Function to get the top players by team for a specific game
def get_top_players_by_team(game_id):
    url = f'https://{API_HOST}/players/statistics'
    querystring = {"game": game_id}
    headers = {
        'x-rapidapi-host': API_HOST,
        'x-rapidapi-key': API_KEY
    }
    
    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        data = response.json()

        # Organize players by team
        teams = {}
        for player_stat in data.get('response', []):
            # Extract player and team information
            player_info = player_stat.get('player', {})
            firstname = player_info.get('firstname', 'Unknown')
            lastname = player_info.get('lastname', 'Player')
            player_name = f"{firstname} {lastname}"
            
            team_info = player_stat.get('team', {})
            team_name = team_info.get('nickname', 'Unknown Team')
            
            # Extract statistics with default to 0 if missing
            points = player_stat.get('points') or 0
            assists = player_stat.get('assists') or 0
            rebounds = player_stat.get('totReb') or 0
            fg_percentage = player_stat.get('fgp', 0)
            three_points_made = player_stat.get('tpm', 0)
            three_points_attempted = player_stat.get('tpa', 0)
            
            # Convert fg_percentage to float if it's a string
            try:
                fg_percentage = float(fg_percentage)
            except (TypeError, ValueError):
                fg_percentage = 0

            # Calculate weighted performance score
            performance_score = (points * POINTS_WEIGHT) + (assists * ASSISTS_WEIGHT) + (rebounds * REBOUNDS_WEIGHT)
            
            # Add player to the corresponding team's list
            if team_name not in teams:
                teams[team_name] = []
            teams[team_name].append({
                'name': player_name,
                'points': points,
                'assists': assists,
                'rebounds': rebounds,
                'fg_percentage': fg_percentage,
                'three_points_made': three_points_made,
                'three_points_attempted': three_points_attempted,
                'performance_score': performance_score
            })

        # Extract and sort top 3 players per team
        top_teams = {}
        for team, players in teams.items():
            top_players = sorted(players, key=lambda x: x['performance_score'], reverse=True)[:3]
            top_teams[team] = top_players

        return top_teams

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")

# Function to get all games for today and retrieve top players for each game
def get_all_games_top_players(date):
    url = f'https://{API_HOST}/games'
    headers = {
        'x-rapidapi-host': API_HOST,
        'x-rapidapi-key': API_KEY
    }
    querystring = {"date": date}
    
    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        games = response.json().get('response', [])

        # Display current date and time
        current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"Date & Time: {current_datetime}\n")

        # Loop through each game and retrieve top players
        for game in games:
            game_id = game.get('id')
            home_team_info = game.get('teams', {}).get('home', {})
            away_team_info = game.get('teams', {}).get('visitors', {})

            # Properly extract both team names and scores
            home_team = home_team_info.get('nickname', 'Unknown Home Team')
            away_team = away_team_info.get('nickname', 'Unknown Away Team')
            home_score = game.get('scores', {}).get('home', {}).get('points', 'N/A')
            away_score = game.get('scores', {}).get('visitors', {}).get('points', 'N/A')

            # Print game details and current score
            print(f"Game: {home_team} vs {away_team}")
            print(f"Score: {home_team} {home_score} - {away_team} {away_score}")
            print("Top Players:")

            # Get top players for each team in the current game
            top_players = get_top_players_by_team(game_id)
            if top_players:
                for team, players in top_players.items():
                    print(f"\nTop 3 Players for {team}:")
                    for player in players:
                        fg_info = f", FG%: {player['fg_percentage']}%" if player['fg_percentage'] > 50 else ""
                        three_point_info = f", 3PT: {player['three_points_made']}/{player['three_points_attempted']}"
                        print(f"{player['name']}: Points: {player['points']}, Assists: {player['assists']}, "
                              f"Rebounds: {player['rebounds']}{fg_info}{three_point_info}")
            print("\n" + "-"*50)

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")

# Run the function for today's date
today_date = datetime.today().strftime('%Y-%m-%d')
get_all_games_top_players(today_date)
