import logging
from datetime import datetime, timedelta
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("nba-scores")

# Set up logging to stderr (important for stdio servers)
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Constants
BALLDONTLIE_API_BASE = "https://www.balldontlie.io/api/v1"


async def make_api_request(url: str) -> dict[str, Any] | None:
    """Make a request to the balldontlie API with proper error handling."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code} for {url}: {e.response.text[:200]}")
            return None
        except httpx.RequestError as e:
            logger.error(f"Request error for {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error for {url}: {e}")
            return None


def format_game(game: dict, include_stats: bool = False) -> str:
    """Format a game into a readable string."""
    home_team = game.get("home_team", {})
    visitor_team = game.get("visitor_team", {})
    
    home_score = game.get("home_team_score")
    visitor_score = game.get("visitor_team_score")
    
    status = game.get("status", "Unknown")
    date = game.get("date", "")
    
    # Format date if available
    date_str = ""
    if date:
        try:
            dt = datetime.fromisoformat(date.replace("Z", "+00:00"))
            date_str = dt.strftime("%B %d, %Y at %I:%M %p")
        except:
            date_str = date
    
    result = f"""
{visitor_team.get("full_name", "Away Team")} @ {home_team.get("full_name", "Home Team")}
Date: {date_str}
Status: {status}
"""
    
    if home_score is not None and visitor_score is not None:
        result += f"Score: {visitor_team.get("abbreviation", "AWY")} {visitor_score} - {home_score} {home_team.get("abbreviation", "HME")}\n"
        
        # Determine winner
        if home_score > visitor_score:
            result += f"Winner: {home_team.get("full_name", "Home Team")}\n"
        elif visitor_score > home_score:
            result += f"Winner: {visitor_team.get("full_name", "Away Team")}\n"
        else:
            result += "Result: Tie\n"
    
    if game.get("season"):
        result += f"Season: {game.get("season")}\n"
    
    if game.get("postseason"):
        result += "Playoff Game: Yes\n"
    
    return result.strip()


@mcp.tool()
async def get_today_games() -> str:
    """Get NBA games scheduled for today.
    
    Returns the list of NBA games happening today with scores if available.
    """
    today = datetime.now().date()
    url = f"{BALLDONTLIE_API_BASE}/games?dates[]={today}&per_page=100"
    
    data = await make_api_request(url)
    
    if not data:
        return "Error: Unable to fetch today's NBA games. The API may be temporarily unavailable."
    
    games = data.get("data", [])
    
    if not games:
        return f"No NBA games scheduled for today ({today.strftime('%B %d, %Y')})."
    
    formatted_games = [format_game(game) for game in games]
    return f"NBA Games for {today.strftime('%B %d, %Y')}:\n\n" + "\n---\n".join(formatted_games)


@mcp.tool()
async def get_games_by_date(date: str) -> str:
    """Get NBA games for a specific date.
    
    Args:
        date: Date in YYYY-MM-DD format (e.g., 2024-01-15)
    """
    try:
        # Validate date format
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return f"Error: Invalid date format '{date}'. Please use YYYY-MM-DD format (e.g., 2024-01-15)."
    
    url = f"{BALLDONTLIE_API_BASE}/games?dates[]={date}&per_page=100"
    
    data = await make_api_request(url)
    
    if not data:
        return f"Error: Unable to fetch NBA games for {date}. The API may be temporarily unavailable."
    
    games = data.get("data", [])
    
    if not games:
        return f"No NBA games scheduled for {date}."
    
    formatted_games = [format_game(game) for game in games]
    return f"NBA Games for {date}:\n\n" + "\n---\n".join(formatted_games)


@mcp.tool()
async def get_team_schedule(team_name: str, season: int = None) -> str:
    """Get the schedule for a specific NBA team.
    
    Args:
        team_name: Team name or abbreviation (e.g., "Lakers", "LAL", "Los Angeles Lakers")
        season: Optional season year (e.g., 2023 for 2023-24 season). Defaults to current season.
    """
    # First, get all teams to find the team ID
    teams_url = f"{BALLDONTLIE_API_BASE}/teams?per_page=100"
    teams_data = await make_api_request(teams_url)
    
    if not teams_data:
        return "Error: Unable to fetch team information. The API may be temporarily unavailable."
    
    # Find matching team
    team_name_lower = team_name.lower()
    matching_team = None
    
    for team in teams_data.get("data", []):
        full_name = team.get("full_name", "").lower()
        abbreviation = team.get("abbreviation", "").lower()
        city = team.get("city", "").lower()
        name = team.get("name", "").lower()
        
        if (team_name_lower in full_name or 
            team_name_lower == abbreviation or 
            team_name_lower in city or 
            team_name_lower in name):
            matching_team = team
            break
    
    if not matching_team:
        return f"Error: Team '{team_name}' not found. Please use a team name, city, or abbreviation (e.g., 'Lakers', 'LAL', 'Los Angeles Lakers')."
    
    team_id = matching_team.get("id")
    team_full_name = matching_team.get("full_name")
    
    # Build URL for games
    if season is None:
        # Default to current season (approximate)
        season = datetime.now().year
    
    url = f"{BALLDONTLIE_API_BASE}/games?team_ids[]={team_id}&seasons[]={season}&per_page=100"
    
    data = await make_api_request(url)
    
    if not data:
        return f"Error: Unable to fetch schedule for {team_full_name}. The API may be temporarily unavailable."
    
    games = data.get("data", [])
    
    if not games:
        return f"No games found for {team_full_name} in the {season} season."
    
    # Sort games by date
    games.sort(key=lambda x: x.get("date", ""))
    
    formatted_games = [format_game(game) for game in games[:20]]  # Limit to 20 most recent/upcoming
    remaining = len(games) - 20
    
    result = f"{team_full_name} Schedule ({season} season):\n\n" + "\n---\n".join(formatted_games)
    
    if remaining > 0:
        result += f"\n\n... and {remaining} more games."
    
    return result


@mcp.tool()
async def get_standings(season: int = None) -> str:
    """Get NBA standings for a season.
    
    Args:
        season: Optional season year (e.g., 2023 for 2023-24 season). Defaults to current season.
    """
    if season is None:
        season = datetime.now().year
    
    # Get all teams
    teams_url = f"{BALLDONTLIE_API_BASE}/teams?per_page=100"
    teams_data = await make_api_request(teams_url)
    
    if not teams_data:
        return "Error: Unable to fetch team information. The API may be temporarily unavailable."
    
    # Get games for the season to calculate standings
    games_url = f"{BALLDONTLIE_API_BASE}/games?seasons[]={season}&per_page=1000"
    games_data = await make_api_request(games_url)
    
    if not games_data:
        return f"Error: Unable to fetch games for {season} season. The API may be temporarily unavailable."
    
    # Calculate standings from games
    team_stats = {}
    
    for team in teams_data.get("data", []):
        team_id = team.get("id")
        team_stats[team_id] = {
            "name": team.get("full_name"),
            "conference": team.get("conference", "Unknown"),
            "division": team.get("division", "Unknown"),
            "wins": 0,
            "losses": 0,
        }
    
    # Process completed games
    for game in games_data.get("data", []):
        if game.get("status") != "Final":
            continue
        
        home_id = game.get("home_team", {}).get("id")
        visitor_id = game.get("visitor_team", {}).get("id")
        home_score = game.get("home_team_score")
        visitor_score = game.get("visitor_team_score")
        
        if home_id and visitor_id and home_score is not None and visitor_score is not None:
            if home_score > visitor_score:
                team_stats[home_id]["wins"] += 1
                team_stats[visitor_id]["losses"] += 1
            else:
                team_stats[visitor_id]["wins"] += 1
                team_stats[home_id]["losses"] += 1
    
    # Format standings by conference
    east_teams = []
    west_teams = []
    
    for team_id, stats in team_stats.items():
        wins = stats["wins"]
        losses = stats["losses"]
        total = wins + losses
        win_pct = (wins / total * 100) if total > 0 else 0
        
        team_info = {
            "name": stats["name"],
            "wins": wins,
            "losses": losses,
            "win_pct": win_pct,
        }
        
        if stats["conference"] == "East":
            east_teams.append(team_info)
        elif stats["conference"] == "West":
            west_teams.append(team_info)
    
    # Sort by wins
    east_teams.sort(key=lambda x: (x["wins"], x["win_pct"]), reverse=True)
    west_teams.sort(key=lambda x: (x["wins"], x["win_pct"]), reverse=True)
    
    result = f"NBA Standings - {season} Season\n\n"
    result += "EASTERN CONFERENCE\n"
    result += "-" * 50 + "\n"
    
    for i, team in enumerate(east_teams, 1):
        result += f"{i}. {team['name']}: {team['wins']}-{team['losses']} ({team['win_pct']:.1f}%)\n"
    
    result += "\nWESTERN CONFERENCE\n"
    result += "-" * 50 + "\n"
    
    for i, team in enumerate(west_teams, 1):
        result += f"{i}. {team['name']}: {team['wins']}-{team['losses']} ({team['win_pct']:.1f}%)\n"
    
    return result


def main():
    # Initialize and run the server
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
