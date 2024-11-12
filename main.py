import requests
from datetime import datetime
import tkinter as tk
from tkinter import ttk

# Set your RapidAPI host and key
API_HOST = 'api-nba-v1.p.rapidapi.com'
API_KEY = '2a13a376ccmsha04475c0610e2d7p1d2679jsn9fd2690835e7'

# Weighting factors
POINTS_WEIGHT = 1.5
ASSISTS_WEIGHT = 1.0
REBOUNDS_WEIGHT = 1.0

def get_top_players_by_team(game_id):
    """Returns top 3 players for each team by score (weighted by points, assists, and rebounds)."""
    url = f'https://{API_HOST}/players/statistics'
    headers = {
        'x-rapidapi-host': API_HOST,
        'x-rapidapi-key': API_KEY
    }
    querystring = {"game": str(game_id)}
    response = requests.get(url, headers=headers, params=querystring)
    stats = response.json().get('response', [])

    # Organize player stats by team
    teams = {}
    for stat in stats:
        team_name = stat['team']['nickname']
        player_name = f"{stat['player']['firstname']} {stat['player']['lastname']}"
        points = stat.get('points', 0) or 0
        assists = stat.get('assists', 0) or 0
        rebounds = stat.get('totReb', 0) or 0
        score = points * POINTS_WEIGHT + assists * ASSISTS_WEIGHT + rebounds * REBOUNDS_WEIGHT
        player_info = {
            'name': player_name,
            'pts': points,
            'ast': assists,
            'reb': rebounds,
            'score': score
        }
        
        if team_name not in teams:
            teams[team_name] = []
        teams[team_name].append(player_info)

    # Sort players in each team by score and pick top 3
    for team in teams:
        teams[team] = sorted(teams[team], key=lambda x: x['score'], reverse=True)[:3]
    
    return teams

def display_games(date):
    url = f'https://{API_HOST}/games'
    headers = {
        'x-rapidapi-host': API_HOST,
        'x-rapidapi-key': API_KEY
    }
    querystring = {"date": date}
    response = requests.get(url, headers=headers, params=querystring)
    games = response.json().get('response', [])

    # Set up the main window with a scrollable frame
    root = tk.Tk()
    root.title("NBA Games and Top Players")
    root.geometry("1000x600")  # Increased width to accommodate more columns

    main_frame = tk.Frame(root)
    main_frame.pack(fill="both", expand=True)

    # Create a canvas and scrollbar for the scrollable frame
    canvas = tk.Canvas(main_frame)
    scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Display each game in a button with a click animation in a grid layout
    col_count = 4  # Set number of columns to 4
    row = 0
    col = 0

    for game in games:
        game_id = game.get('id')
        home_team_info = game.get('teams', {}).get('home', {})
        away_team_info = game.get('teams', {}).get('visitors', {})

        home_team = home_team_info.get('nickname', 'Home Team')
        away_team = away_team_info.get('nickname', 'Away Team')
        home_score = game.get('scores', {}).get('home', {}).get('points', 'N/A')
        away_score = game.get('scores', {}).get('visitors', {}).get('points', 'N/A')

        # Get the top 3 players for each team
        top_players = get_top_players_by_team(game_id)
        
        # Prepare button text with top players, using shortened stat names
        button_text = f"Game: {home_team} vs {away_team}\nScore: {home_team} {home_score} - {away_team} {away_score}\n\n"
        button_text += f"Top 3 Players for {home_team}:\n"
        for player in top_players.get(home_team, []):
            button_text += f"{player['name']}: pts {player['pts']}, ast {player['ast']}, reb {player['reb']}\n"
        button_text += f"\nTop 3 Players for {away_team}:\n"
        for player in top_players.get(away_team, []):
            button_text += f"{player['name']}: pts {player['pts']}, ast {player['ast']}, reb {player['reb']}\n"

        # Create a button for each game block
        game_button = tk.Button(
            scrollable_frame,
            text=button_text,
            font=("Arial", 10),
            bg="lightgrey",
            fg="black",
            padx=10,
            pady=10,
            anchor="w",
            justify="left",
            relief="raised",
            highlightthickness=2,
            wraplength=200  # Wrap text to fit within the button width
        )

        # Add button animation effect
        game_button.bind("<ButtonPress>", lambda e: e.widget.config(relief="sunken"))
        game_button.bind("<ButtonRelease>", lambda e: e.widget.config(relief="raised"))

        # Position the button in a grid layout
        game_button.grid(row=row, column=col, padx=10, pady=5, sticky="nsew")

        # Update row and column to fill in grid row by row
        col += 1
        if col >= col_count:
            col = 0
            row += 1

    root.mainloop()

# Run the function for today's date
today_date = datetime.today().strftime('%Y-%m-%d')
display_games(today_date)
