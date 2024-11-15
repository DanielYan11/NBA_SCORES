import discord
from discord.ext import commands
from discord.ui import Button, View
import requests
from datetime import datetime, timedelta
import time

API_KEY = 'dQpW0RfLEAD8xkHHzZ5AbnyEV0Eumio6okfAJi1H'

# Weighting factors for performance score calculation
POINTS_WEIGHT = 1.5
ASSISTS_WEIGHT = 1.0
REBOUNDS_WEIGHT = 1.0

# Team emojis
TEAM_EMOJIS = {
    "Hawks": "<:AtlantaHawks:1306073940594004024>",
    "Celtics": "<:BostonCeltics:1306073943794516002>",
    "Nets": "<:BrooklynNets:1306073945606324275>",
    "Hornets": "<:CharlotteHornets:1306073946977865801>",
    "Bulls": "<:ChicagoBulls:1306073948655456338>",
    "Cavaliers": "<:ClevelandCavaliers:1306073950014672987>",
    "Mavericks": "<:DallasMavericks:1306073951180685485>",
    "Nuggets": "<:DenverNuggets:1306073952459948104>",
    "Pistons": "<:DetroitPistons:1306074734861090816>",
    "Warriors": "<:GoldenStateWarriors:1306073955534245969>",
    "Rockets": "<:HoustonRockets:1306074736035364935>",
    "Pacers": "<:Pacers:1306100738077884456>",
    "Clippers": "<:LAClippers:1306074737113432135>",
    "Lakers": "<:LosAngelesLakers:1306074738300424234>",
    "Grizzlies": "<:MemphisGrizzlies:1306074786610548746>",
    "Heat": "<:MiamiHeat:1306100226045509673>",
    "Bucks": "<:Bucks:1306100660525207702>",
    "Timberwolves": "<:MinnesotaTimberwolves:1306074791874265160>",
    "Pelicans": "<:NewOrleansPelicans:1306074793292071002>",
    "Knicks": "<:NewYorkKnicks:1306074794516807700>",
    "Thunder": "<:OKC:1306100516794925077>",
    "Magic": "<:OrlandoMagic:1306100394723643432>",
    "76ers": "<:76ers:1306100120311300128>",
    "Suns": "<:PhoenixSuns:1306074852070785054>",
    "Trail Blazers": "<:PortlandTrailBlazers:1306074853396447264>",
    "Kings": "<:SacramentoKings:1306074855044546661>",
    "Spurs": "<:SanAntonioSpurs:1306074856290517092>",
    "Raptors": "<:TorontoRaptors:1306074857871511603>",
    "Jazz": "<:UtahJazz:1306074858580607017>",
    "Wizards": "<:WashingtonWizards:1306099972919398451>"
}

# Stat emojis
POINTS_EMOJI = "🏀"
ASSISTS_EMOJI = "🅰️"
REBOUNDS_EMOJI = "🔄"

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

def get_yesterdays_date():
    return (datetime.now() - timedelta(days=1)).strftime('%Y/%m/%d')

def fetch_games_for_yesterday():
    date = get_yesterdays_date()
    url = f"https://api.sportradar.com/nba/trial/v8/en/games/{date}/schedule.json?api_key={API_KEY}"
    headers = {"accept": "application/json"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        schedule = response.json()
        return schedule.get("games", [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching games: {e}")
        return []

def fetch_summary(game_id, retries=3):
    url = f"https://api.sportradar.com/nba/trial/v8/en/games/{game_id}/summary.json?api_key={API_KEY}"
    headers = {"accept": "application/json"}

    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                time.sleep(10)  # Wait to avoid rate limit
        except Exception as e:
            print(f"An error occurred: {e}")
            break
    return None

def get_team_emoji(team_name):
    return TEAM_EMOJIS.get(team_name, team_name)

def display_top_players(players):
    scored_players = []
    for player in players:
        stats = player.get("statistics", {})
        points = stats.get("points", 0)
        assists = stats.get("assists", 0)
        rebounds = stats.get("rebounds", 0)
        performance_score = (points * POINTS_WEIGHT) + (assists * ASSISTS_WEIGHT) + (rebounds * REBOUNDS_WEIGHT)

        player_info = {
            'name': player['full_name'],
            'points': points,
            'assists': assists,
            'rebounds': rebounds,
            'performance_score': performance_score
        }

        scored_players.append(player_info)

    top_players = sorted(scored_players, key=lambda x: x['performance_score'], reverse=True)[:3]
    
    result = f"{'Player':<20} {POINTS_EMOJI} Points | {ASSISTS_EMOJI} Assists | {REBOUNDS_EMOJI} Rebounds\n"
    result += "-" * 50 + "\n"
    for player in top_players:
        result += (
            f"{player['name']:<20} "
            f"{player['points']:>6}      | {player['assists']:>6}       | {player['rebounds']:>7}\n"
        )
    return result

class GameDetailsView(View):
    def __init__(self, summary):
        super().__init__(timeout=180)
        self.summary = summary

    @discord.ui.button(label="More Details", style=discord.ButtonStyle.primary)
    async def more_details(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message(embed=create_detailed_embed(self.summary), ephemeral=True)

def display_game_info(summary):
    if not summary:
        return None

    home_team = summary['home']['name']
    away_team = summary['away']['name']
    home_score = summary['home']['points']
    away_score = summary['away']['points']

    home_team_emoji = get_team_emoji(home_team)
    away_team_emoji = get_team_emoji(away_team)

    embed = discord.Embed(
        title=f"{home_team_emoji} {home_team} vs {away_team_emoji} {away_team}",
        description=f"**Final Score:** {home_team} {home_score} - {away_team} {away_score}"
    )

    embed.add_field(
        name="Quarter Scores",
        value=(f"{home_team_emoji} {home_team}: " +
               " | ".join(str(quarter["points"]) for quarter in summary['home']['scoring']) +
               f"\n{away_team_emoji} {away_team}: " +
               " | ".join(str(quarter["points"]) for quarter in summary['away']['scoring'])),
        inline=False
    )
    
    embed.add_field(
        name=f"Top 3 Performers for {home_team_emoji} {home_team}",
        value=display_top_players(summary['home'].get('players', [])),
        inline=False
    )
    embed.add_field(
        name=f"Top 3 Performers for {away_team_emoji} {away_team}",
        value=display_top_players(summary['away'].get('players', [])),
        inline=False
    )

    return embed, GameDetailsView(summary)  # Return a new view instance for each game

def create_detailed_embed(summary):
    embed = discord.Embed(
        title="Detailed Game Stats",
        description="Additional detailed statistics for each team"
    )

    # Home team details
    home_team = summary['home']['name']
    home_team_emoji = get_team_emoji(home_team)
    home_stats = summary['home'].get('statistics', {})
    
    embed.add_field(
        name=f"{home_team_emoji} {home_team} - Detailed Stats",
        value=(
            f"Field Goals: {home_stats.get('field_goals_made', 0)}/{home_stats.get('field_goals_att', 0)}\n"
            f"3-Pointers: {home_stats.get('three_points_made', 0)}/{home_stats.get('three_points_att', 0)}\n"
            f"Free Throws: {home_stats.get('free_throws_made', 0)}/{home_stats.get('free_throws_att', 0)}\n"
            f"Points in Paint: {home_stats.get('points_in_paint_made', 0)}/{home_stats.get('points_in_paint_att', 0)}\n"
            f"Rebounds: {home_stats.get('offensive_rebounds', 0)} Off, {home_stats.get('defensive_rebounds', 0)} Def, {home_stats.get('total_rebounds', 0)} Total\n"
            f"Assists: {home_stats.get('assists', 0)} | Steals: {home_stats.get('steals', 0)} | Blocks: {home_stats.get('blocks', 0)}"
        ),
        inline=False
    )

    # Away team details
    away_team = summary['away']['name']
    away_team_emoji = get_team_emoji(away_team)
    away_stats = summary['away'].get('statistics', {})
    
    embed.add_field(
        name=f"{away_team_emoji} {away_team} - Detailed Stats",
        value=(
            f"Field Goals: {away_stats.get('field_goals_made', 0)}/{away_stats.get('field_goals_att', 0)}\n"
            f"3-Pointers: {away_stats.get('three_points_made', 0)}/{away_stats.get('three_points_att', 0)}\n"
            f"Free Throws: {away_stats.get('free_throws_made', 0)}/{away_stats.get('free_throws_att', 0)}\n"
            f"Points in Paint: {away_stats.get('points_in_paint_made', 0)}/{away_stats.get('points_in_paint_att', 0)}\n"
            f"Rebounds: {away_stats.get('offensive_rebounds', 0)} Off, {away_stats.get('defensive_rebounds', 0)} Def, {away_stats.get('total_rebounds', 0)} Total\n"
            f"Assists: {away_stats.get('assists', 0)} | Steals: {away_stats.get('steals', 0)} | Blocks: {away_stats.get('blocks', 0)}"
        ),
        inline=False
    )

    return embed

@bot.command(name="nba")
async def nba(ctx):
    await ctx.send("Fetching NBA game data for yesterday...")
    games = fetch_games_for_yesterday()

    if not games:
        await ctx.send("No games found for yesterday.")
        return

    for game in games:
        game_id = game['id']
        summary = fetch_summary(game_id)
        if summary:
            embed, view = display_game_info(summary)
            if embed:
                await ctx.send(embed=embed, view=view)  # Send each game with its unique view
            else:
                await ctx.send("Failed to display game info.")
        else:
            await ctx.send("Failed to fetch game summary.")
        time.sleep(1)  # To avoid rate limiting

@bot.event
async def on_ready():
    print(f"Bot is ready. Logged in as {bot.user}")

# Run the bot
bot.run("YOUR_BOT_TOKEN")
