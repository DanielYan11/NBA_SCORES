import requests
from datetime import datetime
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from io import BytesIO

# Set your RapidAPI host and key
API_HOST = 'api-nba-v1.p.rapidapi.com'
API_KEY = '2a13a376ccmsha04475c0610e2d7p1d2679jsn9fd2690835e7'

POINTS_WEIGHT = 1.5
ASSISTS_WEIGHT = 1.0
REBOUNDS_WEIGHT = 1.0

def get_top_players_by_team(game_id):
    url = f'https://{API_HOST}/players/statistics'
    headers = {
        'x-rapidapi-host': API_HOST,
        'x-rapidapi-key': API_KEY
    }
    querystring = {"game": str(game_id)}
    response = requests.get(url, headers=headers, params=querystring)
    stats = response.json().get('response', [])

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

    for team in teams:
        teams[team] = sorted(teams[team], key=lambda x: x['score'], reverse=True)[:3]
    
    return teams

def get_team_record(team_id):
    url = f'https://{API_HOST}/teams/statistics'
    headers = {
        'x-rapidapi-host': API_HOST,
        'x-rapidapi-key': API_KEY
    }
    querystring = {"id": str(team_id)}
    response = requests.get(url, headers=headers, params=querystring)
    stats = response.json().get('response', [])
    if stats:
        wins = stats[0].get('win', 0)
        losses = stats[0].get('loss', 0)
        return f"{wins} - {losses}"
    return "0 - 0"

def get_team_logo(team_code):
    url = f'https://{API_HOST}/teams'
    headers = {
        'x-rapidapi-host': API_HOST,
        'x-rapidapi-key': API_KEY
    }
    response = requests.get(url, headers=headers)
    teams = response.json().get('response', [])
    for team in teams:
        if team['code'] == team_code:
            return team['logo']
    return None

def display_games(date):
    url = f'https://{API_HOST}/games'
    headers = {
        'x-rapidapi-host': API_HOST,
        'x-rapidapi-key': API_KEY
    }
    querystring = {"date": date}
    response = requests.get(url, headers=headers, params=querystring)
    games = response.json().get('response', [])

    root = tk.Tk()
    root.title("NBA Games and Top Players")
    root.geometry("1000x800")

    main_frame = tk.Frame(root)
    main_frame.pack(fill="both", expand=True)

    canvas = tk.Canvas(main_frame)
    scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    row = 0

    for game in games:
        game_id = game.get('id')
        home_team_info = game.get('teams', {}).get('home', {})
        away_team_info = game.get('teams', {}).get('visitors', {})

        home_team_name = home_team_info.get('nickname', 'Home Team')
        away_team_name = away_team_info.get('nickname', 'Away Team')
        home_team_code = home_team_info.get('code')
        away_team_code = away_team_info.get('code')
        
        home_score = game.get('scores', {}).get('home', {}).get('points', 'N/A')
        away_score = game.get('scores', {}).get('visitors', {}).get('points', 'N/A')

        home_team_id = home_team_info.get('id')
        away_team_id = away_team_info.get('id')
        home_record = get_team_record(home_team_id)
        away_record = get_team_record(away_team_id)

        quarters_home = game.get('scores', {}).get('home', {}).get('linescore', [])
        quarters_away = game.get('scores', {}).get('visitors', {}).get('linescore', [])

        top_players = get_top_players_by_team(game_id)

        button_frame = tk.Frame(scrollable_frame, bg="lightgrey", relief="raised", borderwidth=2)
        button_frame.grid(row=row, column=0, padx=10, pady=10, sticky="nsew")

        # Download and resize team logos
        home_logo_url = get_team_logo(home_team_code)
        away_logo_url = get_team_logo(away_team_code)
        home_logo_img = away_logo_img = None
        if home_logo_url:
            home_logo_img = ImageTk.PhotoImage(Image.open(BytesIO(requests.get(home_logo_url).content)).resize((50, 50)))
        if away_logo_url:
            away_logo_img = ImageTk.PhotoImage(Image.open(BytesIO(requests.get(away_logo_url).content)).resize((50, 50)))

        if home_logo_img:
            home_logo_label = tk.Label(button_frame, image=home_logo_img, bg="lightgrey")
            home_logo_label.image = home_logo_img
            home_logo_label.grid(row=0, column=0, padx=10)

        if away_logo_img:
            away_logo_label = tk.Label(button_frame, image=away_logo_img, bg="lightgrey")
            away_logo_label.image = away_logo_img
            away_logo_label.grid(row=0, column=3, padx=10)

        logo_label_home = tk.Label(button_frame, text=home_team_name, font=("Arial", 12, "bold"), bg="lightgrey")
        logo_label_home.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        logo_label_away = tk.Label(button_frame, text=away_team_name, font=("Arial", 12, "bold"), bg="lightgrey")
        logo_label_away.grid(row=0, column=2, padx=10, pady=5, sticky="e")

        score_label = tk.Label(button_frame, text=f"{home_score} - {away_score}", font=("Arial", 14, "bold"), bg="lightgrey")
        score_label.grid(row=1, column=1, columnspan=2, pady=5)

        record_label_home = tk.Label(button_frame, text=f"({home_record})", bg="lightgrey")
        record_label_home.grid(row=2, column=1, padx=10, sticky="w")

        record_label_away = tk.Label(button_frame, text=f"({away_record})", bg="lightgrey")
        record_label_away.grid(row=2, column=2, padx=10, sticky="e")

        quarter_label = tk.Label(button_frame, text="Q1  Q2  Q3  Q4", bg="lightgrey")
        quarter_label.grid(row=3, column=1, columnspan=2)

        score_quarters = tk.Label(button_frame, text=f"{' '.join(quarters_home)}  -  {' '.join(quarters_away)}", bg="lightgrey")
        score_quarters.grid(row=4, column=1, columnspan=2)

        players_label_home = tk.Label(button_frame, text=f"{home_team_name} Top Players:", font=("Arial", 10, "italic"), bg="lightgrey")
        players_label_home.grid(row=5, column=0, columnspan=2, sticky="w", padx=10)

        players_label_away = tk.Label(button_frame, text=f"{away_team_name} Top Players:", font=("Arial", 10, "italic"), bg="lightgrey")
        players_label_away.grid(row=5, column=2, columnspan=2, sticky="e", padx=10)

        for i, player in enumerate(top_players.get(home_team_name, [])):
            home_player_label = tk.Label(button_frame, text=f"{player['name']}: pts {player['pts']}, ast {player['ast']}, reb {player['reb']}", bg="lightgrey")
            home_player_label.grid(row=6 + i, column=0, columnspan=2, sticky="w", padx=10)

        for i, player in enumerate(top_players.get(away_team_name, [])):
            away_player_label = tk.Label(button_frame, text=f"{player['name']}: pts {player['pts']}, ast {player['ast']}, reb {player['reb']}", bg="lightgrey")
            away_player_label.grid(row=6 + i, column=2, columnspan=2, sticky="e", padx=10)

        row += 1

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    root.mainloop()

today_date = datetime.today().strftime('%Y-%m-%d')
display_games(today_date)
